import os
import streamlit as st
import requests
from state import init_state, get_student_info, get_session_id, set_student_info

# Page configuration
st.set_page_config(
    page_title="CareerCopilot AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
init_state()

# Fetch backend url from environment
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Check backend health
backend_online = False
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=3)
    if response.status_code == 200 and response.json().get("status") == "ok":
        backend_online = True
except Exception:
    backend_online = False

# Inject Custom CSS for Premium Look & Feel
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    /* Main Container Font Override */
    .stApp, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Gradient Header Card */
    .header-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        border: 1px solid #312e81;
        border-radius: 16px;
        padding: 3rem 2rem;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .header-title {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(to right, #c084fc, #818cf8, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.75rem;
        letter-spacing: -0.03em;
    }

    .header-subtitle {
        font-size: 1.25rem;
        color: #94a3b8;
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* Feature Cards Grid */
    .feature-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        border-color: #818cf8;
        background: rgba(30, 41, 59, 0.8);
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.15);
    }

    .feature-icon {
        font-size: 2.2rem;
        margin-bottom: 0.75rem;
        display: inline-block;
    }

    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }

    .feature-desc {
        font-size: 0.95rem;
        color: #94a3b8;
        line-height: 1.5;
    }

    /* Status Pill */
    .api-status-container {
        display: flex;
        justify-content: center;
        margin-top: 1rem;
    }

    .api-status {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        background: #1e293b;
        border: 1px solid #334155;
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        font-size: 0.9rem;
        color: #e2e8f0;
    }

    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }

    .status-online {
        background-color: #10b981;
        box-shadow: 0 0 10px #10b981;
    }

    .status-offline {
        background-color: #ef4444;
        box-shadow: 0 0 10px #ef4444;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header Section
st.markdown(
    """
    <div class="header-card">
        <div class="header-title">CareerCopilot AI</div>
        <div class="header-subtitle">
            Accelerate your career preparation with real-time ATS job matching, custom behavioral & technical mock interviews, and automated skill-gap analysis.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Core Feature highlights
st.markdown("### Core Features")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">ATS Job Matching</div>
            <div class="feature-desc">
                Upload your resume alongside target job descriptions to analyze keyword matching, score your suitability, and identify improvements instantly.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <div class="feature-title">AI Mock Interviews</div>
            <div class="feature-desc">
                Engage in interactive technical and behavioral question rounds. Get scoring and comprehensive qualitative feedback on each answer.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Skill-Gap Analysis</div>
            <div class="feature-desc">
                Uncover missing requirements for your dream jobs and receive automated action items to bridge the gap and stay competitive.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br><br>", unsafe_allow_html=True)

# Main action area
st.markdown("### Get Started")

student = get_student_info()
if not student["id"]:
    col_action, col_spacer = st.columns([2, 3])
    with col_action:
        st.markdown('<div class="feature-card" style="padding: 1.5rem; border-color: #312e81; background: rgba(30, 41, 59, 0.75);">', unsafe_allow_html=True)
        st.markdown("<h5 style='margin-top:0; color:#c084fc;'>🚀 Initialize CareerCopilot Session</h5>", unsafe_allow_html=True)
        name_input = st.text_input("Full Name", placeholder="John Doe")
        email_input = st.text_input("Email Address", placeholder="john@example.com")
        
        btn_clicked = st.button("Start CareerCopilot Session 🚀", use_container_width=True)
        if btn_clicked:
            if not name_input.strip() or not email_input.strip():
                st.error("Please enter both your name and email.")
            else:
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/student",
                        json={"name": name_input.strip(), "email": email_input.strip()},
                        timeout=5
                    )
                    if response.status_code == 200:
                        res_data = response.json()
                        set_student_info(res_data["id"], res_data["name"], res_data["email"])
                        st.success(f"Welcome {res_data['name']}! Session initialized. Use the sidebar menu to upload your resume.")
                        st.rerun()
                    else:
                        st.error("Failed to initialize session on backend.")
                except Exception as e:
                    # Fallback to local session state if backend endpoint fails
                    set_student_info(999, name_input.strip(), email_input.strip())
                    st.success(f"Welcome {name_input.strip()}! Session initialized locally.")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.success(f"✓ Session Active for **{student['name']}** ({student['email']}). Navigate to **Upload Resume** in the sidebar to begin!")


# Sidebar Status & Debugging Info
with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/bot.png", width=70)
    st.markdown("## Configuration & State")
    
    # State debug display
    student = get_student_info()
    session_id = get_session_id()
    
    st.write("**Current Session State:**")
    st.json({
        "session_id": session_id,
        "student_id": student["id"],
        "student_name": student["name"],
        "student_email": student["email"]
    })
    
    st.markdown("---")
    
    # Backend health indicator
    status_class = "status-online" if backend_online else "status-offline"
    status_label = "Online" if backend_online else "Offline"
    st.markdown(
        f"""
        <div class="api-status">
            <span class="status-dot {status_class}"></span>
            Backend API: <strong>{status_label}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )
