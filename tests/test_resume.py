import os
import sys
import unittest

# Ensure the backend directory is in python PATH
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, "careercopilot"))
sys.path.append(os.path.join(parent_dir, "careercopilot", "backend"))

# Set DATABASE_URL to sqlite for self-contained testing
os.environ["DATABASE_URL"] = "sqlite:///./test_temp.db"
os.environ["GROQ_API_KEY"] = "your_groq_api_key_here"  # Use placeholder to trigger fallback parser

import fitz  # PyMuPDF
from fastapi.testclient import TestClient
from careercopilot.backend.app.main import app
from careercopilot.backend.app.database import engine, Base
from careercopilot.backend.app.parser import extract_text_from_pdf
from careercopilot.backend.app.scoring import compute_ats_score, analyze_skill_gaps


class TestResumeParserAndScorer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create tables in test database
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        
    @classmethod
    def tearDownClass(cls):
        # Drop tables and remove temp database file
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_temp.db"):
            try:
                os.remove("./test_temp.db")
            except OSError:
                pass

    def test_01_pdf_generation_and_extraction(self):
        """Test PDF generation and text extraction using PyMuPDF."""
        # Create a mock PDF
        doc = fitz.open()
        page = doc.new_page()
        text_content = "John Doe Resume\nSkills: Python, SQL, Docker, FastAPI\nExperience: Software Engineer at Google"
        page.insert_textbox(fitz.Rect(50, 50, 500, 500), text_content)
        pdf_bytes = doc.write()
        doc.close()
        
        # Verify text extraction
        extracted_text = extract_text_from_pdf(pdf_bytes)
        self.assertIn("John Doe Resume", extracted_text)
        self.assertIn("Python", extracted_text)
        self.assertIn("FastAPI", extracted_text)

    def test_02_scoring_logic(self):
        """Test the semantic scoring and skill matching functions."""
        resume = "Experienced developer working with Python, SQL, and Docker."
        job_desc = "Looking for a software engineer skilled in Python, Docker, and Kubernetes."
        
        # Test ATS Cosine Similarity Score
        score = compute_ats_score(resume, job_desc)
        self.assertTrue(0 <= score <= 100)
        
        # Test Skill Match
        resume_skills = ["Python", "SQL", "Docker"]
        job_skills = ["Python", "Docker", "Kubernetes"]
        matched, missing = analyze_skill_gaps(resume_skills, job_skills, resume)
        
        self.assertIn("Python", matched)
        self.assertIn("Docker", matched)
        self.assertIn("Kubernetes", missing)

    def test_03_upload_endpoint(self):
        """Test the POST /api/resume/upload endpoint with a mock PDF."""
        # Create a mock PDF
        doc = fitz.open()
        page = doc.new_page()
        text_content = "Jane Doe Resume\nSkills: Python, SQL, Git, FastAPI\nEducation: B.S. in Computer Science"
        page.insert_textbox(fitz.Rect(50, 50, 500, 500), text_content)
        pdf_bytes = doc.write()
        doc.close()
        
        # Prepare POST request files & data
        files = {
            "resume": ("resume.pdf", pdf_bytes, "application/pdf")
        }
        data = {
            "job_description": "We need a developer with Python, FastAPI, SQL, and AWS."
        }
        
        # Call the endpoint
        response = self.client.post("/api/resume/upload", files=files, data=data)
        
        # Assert response details
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        
        self.assertIn("session_id", res_json)
        self.assertIn("ats_score", res_json)
        self.assertIn("matched_skills", res_json)
        self.assertIn("missing_skills", res_json)
        self.assertIn("parsed_resume", res_json)
        self.assertIn("personalized_questions", res_json)
        
        # Save session_id for next test
        self.__class__.session_id = res_json["session_id"]
        
        # Check parsed resume subfields
        parsed_resume = res_json["parsed_resume"]
        self.assertIn("skills", parsed_resume)
        self.assertIn("experience", parsed_resume)
        self.assertIn("projects", parsed_resume)
        self.assertIn("education", parsed_resume)
        
        # Score validation
        self.assertTrue(0 <= res_json["ats_score"] <= 100)
        
        # Verify non-empty personalized questions in response
        self.assertTrue(len(res_json["personalized_questions"]) > 0)

    def test_04_questions_endpoint(self):
        """Test GET /api/session/{id}/questions returns non-empty personalized questions with audio."""
        session_id = getattr(self.__class__, "session_id", None)
        self.assertIsNotNone(session_id, "Session ID was not saved from previous test.")
        
        # Call GET /api/session/{id}/questions
        response = self.client.get(f"/api/session/{session_id}/questions")
        
        self.assertEqual(response.status_code, 200)
        questions_list = response.json()
        
        self.assertTrue(isinstance(questions_list, list))
        self.assertTrue(len(questions_list) > 0)
        
        # Save question IDs for next tests
        self.__class__.question_ids = [q["id"] for q in questions_list]
        self.__class__.question_skills = {q["id"]: q["skill_tag"] for q in questions_list}
        
        # Verify that at least one question (the active/first unanswered one) has base64 audio returned
        has_audio = False
        for q in questions_list:
            self.assertIn("id", q)
            self.assertIn("question", q)
            self.assertIn("skill_tag", q)
            self.assertIn("audio_base64", q)
            if len(q["audio_base64"]) > 0:
                has_audio = True
        self.assertTrue(has_audio)

    def test_05_answer_text_endpoint(self):
        """Test POST /api/interview/{session_id}/answer-text evaluates answers and returns status."""
        session_id = getattr(self.__class__, "session_id", None)
        q_ids = getattr(self.__class__, "question_ids", None)
        self.assertIsNotNone(session_id)
        self.assertTrue(len(q_ids) > 0)
        
        target_q_id = q_ids[0]
        
        data = {
            "question_id": target_q_id,
            "answer_text": "I am highly experienced in Python and writing backend APIs using FastAPI and SQLAlchemy."
        }
        
        # Call text answer submit
        response = self.client.post(f"/api/interview/{session_id}/answer-text", data=data)
        
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        
        self.assertIn("evaluation", res_json)
        self.assertIn("status", res_json)
        self.assertIn("next_question", res_json)
        
        eval_details = res_json["evaluation"]
        self.assertIn("technical_score", eval_details)
        self.assertIn("confidence_score", eval_details)
        self.assertIn("feedback", eval_details)
        self.assertIn("transcript", eval_details)
        self.assertEqual(eval_details["transcript"], data["answer_text"])

    def test_06_answer_audio_endpoint(self):
        """Test POST /api/interview/{session_id}/answer-audio evaluates voice responses."""
        session_id = getattr(self.__class__, "session_id", None)
        q_ids = getattr(self.__class__, "question_ids", None)
        self.assertIsNotNone(session_id)
        self.assertTrue(len(q_ids) > 1)
        
        # Use second question
        target_q_id = q_ids[1]
        
        # Generate dummy wav audio bytes (header + silence)
        dummy_wav_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        
        files = {
            "audio": ("answer.wav", dummy_wav_bytes, "audio/wav")
        }
        data = {
            "question_id": target_q_id
        }
        
        # Call audio answer submit
        response = self.client.post(f"/api/interview/{session_id}/answer-audio", files=files, data=data)
        
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        
        self.assertIn("evaluation", res_json)
        self.assertIn("status", res_json)
        self.assertIn("next_question", res_json)
        
        eval_details = res_json["evaluation"]
        self.assertIn("technical_score", eval_details)
        self.assertIn("confidence_score", eval_details)
        self.assertIn("feedback", eval_details)
        self.assertIn("transcript", eval_details)
        
        # Verify transcription output is returned
        self.assertTrue(len(eval_details["transcript"]) > 0)
        
        # Verify local audio file was created
        audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "careercopilot", "backend", "audio_uploads")
        saved_files = os.listdir(audio_dir) if os.path.exists(audio_dir) else []
        self.assertTrue(len(saved_files) > 0)
        
        # Clean up audio_uploads files generated in test
        if os.path.exists(audio_dir):
            for f in os.listdir(audio_dir):
                try:
                    os.remove(os.path.join(audio_dir, f))
                except OSError:
                    pass
            try:
                os.rmdir(audio_dir)
            except OSError:
                pass

    def test_07_avatar_signaling_endpoints(self):
        """Test D-ID WebRTC signaling endpoints for stream creation, SDP/ICE submission, and speaking."""
        # 1. Create Stream Session
        response = self.client.post("/api/avatar/stream/create")
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        
        self.assertIn("id", res_json)
        self.assertIn("session_id", res_json)
        self.assertIn("offer", res_json)
        self.assertIn("ice_servers", res_json)
        self.assertIn("mock", res_json)
        
        # Verify the offer has sdp and type keys
        offer = res_json["offer"]
        self.assertIn("type", offer)
        self.assertIn("sdp", offer)
        
        stream_id = res_json["id"]
        session_id = res_json["session_id"]
        
        # 2. Submit SDP Answer
        sdp_payload = {
            "session_id": session_id,
            "sdp": {
                "type": "answer",
                "sdp": "v=0\r\no=- 421312 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n"
            }
        }
        sdp_response = self.client.post(f"/api/avatar/stream/{stream_id}/sdp", json=sdp_payload)
        self.assertEqual(sdp_response.status_code, 200)
        self.assertEqual(sdp_response.json(), {"status": "ok"})
        
        # 3. Submit ICE Candidate
        ice_payload = {
            "session_id": session_id,
            "candidate": {
                "candidate": "candidate:842163049 1 udp 16777215 127.0.0.1 9 typ srflx raddr 127.0.0.1 rport 9",
                "sdpMid": "0",
                "sdpMLineIndex": 0
            }
        }
        ice_response = self.client.post(f"/api/avatar/stream/{stream_id}/ice", json=ice_payload)
        self.assertEqual(ice_response.status_code, 200)
        self.assertEqual(ice_response.json(), {"status": "ok"})
        
        # 4. Trigger Speaking Stream
        speak_payload = {
            "session_id": session_id,
            "text": "Hello and welcome to your AI technical mock interview session. Let us get started."
        }
        speak_response = self.client.post(f"/api/avatar/stream/{stream_id}/speak", json=speak_payload)
        self.assertEqual(speak_response.status_code, 200)
        self.assertEqual(speak_response.json(), {"status": "ok"})

if __name__ == "__main__":
    unittest.main()


