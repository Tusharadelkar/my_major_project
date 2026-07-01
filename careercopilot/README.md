# CareerCopilot AI 🤖

CareerCopilot AI is an advanced, AI-driven career preparation platform designed to help students accelerate their job readiness. By uploading a resume and targeting a job description, the platform calculates ATS match scores, highlights skill gaps, seeds mock interviews with relevant questions, personalizes those questions using resume context, and allows students to complete voice-based interviews with speech-to-text transcription and text-to-speech feedback.

---

## 📂 Repository Structure

```text
careercopilot/
├── backend/                  # FastAPI Application (Python 3.11+)
│   ├── app/
│   │   ├── database.py       # SQLAlchemy engine and session local configuration
│   │   ├── generator.py      # LLM question personalization via Groq Llama 3
│   │   ├── interview.py      # Whisper audio transcription and answer grading logic
│   │   ├── main.py           # FastAPI path operations and endpoints
│   │   ├── models.py         # SQLAlchemy models (students, sessions, qa_records, skill_gaps)
│   │   ├── parser.py         # Document parsing logic (PDF / DOCX)
│   │   ├── scoring.py        # SentenceTransformers ATS similarity score engine
│   │   ├── tts.py            # TTS generation (ElevenLabs & gTTS fallback)
│   │   └── vector_store.py   # ChromaDB indexing, seeding, and search
│   ├── Dockerfile
│   └── requirements.txt      # Backend Python package requirements
│
├── frontend/                 # Streamlit Web Application (Python)
│   ├── pages/
│   │   ├── 1_Upload_Resume.py # Upload portal, ATS scorecard, and skill gaps page
│   │   └── 2_Mock_Interview.py# Audio interview console with speech recordings & scorecard
│   ├── app.py                # Main home landing page
│   ├── state.py              # Shared Streamlit session state wrapper
│   ├── Dockerfile
│   └── requirements.txt      # Frontend Python package requirements
│
├── docker-compose.yml        # Multi-container service orchestration
├── .env.example              # Template configuration for environment settings
└── .env                      # Local active environment configuration
```

---

## ⚙️ Environment Configuration

The application requires configuration via environment variables. Copy `.env.example` to `.env` and set the following parameters:

```bash
# Database Settings (For Docker Postgres or local instance)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_password_change_me
POSTGRES_DB=careercopilot_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres:postgres_password_change_me@db:5432/careercopilot_db

# LLM Configuration (Required for Groq Whisper and Llama 3)
GROQ_API_KEY=your_groq_api_key_here

# Speech Synthesis (Optional, falls back to Google TTS if not provided)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Communication endpoint
BACKEND_URL=http://backend:8000
```

---

## 🚀 Running the Project

### Option A: Local Execution (Without Docker)
This is the recommended method if Docker is not installed on your system.

1. **Prerequisites**:
   Ensure you have Python 3.11+ installed.

2. **Configure `.env`**:
   To run completely offline without setting up a local PostgreSQL, you can use SQLite:
   ```env
   DATABASE_URL=sqlite:///./local_temp.db
   BACKEND_URL=http://localhost:8000
   GROQ_API_KEY=your_actual_groq_api_key
   ```

3. **Start the Backend API Server**:
   ```bash
   cd careercopilot/backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   *Note: On first startup, the server automatically seeds the ChromaDB vector database with 110 baseline questions.*

4. **Start the Frontend Streamlit App**:
   ```bash
   cd careercopilot/frontend
   pip install -r requirements.txt
   streamlit run app.py --server.port 8501
   ```

5. **Access the Application**:
   Open [http://localhost:8501](http://localhost:8501) in your browser.

---

### Option B: Docker Compose Execution
If Docker Desktop is installed and running on your machine:

1. **Boot all services**:
   Run the following command at the root of the project (`careercopilot/`):
   ```bash
   docker compose up --build
   ```

2. **Access services**:
   - Streamlit Application: [http://localhost:8501](http://localhost:8501)
   - FastAPI Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Running Automated Tests

A comprehensive unit test suite is available. Tests cover PDF parsing, embedding calculations, ChromaDB searches, text evaluations, audio transcriptions, and API routers.

To execute tests locally:
```bash
# Run from the workspace root (one level above careercopilot/)
python tests/test_resume.py
```
