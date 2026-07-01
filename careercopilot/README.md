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
├── frontend-react/           # React + Vite Web Application (Javascript)
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js     # Axios API client pointing to FastAPI backend
│   │   ├── components/       # Custom React components (Navbar, AudioRecorder, etc.)
│   │   ├── App.jsx           # Main React component
│   │   └── index.css         # Modern styling & typography system
│   ├── Dockerfile
│   ├── package.json          # Node package requirements & scripts
│   └── vite.config.js        # Vite build configuration (exposed on port 5173)
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

# D-ID Avatar Configuration (Optional)
DID_API_KEY=your_did_api_key_here
```

---

## 🚀 Running the Project

### Option A: Local Execution (Without Docker)

#### 1. Start the Backend API Server
Ensure you have Python 3.11+ installed.

```bash
cd careercopilot/backend

# Install dependencies
pip install -r requirements.txt

# Start the server (port 8000)
# Note: On first startup, the server automatically seeds the ChromaDB vector database with baseline questions.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Start the React Frontend App
Ensure you have Node.js 18+ installed.

```bash
cd careercopilot/frontend-react

# Install dependencies
npm install

# Start Vite development server (runs on http://localhost:5173)
npm run dev
```

#### 3. Access the Application
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

### Option B: Docker Compose Execution
If Docker Desktop is installed and running on your machine:

1. **Boot all services**:
   Run the following command at the root of the project (`careercopilot/`):
   ```bash
   docker compose up --build
   ```

2. **Access services**:
   - React Frontend Application: [http://localhost:5173](http://localhost:5173)
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
