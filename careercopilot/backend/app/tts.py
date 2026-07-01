import os
import io
import logging
import requests
from gtts import gTTS
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache(maxsize=128)
def generate_speech(text: str) -> bytes:
    """
    Generates TTS audio (MP3 bytes) for the given text.
    Uses ElevenLabs if ELEVENLABS_API_KEY is configured,
    otherwise falls back to Google Text-to-Speech (gTTS).
    """
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if elevenlabs_api_key and elevenlabs_api_key != "your_elevenlabs_api_key_here":
        try:
            logger.info("Generating speech using ElevenLabs API...")
            # Default to voice: Rachel (21m00Tcm4TlvDq8ikWAM)
            voice_id = "21m00Tcm4TlvDq8ikWAM"
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.55
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            if response.status_code == 200:
                logger.info("ElevenLabs TTS generation successful.")
                return response.content
            else:
                logger.warning(f"ElevenLabs API returned status code {response.status_code}. Falling back to gTTS.")
        except Exception as e:
            logger.warning(f"ElevenLabs TTS failed: {str(e)}. Falling back to gTTS.")
            
    # Fallback to gTTS (Google Text-to-Speech)
    try:
        logger.info("Generating speech using gTTS fallback...")
        tts = gTTS(text=text, lang="en", tld="com")
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_bytes = fp.read()
        logger.info("gTTS generation successful.")
        return audio_bytes
    except Exception as e:
        logger.error(f"gTTS fallback failed: {str(e)}")
        # Ultimate fallback: return empty bytes to prevent crash
        return b""
