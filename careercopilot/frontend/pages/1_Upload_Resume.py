import os
import sys
import streamlit as st
import requests

# Add root folder of frontend to PATH so we can import state.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import state

# Page configuration
st.set_page_config(
    page_title="Upload Resume | CareerCopilot AI",
    page_icon="📄",
    layout="wide"
)

# Initialize Session State
state.init_state()

# Fetch backend url from environment
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Inject Custom CSS for Premium Design
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    .stApp, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
    }

    .page-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(to right, #a855f7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .page-description {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }

    .card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .score-container {
        text-align: center;
        background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
        border: 1px solid #4c1d95;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }

    .score-val {
        font-size: 4rem;
        font-weight: 800;
        color: #c084fc;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 15px rgba(192, 132, 252, 0.4);
    }

    .score-label {
        font-size: 1.1rem;
        color: #cbd5e1;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .skill-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }

    .skill-matched {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .skill-missing {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 1rem;
        border-left: 4px solid #818cf8;
        padding-left: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="page-title">Resume Parsing & ATS Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="page-description">Upload your resume (PDF/DOCX) and specify the target job description to run automated ATS scoring and skill gap mapping.</div>', unsafe_allow_html=True)

# Main container grid
col_input, col_results = st.columns([1, 1])

# Check for results in session state to persist views across interaction runs
if "ats_results" not in st.session_state:
    st.session_state.ats_results = None

with col_input:
    st.markdown('<div class="section-title">Upload & Setup</div>', unsafe_allow_html=True)
    
    with st.container():
        # Resume file uploader
        resume_file = st.file_uploader(
            "Upload Resume (PDF or DOCX)",
            type=["pdf", "docx"],
            help="Supported file types: PDF and DOCX"
        )
        
        # Job Description text area
        job_description = st.text_area(
            "Target Job Description",
            height=250,
            placeholder="Paste the full job description or requirements list here..."
        )
        
        # Submit Button
        submit_btn = st.button("Run ATS Evaluation ⚡", use_container_width=True)

    if submit_btn:
        if not resume_file:
            st.error("Please upload a resume file.")
        elif not job_description.strip():
            st.error("Please paste a job description.")
        else:
            with st.spinner("Processing resume, calling AI LLM, and calculating scores..."):
                try:
                    # Prepare file payload
                    file_payload = {
                        "resume": (resume_file.name, resume_file.getvalue(), resume_file.type)
                    }
                    data_payload = {
                        "job_description": job_description
                    }
                    
                    # Fetch student info from state if any
                    student = state.get_student_info()
                    if student["id"]:
                        data_payload["student_id"] = student["id"]

                    # Call backend API
                    response = requests.post(
                        f"{BACKEND_URL}/api/resume/upload",
                        files=file_payload,
                        data=data_payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        st.session_state.ats_results = res_data
                        
                        # Store session ID in state
                        state.set_session_id(res_data.get("session_id"))
                        st.success("ATS Evaluation completed successfully!")
                        
                    else:
                        error_detail = response.json().get("detail", "Unknown server error.")
                        st.error(f"Backend API Error: {error_detail}")
                        
                except Exception as e:
                    st.error(f"Failed to connect to backend server: {str(e)}")

# Display Results Section
with col_results:
    st.markdown('<div class="section-title">Evaluation Results</div>', unsafe_allow_html=True)
    
    results = st.session_state.ats_results
    
    if results:
        ats_score = results.get("ats_score", 0)
        matched_skills = results.get("matched_skills", [])
        missing_skills = results.get("missing_skills", [])
        parsed_resume = results.get("parsed_resume", {})
        session_id = results.get("session_id")
        
        # 1. ATS Score card
        st.markdown(
            f"""
            <div class="score-container">
                <div class="score-val">{ats_score}%</div>
                <div class="score-label">ATS Match Score</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.write("")
        
        # Visual progress bar
        # Determine color of progress bar based on score
        if ats_score >= 80:
            st.success(f"Great match! Your resume matches {ats_score}% of the job description.")
        elif ats_score >= 50:
            st.warning(f"Moderate match ({ats_score}%). Consider adding missing skills below to optimize.")
        else:
            st.error(f"Low match ({ats_score}%). High modifications needed.")
            
        st.progress(ats_score / 100.0)
        st.write("")
        
        # 2. Skills columns
        st.markdown("##### Skill Gap Analysis")
        col_match, col_miss = st.columns(2)
        
        with col_match:
            st.write(f"**Matched Skills ({len(matched_skills)})**")
            if matched_skills:
                for skill in matched_skills:
                    st.markdown(f'<span class="skill-badge skill-matched">{skill}</span>', unsafe_allow_html=True)
            else:
                st.write("No direct matching skills found.")
                
        with col_miss:
            st.write(f"**Missing Skills ({len(missing_skills)})**")
            if missing_skills:
                for skill in missing_skills:
                    st.markdown(f'<span class="skill-badge skill-missing">{skill}</span>', unsafe_allow_html=True)
            else:
                st.write("No missing skills! You match all requirements.")
        
        st.write("")
        st.markdown("---")
        
        # 3. Parsed resume details
        with st.expander("🔍 View AI Parsed Resume Details"):
            st.markdown("**Extracted Resume Skills:**")
            skills_list = parsed_resume.get("skills", [])
            if skills_list:
                st.write(", ".join(skills_list))
            else:
                st.write("*None found*")
                
            st.write("")
            st.markdown("**Experience & Projects:**")
            
            st.markdown("*Work Experience:*")
            exp_list = parsed_resume.get("experience", [])
            for exp in exp_list:
                st.write(f"- {exp}")
            if not exp_list:
                st.write("*None found*")
                
            st.write("")
            st.markdown("*Projects:*")
            proj_list = parsed_resume.get("projects", [])
            for proj in proj_list:
                st.write(f"- {proj}")
            if not proj_list:
                st.write("*None found*")
                
            st.write("")
            st.markdown("**Education:**")
            edu_list = parsed_resume.get("education", [])
            for edu in edu_list:
                st.write(f"- {edu}")
            if not edu_list:
                st.write("*None found*")
                
    else:
        # State when no evaluation is run
        st.info("Upload a resume and paste a job description on the left, then click 'Run ATS Evaluation' to see your match details here.")
