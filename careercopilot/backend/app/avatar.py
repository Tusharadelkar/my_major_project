import os
import base64
import logging
import requests

logger = logging.getLogger(__name__)

D_ID_BASE_URL = "https://api.d-id.com"
DEFAULT_AVATAR_URL = "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg"

def get_auth_headers() -> dict:
    """Helper to get D-ID API headers with Basic Auth."""
    did_api_key = os.getenv("DID_API_KEY")
    if not did_api_key or did_api_key == "your_d_id_api_key_here":
        return {}
    
    # D-ID uses Basic Auth. If the API key is already in the format "username:password"
    # (which includes a colon), encode it directly. Otherwise, assume password is empty.
    credentials = did_api_key if ":" in did_api_key else f"{did_api_key}:"
    encoded_auth = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    return {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }

def create_talk_stream() -> dict:
    """
    Initiate a talk stream session on D-ID.
    Returns: WebRTC offer, session ID, stream ID, and ICE servers.
    """
    headers = get_auth_headers()
    if not headers:
        logger.warning("DID_API_KEY is not configured. Returning mock stream data.")
        return get_mock_stream_data()

    url = f"{D_ID_BASE_URL}/talks/streams"
    payload = {
        "source_url": DEFAULT_AVATAR_URL
    }

    try:
        logger.info("Calling D-ID Talks Streams API to create new WebRTC stream session...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            logger.info("Successfully created D-ID stream session.")
            return {
                "id": data.get("id"),
                "session_id": data.get("session_id"),
                "offer": data.get("offer"),
                "ice_servers": data.get("ice_servers"),
                "mock": False
            }
        else:
            logger.error(f"D-ID API failed with status {response.status_code}: {response.text}")
            return get_mock_stream_data()
    except Exception as e:
        logger.error(f"Error creating talk stream: {str(e)}")
        return get_mock_stream_data()

def submit_sdp_answer(stream_id: str, session_id: str, sdp_answer: dict) -> bool:
    """Submit client WebRTC SDP answer to D-ID stream."""
    headers = get_auth_headers()
    if not headers or stream_id == "mock_stream":
        logger.info("Mock SDP answer submission accepted.")
        return True

    url = f"{D_ID_BASE_URL}/talks/streams/{stream_id}/sdp"
    payload = {
        "answer": sdp_answer,
        "session_id": session_id
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            logger.info("Successfully submitted SDP answer to D-ID.")
            return True
        else:
            logger.error(f"Failed to submit SDP answer: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error submitting SDP answer: {str(e)}")
        return False

def submit_ice_candidate(stream_id: str, session_id: str, candidate: dict) -> bool:
    """Forward WebRTC local ICE candidates to D-ID."""
    headers = get_auth_headers()
    if not headers or stream_id == "mock_stream":
        return True

    url = f"{D_ID_BASE_URL}/talks/streams/{stream_id}/ice"
    payload = {
        "candidate": candidate.get("candidate"),
        "sdpMid": candidate.get("sdpMid"),
        "sdpMLineIndex": candidate.get("sdpMLineIndex"),
        "session_id": session_id
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            return True
        else:
            logger.error(f"Failed to submit ICE candidate: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error submitting ICE candidate: {str(e)}")
        return False

def trigger_stream_speech(stream_id: str, session_id: str, text: str) -> bool:
    """Command the D-ID avatar to speak specific text on the WebRTC stream."""
    headers = get_auth_headers()
    if not headers or stream_id == "mock_stream":
        logger.info(f"Mock avatar speech triggered for text: {text}")
        return True

    url = f"{D_ID_BASE_URL}/talks/streams/{stream_id}"
    payload = {
        "script": {
            "type": "text",
            "subtitles": False,
            "provider": {
                "type": "microsoft",
                "voice_id": "en-US-JennyNeural"
            },
            "input": text
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.0
        },
        "session_id": session_id
    }

    try:
        logger.info(f"Triggering speech stream for text: '{text[:30]}...'")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201, 202):
            logger.info("Speech stream successfully triggered.")
            return True
        else:
            logger.error(f"Failed to trigger speech: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error triggering speech: {str(e)}")
        return False

def get_mock_stream_data() -> dict:
    """Fallback generator for mock WebRTC setup."""
    return {
        "id": "mock_stream",
        "session_id": "mock_session",
        "offer": {
            "type": "offer",
            "sdp": "v=0\r\no=- 421312 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=sendrecv\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 127.0.0.1\r\n"
        },
        "ice_servers": [{"urls": ["stun:stun.l.google.com:19302"]}],
        "mock": True
    }
