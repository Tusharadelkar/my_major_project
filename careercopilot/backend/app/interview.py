import os
import io
import json
import logging
from groq import Groq
from sqlalchemy.orm import Session
from . import models

logger = logging.getLogger(__name__)

def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    """
    Transcribes audio bytes to text using Groq's Whisper API.
    Falls back to a mock transcription if GROQ_API_KEY is not set.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY is not set or using placeholder. Returning mock transcription.")
        return "This is a mock transcription of the spoken response. The candidate explained the concept clearly using standard Python features."

    try:
        client = Groq(api_key=groq_api_key)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename  # Required for format detection in Groq
        
        logger.info(f"Calling Groq Whisper API for transcription of {filename}...")
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            response_format="json"
        )
        logger.info("Transcription successful.")
        return transcription.text
    except Exception as e:
        logger.error(f"Error during audio transcription: {str(e)}")
        return "This is a fallback transcription due to a transcription error. The answer discussed database indexing and caching strategies."

def evaluate_answer(question: str, answer: str) -> dict:
    """
    Evaluates the candidate's answer using Llama 3 via Groq.
    Returns:
        {
            "technical_score": int (1-5),
            "confidence_score": int (1-5),
            "feedback": str
        }
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY is not set or using placeholder. Returning mock evaluation.")
        return get_mock_evaluation(question)

    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {str(e)}")
        return get_mock_evaluation(question)

    system_prompt = (
        "You are an expert technical interviewer. Evaluate the candidate's answer to this interview question.\n\n"
        "Question: [Question]\n"
        "Answer: [Answer]\n\n"
        "Provide a constructive, professional evaluation of their answer. Your response MUST be a single, valid JSON object with the following keys:\n"
        "{\n"
        "  \"technical_score\": <integer from 1 to 5, where 1 is poor/incorrect and 5 is excellent/fully correct>,\n"
        "  \"confidence_score\": <integer from 1 to 5, where 1 is hesitant/unsure and 5 is fluent/very confident>,\n"
        "  \"feedback\": \"detailed feedback on what they did well and how they could improve\"\n"
        "}"
    )

    user_content = (
        f"Question: {question}\n"
        f"Answer: {answer}\n"
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Calling Groq LLM to evaluate answer - Attempt {attempt + 1}")
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content.strip()
            data = json.loads(response_text)
            
            # Type and value safety checks
            tech_score = int(data.get("technical_score", 3))
            conf_score = int(data.get("confidence_score", 3))
            
            return {
                "technical_score": min(5, max(1, tech_score)),
                "confidence_score": min(5, max(1, conf_score)),
                "feedback": data.get("feedback", "Good effort. Try to elaborate on structural details next time.")
            }
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed during answer evaluation LLM call: {str(e)}")
            if attempt == max_retries - 1:
                return get_mock_evaluation(question)

def get_mock_evaluation(question: str) -> dict:
    """Helper to return a default mock evaluation."""
    return {
        "technical_score": 4,
        "confidence_score": 4,
        "feedback": "Mock Feedback: The candidate demonstrated a solid conceptual understanding of the topic. They could improve by detailing practical edge cases and performance considerations in their architecture."
    }

def decide_followup(
    session_id: int,
    question_text: str,
    original_skill: str,
    answer: str,
    technical_score: int,
    db: Session
) -> str | None:
    """
    Decides whether to ask a follow-up question based on the candidate's answer technical score.
    If yes, generates the follow-up, saves it to database, and returns the follow-up text.
    """
    # Rule 1: We only ask follow-ups if the technical score is low (<= 2)
    if technical_score > 2:
        return None

    # Rule 2: Do not ask a follow-up if this question is ALREADY a follow-up
    if "(Follow-up)" in original_skill:
        return None

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        # Mock follow-up
        followup_text = f"You mentioned that in your response. Could you explain how you would manage state synchronization under high loads?"
    else:
        try:
            client = Groq(api_key=groq_api_key)
            prompt = (
                f"You are a technical interviewer. The candidate gave a weak answer to the question: '{question_text}'\n"
                f"Their answer: '{answer}'\n\n"
                f"Generate a single brief, constructive follow-up question to probe their understanding further. "
                f"Return ONLY the question text itself. Do not say 'Here is a follow up' or add quotes."
            )
            logger.info("Calling Groq LLM to generate follow-up question...")
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            followup_text = completion.choices[0].message.content.strip()
            logger.info("Follow-up question generated.")
        except Exception as e:
            logger.error(f"Failed to generate follow-up question: {str(e)}")
            followup_text = "Could you elaborate on the specific details and trade-offs of that approach?"

    # Store the follow-up question in the qa_records table
    try:
        new_record = models.QARecord(
            session_id=session_id,
            question=followup_text,
            skill_tag=f"{original_skill} (Follow-up)"
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        logger.info(f"Stored follow-up question row (id: {new_record.id}) in database.")
        return followup_text
    except Exception as e:
        logger.error(f"Failed to save follow-up to database: {str(e)}")
        db.rollback()
        return None
