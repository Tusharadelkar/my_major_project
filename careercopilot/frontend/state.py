import streamlit as st

def init_state():
    """Initializes default values in streamlit session state if they do not exist."""
    defaults = {
        "session_id": None,
        "student_id": None,
        "student_name": "",
        "student_email": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_session_id():
    init_state()
    return st.session_state["session_id"]

def set_session_id(session_id):
    st.session_state["session_id"] = session_id

def get_student_id():
    init_state()
    return st.session_state["student_id"]

def set_student_id(student_id):
    st.session_state["student_id"] = student_id

def get_student_info():
    init_state()
    return {
        "id": st.session_state["student_id"],
        "name": st.session_state["student_name"],
        "email": st.session_state["student_email"],
    }

def set_student_info(student_id, name, email):
    st.session_state["student_id"] = student_id
    st.session_state["student_name"] = name
    st.session_state["student_email"] = email

def clear_state():
    st.session_state["session_id"] = None
    st.session_state["student_id"] = None
    st.session_state["student_name"] = ""
    st.session_state["student_email"] = ""
