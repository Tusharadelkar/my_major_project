import os
import sys
import base64
import streamlit as st
import requests
import streamlit.components.v1 as components

# Add root folder of frontend to PATH so we can import state.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import state

# Page configuration
st.set_page_config(
    page_title="AI Mock Interview | CareerCopilot AI",
    page_icon="💬",
    layout="wide"
)

# Initialize Session State
state.init_state()

# Fetch backend url from environment
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
# Browser-accessible backend URL (default to localhost if inside docker container network)
BROWSER_BACKEND_URL = "http://localhost:8000" if "backend:" in BACKEND_URL else BACKEND_URL

# Inject Custom CSS for Premium Look
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

    .question-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }

    .question-tag {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background-color: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        margin-bottom: 1rem;
    }

    .question-text {
        font-size: 1.5rem;
        font-weight: 600;
        color: #f1f5f9;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .completion-card {
        background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
        border: 1px solid #047857;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(4, 120, 87, 0.1);
        margin-bottom: 2rem;
    }

    .eval-result-card {
        background: linear-gradient(135deg, #0f2a1a 0%, #0a1628 100%);
        border: 1px solid #1a4731;
        border-radius: 14px;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 24px rgba(0,0,0,0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="page-title">AI Mock Interview Console</div>', unsafe_allow_html=True)

# Fetch session ID from session state
session_id = state.get_session_id()

if not session_id:
    st.info("No active interview session detected. Please upload a resume first or enter your Session ID below to begin.")
    manual_session = st.text_input("Enter Session ID:")
    if manual_session:
        try:
            s_id = int(manual_session)
            state.set_session_id(s_id)
            st.success(f"Loaded Session #{s_id}!")
            st.rerun()
        except ValueError:
            st.error("Please enter a valid numeric session ID.")
else:
    # Sidebar control
    with st.sidebar:
        st.markdown("### Interview Status")
        st.write(f"**Session ID:** `{session_id}`")
        if st.button("Reset Interview Session", use_container_width=True):
            state.clear_state()
            if "ats_results" in st.session_state:
                del st.session_state.ats_results
            for k in ["last_eval", "showing_eval"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    # Load session questions
    try:
        response = requests.get(f"{BACKEND_URL}/api/session/{session_id}/questions", timeout=30)
        if response.status_code == 200:
            questions = response.json()
        else:
            st.error("Failed to load interview questions from backend.")
            questions = []
    except Exception as e:
        st.error(f"Error fetching questions: {str(e)}")
        questions = []

    if questions:
        unanswered = [q for q in questions if not q.get("answer_transcript")]
        total_qs = len(questions)
        answered_count = total_qs - len(unanswered)

        # ── Show evaluation result after an answer was submitted ──
        if st.session_state.get("showing_eval") and st.session_state.get("last_eval"):
            eval_data = st.session_state["last_eval"]

            st.markdown(f"##### ✅ Answer Submitted — Question {answered_count} of {total_qs}")

            tech_score = eval_data.get("technical_score", 0)
            conf_score = eval_data.get("confidence_score", 0)
            feedback   = eval_data.get("feedback", "")
            transcript = eval_data.get("transcript", "")

            st.markdown(
                f"""
                <div class="eval-result-card">
                    <div style="font-size:1.1rem; font-weight:600; color:#a7f3d0; margin-bottom:1rem;">📊 Evaluation Result</div>
                    <div style="display:flex; gap:2rem; margin-bottom:1.2rem;">
                        <div>
                            <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.05em;">Technical Score</div>
                            <div style="font-size:2rem; font-weight:700; color:#818cf8;">{"⭐" * tech_score} {tech_score}/5</div>
                        </div>
                        <div>
                            <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.05em;">Confidence Score</div>
                            <div style="font-size:2rem; font-weight:700; color:#34d399;">{"⭐" * conf_score} {conf_score}/5</div>
                        </div>
                    </div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:0.5rem; text-transform:uppercase; letter-spacing:0.04em;">Interviewer Feedback</div>
                    <div style="font-size:1rem; color:#e2e8f0; line-height:1.6;">{feedback}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if transcript:
                with st.expander("📝 Your Answer Transcript"):
                    st.write(transcript)

            if unanswered:
                btn_label = f"Next Question ({answered_count + 1}/{total_qs}) →"
            else:
                btn_label = "View Final Scorecard 🏆"

            if st.button(btn_label, type="primary", use_container_width=True):
                del st.session_state["last_eval"]
                del st.session_state["showing_eval"]
                st.rerun()

        elif unanswered:
            # ── Show current unanswered question ──
            current_q = unanswered[0]

            st.markdown(f"##### Question {answered_count + 1} of {total_qs}")

            col_avatar, col_q = st.columns([1, 2])

            with col_avatar:
                avatar_html = f"""
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                     font-family: 'Outfit', sans-serif; background: #0f172a; border: 1px solid #334155;
                     border-radius: 16px; padding: 1.5rem; height: 400px; box-shadow: 0 10px 20px rgba(0,0,0,0.3);">

                    <div id="video-container" style="position: relative; width: 220px; height: 220px;
                         border-radius: 50%; overflow: hidden; border: 4px solid #6366f1; background: #1e293b;
                         display: flex; align-items: center; justify-content: center;">
                        <video id="avatar-video" width="220" height="220" autoplay
                               style="object-fit: cover; display: none;"></video>

                        <div id="avatar-placeholder" style="display: flex; flex-direction: column;
                             align-items: center; justify-content: center;">
                            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#818cf8"
                                 stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"
                                 style="animation: pulse 2s infinite;">
                                <style>
                                    @keyframes pulse {{
                                        0%   {{ transform: scale(1);   opacity: 0.7; }}
                                        50%  {{ transform: scale(1.1); opacity: 1;   }}
                                        100% {{ transform: scale(1);   opacity: 0.7; }}
                                    }}
                                </style>
                                <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
                                <rect x="9" y="9" width="6" height="6"></rect>
                                <line x1="9"  y1="1"  x2="9"  y2="4"></line>
                                <line x1="15" y1="1"  x2="15" y2="4"></line>
                                <line x1="9"  y1="20" x2="9"  y2="23"></line>
                                <line x1="15" y1="20" x2="15" y2="23"></line>
                                <line x1="20" y1="9"  x2="23" y2="9"></line>
                                <line x1="20" y1="15" x2="23" y2="15"></line>
                                <line x1="1"  y1="9"  x2="4"  y2="9"></line>
                                <line x1="1"  y1="15" x2="4"  y2="15"></line>
                            </svg>
                            <span id="avatar-status-label"
                                  style="font-size: 0.85rem; color: #94a3b8; margin-top: 10px; font-weight: 500;">
                                AI Avatar Offline
                            </span>
                        </div>
                    </div>

                    <button id="webrtc-connect-btn"
                        style="margin-top: 1.25rem; font-weight: 600; font-family: 'Outfit', sans-serif;
                               font-size: 0.9rem; padding: 0.6rem 1.2rem; border-radius: 8px; border: none;
                               background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); color: white;
                               cursor: pointer; box-shadow: 0 4px 15px rgba(99,102,241,0.4);">
                        Connect AI Interviewer
                    </button>

                    <div id="demo-info"
                         style="display:none; margin-top:0.75rem; font-size:0.78rem;
                                background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.35);
                                border-radius:8px; padding:0.5rem 0.9rem; color:#fbbf24; text-align:center;">
                        🎭 <strong>Demo Mode</strong> — animated AI avatar.<br>
                        Add <code>DID_API_KEY</code> to .env for live video.
                    </div>
                </div>

                <script>
                    const connectBtn    = document.getElementById('webrtc-connect-btn');
                    const avatarLabel   = document.getElementById('avatar-status-label');
                    const videoEl       = document.getElementById('avatar-video');
                    const placeholderEl = document.getElementById('avatar-placeholder');
                    const demoInfo      = document.getElementById('demo-info');

                    let peerConnection, streamId, sessionId, isMock = false;
                    const backendUrl = "{BROWSER_BACKEND_URL}";

                    connectBtn.onclick = async () => {{
                        avatarLabel.innerText = "Connecting…";
                        connectBtn.disabled = true;
                        connectBtn.style.opacity = 0.6;

                        try {{
                            const response = await fetch(backendUrl + '/api/avatar/stream/create', {{ method: 'POST' }});
                            const data = await response.json();

                            streamId  = data.id;
                            sessionId = data.session_id;
                            isMock    = data.mock;

                            if (isMock) {{
                                avatarLabel.innerText = "Demo Mode Active";
                                demoInfo.style.display = 'block';
                                connectBtn.innerText = "✓ Connected (Demo)";
                                connectBtn.style.background = "linear-gradient(135deg,#047857,#065f46)";
                                connectBtn.disabled = true;
                                return;
                            }}

                            peerConnection = new RTCPeerConnection({{ iceServers: data.ice_servers }});

                            peerConnection.ontrack = (event) => {{
                                if (event.track.kind === 'video') {{
                                    videoEl.srcObject = event.streams[0];
                                    videoEl.style.display = 'block';
                                    placeholderEl.style.display = 'none';
                                    avatarLabel.innerText = "Live!";
                                    connectBtn.innerText = "✓ Connected";
                                    connectBtn.style.background = "linear-gradient(135deg,#047857,#065f46)";
                                }}
                            }};

                            peerConnection.onicecandidate = (event) => {{
                                if (event.candidate) {{
                                    fetch(backendUrl + `/api/avatar/stream/${{streamId}}/ice`, {{
                                        method: 'POST',
                                        headers: {{ 'Content-Type': 'application/json' }},
                                        body: JSON.stringify({{ session_id: sessionId, candidate: event.candidate }})
                                    }});
                                }}
                            }};

                            await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
                            const answer = await peerConnection.createAnswer();
                            await peerConnection.setLocalDescription(answer);

                            await fetch(backendUrl + `/api/avatar/stream/${{streamId}}/sdp`, {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                body: JSON.stringify({{ session_id: sessionId, sdp: answer }})
                            }});

                            setTimeout(speakQuestion, 1500);

                        }} catch (err) {{
                            console.error("WebRTC error:", err);
                            avatarLabel.innerText = "Connection failed";
                            connectBtn.disabled = false;
                            connectBtn.style.opacity = 1;
                        }}
                    }};

                    function speakQuestion() {{
                        const text = {repr(current_q.get("question"))};
                        if (isMock || !streamId || !sessionId) return;
                        fetch(backendUrl + `/api/avatar/stream/${{streamId}}/speak`, {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ session_id: sessionId, text: text }})
                        }});
                    }}
                </script>
                """
                components.html(avatar_html, height=430)

            with col_q:
                st.markdown(
                    f"""
                    <div class="question-card">
                        <span class="question-tag">{current_q.get('skill_tag', 'General')}</span>
                        <div class="question-text">{current_q.get('question')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Play pre-generated TTS audio for this question
                audio_b64 = current_q.get("audio_base64")
                if audio_b64:
                    audio_bytes_tts = base64.b64decode(audio_b64)
                    st.audio(audio_bytes_tts, format="audio/mp3", autoplay=True)

                st.write("")
                st.markdown("### 🎙️ Record Your Answer")
                audio_input = st.audio_input("Tap to record your spoken answer:")

                if audio_input is not None:
                    with st.spinner("Transcribing and grading your answer…"):
                        try:
                            files_payload = {"audio": ("answer.wav", audio_input.getvalue(), "audio/wav")}
                            data_payload  = {"question_id": current_q["id"]}
                            res = requests.post(
                                f"{BACKEND_URL}/api/interview/{session_id}/answer-audio",
                                files=files_payload,
                                data=data_payload,
                                timeout=60
                            )
                            if res.status_code == 200:
                                result = res.json()
                                st.session_state["last_eval"]    = result.get("evaluation", {})
                                st.session_state["showing_eval"] = True
                                st.rerun()
                            else:
                                st.error(f"Error submitting audio: {res.json().get('detail', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Failed to submit audio: {str(e)}")

            st.write("<br>", unsafe_allow_html=True)

            # Text answer fallback
            with st.expander("⌨️ Or Type Your Answer Instead"):
                typed_answer = st.text_area("Your typed response:", height=150)
                submit_text  = st.button("Submit Typed Answer 📤")

                if submit_text:
                    if not typed_answer.strip():
                        st.error("Please enter a response before submitting.")
                    else:
                        with st.spinner("Grading answer…"):
                            try:
                                data_payload = {
                                    "question_id": current_q["id"],
                                    "answer_text": typed_answer
                                }
                                res = requests.post(
                                    f"{BACKEND_URL}/api/interview/{session_id}/answer-text",
                                    data=data_payload,
                                    timeout=30
                                )
                                if res.status_code == 200:
                                    result = res.json()
                                    st.session_state["last_eval"]    = result.get("evaluation", {})
                                    st.session_state["showing_eval"] = True
                                    st.rerun()
                                else:
                                    st.error(f"Error submitting text: {res.json().get('detail', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"Failed to submit text: {str(e)}")

        else:
            # ── All questions answered — show final scorecard ──
            st.markdown(
                """
                <div class="completion-card">
                    <h2>🎉 Mock Interview Completed!</h2>
                    <p style="font-size: 1.15rem; color: #a7f3d0;">
                        Congratulations! You have completed all questions in this session.
                        Review your scorecard and performance feedback below.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            for k in ["last_eval", "showing_eval"]:
                if k in st.session_state:
                    del st.session_state[k]

            tech_scores = [q.get("technical_score") for q in questions if q.get("technical_score") is not None]
            conf_scores = [q.get("confidence_score") for q in questions if q.get("confidence_score") is not None]

            avg_tech = sum(tech_scores) / len(tech_scores) if tech_scores else 0
            avg_conf = sum(conf_scores) / len(conf_scores) if conf_scores else 0

            col_t, col_c = st.columns(2)
            with col_t:
                st.metric("Average Technical Score", f"{avg_tech:.1f} / 5.0")
                st.progress(avg_tech / 5.0)
            with col_c:
                st.metric("Average Confidence Score", f"{avg_conf:.1f} / 5.0")
                st.progress(avg_conf / 5.0)

            st.write("<br>", unsafe_allow_html=True)
            st.markdown("### Question-by-Question Breakdown")

            for i, q in enumerate(questions):
                with st.expander(f"Q{i+1}: {q.get('question')} ({q.get('skill_tag')})"):
                    st.write("**Your Answer:**")
                    st.info(q.get("answer_transcript", "*No answer captured*"))

                    col_st, col_sc = st.columns(2)
                    with col_st:
                        st.write(f"**Technical Score:** `{q.get('technical_score') or 0} / 5`")
                    with col_sc:
                        st.write(f"**Confidence Score:** `{q.get('confidence_score') or 0} / 5`")

                    st.write("**Interviewer Feedback:**")
                    st.write(q.get("feedback", "No feedback recorded."))
    else:
        st.warning("No questions have been generated for this session yet. Please run resume upload first.")
