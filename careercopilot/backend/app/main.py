from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import base64
import os
import logging

# Load .env file automatically so API keys (GROQ, ElevenLabs, D-ID) are available
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    load_dotenv(dotenv_path=os.path.abspath(_env_path), override=True)
except ImportError:
    pass  # python-dotenv not installed — rely on shell env vars
from .database import engine, get_db
from . import models, parser, scoring, avatar
from .vector_store import seed_vector_db, retrieve_questions
from .generator import generate_personalized_questions
from .tts import generate_speech
from .interview import transcribe_audio, evaluate_answer, decide_followup

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all tables are created in the database on startup
    models.Base.metadata.create_all(bind=engine)
    # Seed ChromaDB vector store with questions on startup
    seed_vector_db()
    yield

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CareerCopilot AI API",
    description="Backend services for CareerCopilot AI",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for browser-side WebRTC fetches
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/student")
async def create_or_get_student(payload: dict, db: Session = Depends(get_db)):
    name = payload.get("name")
    email = payload.get("email")
    if not name or not email:
        raise HTTPException(status_code=400, detail="Name and email are required.")
    
    student = db.query(models.Student).filter(models.Student.email == email).first()
    if not student:
        student = models.Student(name=name, email=email)
        db.add(student)
        db.commit()
        db.refresh(student)
    else:
        if student.name != name:
            student.name = name
            db.commit()
            db.refresh(student)
            
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email
    }


@app.post("/api/resume/upload")
async def upload_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    student_id: int = Form(None),
    db: Session = Depends(get_db)
):
    # 1. Validate file extension
    filename = resume.filename or ""
    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    # 2. Read file bytes
    try:
        file_bytes = await resume.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read upload file: {str(e)}")

    # 3. Extract raw text from the resume
    try:
        if filename.endswith(".pdf"):
            resume_text = parser.extract_text_from_pdf(file_bytes)
        else:
            resume_text = parser.extract_text_from_docx(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="The uploaded resume file contains no readable text.")

    # 4. Ensure we have a student to satisfy the foreign key constraint
    student = None
    if student_id:
        student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        # Fallback to the first student in DB
        student = db.query(models.Student).first()
    if not student:
        # Create a default student if DB is empty
        student = models.Student(name="Default Student", email="default@careercopilot.ai")
        db.add(student)
        db.commit()
        db.refresh(student)

    # 5. Extract structured resume information using Llama 3 via Groq
    parsed_data = parser.parse_resume_with_llm(resume_text, job_description)

    # 6. Compute ATS Score (cosine similarity of embeddings mapped to 0-100)
    ats_score = scoring.compute_ats_score(resume_text, job_description)

    # 7. Analyze skill gaps
    matched_skills, missing_skills = scoring.analyze_skill_gaps(
        parsed_data.get("skills", []),
        parsed_data.get("job_description_skills", []),
        resume_text
    )

    # 8. Create a new session row in the database
    db_session = models.Session(
        student_id=student.id,
        job_description=job_description,
        ats_score=ats_score
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    # 9. Store each skill gap as a row in skill_gaps table
    for skill in matched_skills:
        gap = models.SkillGap(session_id=db_session.id, skill_name=skill, status="matched")
        db.add(gap)
    for skill in missing_skills:
        gap = models.SkillGap(session_id=db_session.id, skill_name=skill, status="missing")
        db.add(gap)
    db.commit()

    # 10. Query ChromaDB and generate personalized questions
    retrieved_qs = retrieve_questions(matched_skills, missing_skills, limit=12)
    personalized_qs = generate_personalized_questions(retrieved_qs, parsed_data)

    # 11. Store the finalized personalized question set in the qa_records table
    # Generating TTS audio on upload blocks the request, so we store empty and generate lazily/on-demand.
    for q in personalized_qs:
        record = models.QARecord(
            session_id=db_session.id,
            question=q["question"],
            skill_tag=q["skill"],
            audio_base64=""
        )
        db.add(record)
    db.commit()

    # 12. Return response
    return {
        "session_id": db_session.id,
        "ats_score": ats_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "parsed_resume": {
            "skills": parsed_data.get("skills", []),
            "projects": parsed_data.get("projects", []),
            "experience": parsed_data.get("experience", []),
            "education": parsed_data.get("education", [])
        },
        "personalized_questions": personalized_qs
    }

@app.get("/api/session/{id}/questions")
async def get_session_questions(id: int, db: Session = Depends(get_db)):
    """Return the personalized question list generated for the session.
    TTS audio is pre-generated at question creation time, not on every request.
    """
    session = db.query(models.Session).filter(models.Session.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    records = db.query(models.QARecord).filter(models.QARecord.session_id == id).all()
    
    # Find the first unanswered record
    first_unanswered = None
    for r in records:
        if r.answer_transcript is None:
            first_unanswered = r
            break
            
    response_list = []
    for r in records:
        # Use cached audio if available; only regenerate if missing
        audio_b64 = r.audio_base64 or ""
        # Only generate TTS dynamically if this is the active (first unanswered) question
        if r == first_unanswered and not audio_b64:
            try:
                audio_bytes = generate_speech(r.question)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                # Cache it back so we don't regenerate next time
                r.audio_base64 = audio_b64
                db.commit()
            except Exception as e:
                logger.error(f"Failed to generate TTS for question {r.id}: {str(e)}")
                audio_b64 = ""
            
        response_list.append({
            "id": r.id,
            "question": r.question,
            "skill_tag": r.skill_tag,
            "audio_base64": audio_b64,
            "answer_transcript": r.answer_transcript,
            "technical_score": r.technical_score,
            "confidence_score": r.confidence_score,
            "feedback": r.feedback
        })
    return response_list

@app.post("/api/interview/{session_id}/answer-audio")
async def submit_answer_audio(
    session_id: int,
    question_id: int = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Verify question and session exist
    qa_record = db.query(models.QARecord).filter(
        models.QARecord.id == question_id,
        models.QARecord.session_id == session_id
    ).first()
    if not qa_record:
        raise HTTPException(status_code=404, detail="Question record not found for this session.")

    # 2. Read audio bytes
    try:
        audio_bytes = await audio.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read audio file: {str(e)}")

    # 3. Transcribe audio using Whisper
    filename = audio.filename or "answer.wav"
    transcript = transcribe_audio(audio_bytes, filename)

    # 4. Save audio file locally
    audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audio_uploads")
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, f"session_{session_id}_qa_{question_id}_{filename}")
    try:
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
    except Exception as e:
        logger.error(f"Failed to save audio file locally: {str(e)}")

    # 5. Evaluate the transcribed answer
    eval_result = evaluate_answer(qa_record.question, transcript)

    # 6. Update qa_record
    qa_record.answer_transcript = transcript
    qa_record.technical_score = eval_result["technical_score"]
    qa_record.confidence_score = eval_result["confidence_score"]
    qa_record.feedback = eval_result["feedback"]
    qa_record.audio_path = audio_path
    db.commit()

    # 7. Decide follow-up logic
    followup_q = decide_followup(
        session_id=session_id,
        question_text=qa_record.question,
        original_skill=qa_record.skill_tag,
        answer=transcript,
        technical_score=eval_result["technical_score"],
        db=db
    )

    # 8. Check for next question
    next_question_payload = None
    if followup_q:
        # A new follow-up was generated and stored in db. Fetch it.
        new_q = db.query(models.QARecord).filter(
            models.QARecord.session_id == session_id,
            models.QARecord.question == followup_q
        ).first()
        if new_q:
            try:
                audio_bytes = generate_speech(new_q.question)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                new_q.audio_base64 = audio_b64
                db.commit()
            except Exception:
                audio_b64 = ""
            next_question_payload = {
                "id": new_q.id,
                "question": new_q.question,
                "skill_tag": new_q.skill_tag,
                "audio_base64": audio_b64
            }
    
    if not next_question_payload:
        # Get the next unanswered question (where answer_transcript is still None)
        next_q = db.query(models.QARecord).filter(
            models.QARecord.session_id == session_id,
            models.QARecord.answer_transcript == None
        ).order_by(models.QARecord.id.asc()).first()
        
        if next_q:
            try:
                audio_bytes = generate_speech(next_q.question)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                next_q.audio_base64 = audio_b64
                db.commit()
            except Exception:
                audio_b64 = ""
            next_question_payload = {
                "id": next_q.id,
                "question": next_q.question,
                "skill_tag": next_q.skill_tag,
                "audio_base64": audio_b64
            }

    status = "ongoing" if next_question_payload else "completed"

    return {
        "evaluation": {
            "technical_score": eval_result["technical_score"],
            "confidence_score": eval_result["confidence_score"],
            "feedback": eval_result["feedback"],
            "transcript": transcript
        },
        "status": status,
        "next_question": next_question_payload
    }

@app.post("/api/interview/{session_id}/answer-text")
async def submit_answer_text(
    session_id: int,
    question_id: int = Form(...),
    answer_text: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Verify question and session exist
    qa_record = db.query(models.QARecord).filter(
        models.QARecord.id == question_id,
        models.QARecord.session_id == session_id
    ).first()
    if not qa_record:
        raise HTTPException(status_code=404, detail="Question record not found for this session.")

    # 2. Evaluate the answer text
    eval_result = evaluate_answer(qa_record.question, answer_text)

    # 3. Update qa_record
    qa_record.answer_transcript = answer_text
    qa_record.technical_score = eval_result["technical_score"]
    qa_record.confidence_score = eval_result["confidence_score"]
    qa_record.feedback = eval_result["feedback"]
    db.commit()

    # 4. Decide follow-up logic
    followup_q = decide_followup(
        session_id=session_id,
        question_text=qa_record.question,
        original_skill=qa_record.skill_tag,
        answer=answer_text,
        technical_score=eval_result["technical_score"],
        db=db
    )

    # 5. Check for next question
    next_question_payload = None
    if followup_q:
        new_q = db.query(models.QARecord).filter(
            models.QARecord.session_id == session_id,
            models.QARecord.question == followup_q
        ).first()
        if new_q:
            try:
                audio_bytes = generate_speech(new_q.question)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                new_q.audio_base64 = audio_b64
                db.commit()
            except Exception:
                audio_b64 = ""
            next_question_payload = {
                "id": new_q.id,
                "question": new_q.question,
                "skill_tag": new_q.skill_tag,
                "audio_base64": audio_b64
            }
    
    if not next_question_payload:
        next_q = db.query(models.QARecord).filter(
            models.QARecord.session_id == session_id,
            models.QARecord.answer_transcript == None
        ).order_by(models.QARecord.id.asc()).first()
        
        if next_q:
            try:
                audio_bytes = generate_speech(next_q.question)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                next_q.audio_base64 = audio_b64
                db.commit()
            except Exception:
                audio_b64 = ""
            next_question_payload = {
                "id": next_q.id,
                "question": next_q.question,
                "skill_tag": next_q.skill_tag,
                "audio_base64": audio_b64
            }

    status = "ongoing" if next_question_payload else "completed"

    return {
        "evaluation": {
            "technical_score": eval_result["technical_score"],
            "confidence_score": eval_result["confidence_score"],
            "feedback": eval_result["feedback"],
            "transcript": answer_text
        },
        "status": status,
        "next_question": next_question_payload
    }

@app.post("/api/avatar/stream/create")
async def api_create_stream():
    """Signaling endpoint: Create a new D-ID WebRTC talk stream session."""
    return avatar.create_talk_stream()

@app.post("/api/avatar/stream/{stream_id}/sdp")
async def api_submit_sdp(stream_id: str, payload: dict):
    """Signaling endpoint: Submit WebRTC SDP answer to D-ID."""
    session_id = payload.get("session_id")
    sdp = payload.get("sdp")
    success = avatar.submit_sdp_answer(stream_id, session_id, sdp)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to submit SDP answer to D-ID.")
    return {"status": "ok"}

@app.post("/api/avatar/stream/{stream_id}/ice")
async def api_submit_ice(stream_id: str, payload: dict):
    """Signaling endpoint: Submit local ICE candidates to D-ID."""
    session_id = payload.get("session_id")
    candidate = payload.get("candidate")
    success = avatar.submit_ice_candidate(stream_id, session_id, candidate)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to submit ICE candidate to D-ID.")
    return {"status": "ok"}

@app.post("/api/avatar/stream/{stream_id}/speak")
async def api_trigger_speak(stream_id: str, payload: dict):
    """Trigger speech for the WebRTC stream session."""
    session_id = payload.get("session_id")
    text = payload.get("text")
    success = avatar.trigger_stream_speech(stream_id, session_id, text)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to trigger avatar speech stream.")
    return {"status": "ok"}



