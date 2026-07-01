import { useRef, useState, useEffect } from 'react';
import { createAvatarStream, submitSdp, submitIce, triggerSpeak } from '../api/avatarApi';
import './AvatarPanel.css';

export default function AvatarPanel({ questionText }) {
  const videoRef = useRef(null);
  const pcRef = useRef(null);
  const [status, setStatus] = useState('idle'); // idle | connecting | demo | live | error
  const [streamId, setStreamId] = useState(null);
  const [avatarSessionId, setAvatarSessionId] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const speakTimerRef = useRef(null);

  // Auto-connect as soon as the component receives a question
  useEffect(() => {
    if (questionText && status === 'idle') {
      connect();
    }
  }, [questionText]);

  // Auto-speak when question changes and already connected
  useEffect(() => {
    if (status === 'live' && streamId && avatarSessionId && questionText) {
      setIsSpeaking(true);
      triggerSpeak(streamId, avatarSessionId, questionText)
        .catch(console.error)
        .finally(() => {
          // Approximate speaking duration (100ms per char, min 2s, max 12s)
          const dur = Math.min(Math.max(questionText.length * 80, 2000), 12000);
          clearTimeout(speakTimerRef.current);
          speakTimerRef.current = setTimeout(() => setIsSpeaking(false), dur);
        });
    }
    if (status === 'demo' && questionText) {
      setIsSpeaking(true);
      const dur = Math.min(Math.max(questionText.length * 80, 2000), 12000);
      clearTimeout(speakTimerRef.current);
      speakTimerRef.current = setTimeout(() => setIsSpeaking(false), dur);
    }
  }, [questionText, status]);

  // Cleanup
  useEffect(() => () => clearTimeout(speakTimerRef.current), []);

  const connect = async () => {
    setStatus('connecting');
    try {
      const data = await createAvatarStream();
      setStreamId(data.id);
      setAvatarSessionId(data.session_id);

      if (data.mock) {
        setStatus('demo');
        return;
      }

      const pc = new RTCPeerConnection({ iceServers: data.ice_servers });
      pcRef.current = pc;

      pc.ontrack = (event) => {
        if (event.track.kind === 'video' && videoRef.current) {
          videoRef.current.srcObject = event.streams[0];
          setStatus('live');
        }
      };

      pc.onicecandidate = (event) => {
        if (event.candidate) {
          submitIce(data.id, data.session_id, event.candidate).catch(console.error);
        }
      };

      await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      await submitSdp(data.id, data.session_id, answer);

      setTimeout(() => {
        if (questionText) triggerSpeak(data.id, data.session_id, questionText).catch(console.error);
      }, 1500);

    } catch (err) {
      console.error('Avatar connection error:', err);
      // Fallback to demo mode instead of hard error
      setStatus('demo');
    }
  };

  // Demo avatar: animated AI face SVG
  const DemoAvatar = () => (
    <div className={`avatar-demo-face ${isSpeaking ? 'speaking' : ''}`}>
      <svg viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
        {/* Head */}
        <circle cx="60" cy="52" r="34" fill="url(#headGrad)" />
        {/* Eyes */}
        <ellipse cx="47" cy="46" rx="5" ry="6" fill="white" />
        <ellipse cx="73" cy="46" rx="5" ry="6" fill="white" />
        <circle cx="48" cy="47" r="3" fill="#4f46e5" />
        <circle cx="74" cy="47" r="3" fill="#4f46e5" />
        <circle cx="49" cy="46" r="1" fill="white" />
        <circle cx="75" cy="46" r="1" fill="white" />
        {/* Mouth — animate when speaking */}
        {isSpeaking ? (
          <ellipse cx="60" cy="62" rx="10" ry="6" fill="#1e1b4b" className="mouth-open" />
        ) : (
          <path d="M50 61 Q60 68 70 61" stroke="#6366f1" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        )}
        {/* Ears / antenna */}
        <line x1="26" y1="42" x2="26" y2="30" stroke="#818cf8" strokeWidth="2.5" strokeLinecap="round" />
        <circle cx="26" cy="28" r="4" fill="#6366f1" />
        <line x1="94" y1="42" x2="94" y2="30" stroke="#818cf8" strokeWidth="2.5" strokeLinecap="round" />
        <circle cx="94" cy="28" r="4" fill="#6366f1" />
        {/* Neck + body */}
        <rect x="50" y="86" width="20" height="14" rx="4" fill="url(#bodyGrad)" />
        <rect x="36" y="100" width="48" height="18" rx="8" fill="url(#bodyGrad)" />
        <defs>
          <radialGradient id="headGrad" cx="40%" cy="35%">
            <stop offset="0%" stopColor="#818cf8" />
            <stop offset="100%" stopColor="#4338ca" />
          </radialGradient>
          <linearGradient id="bodyGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="100%" stopColor="#4338ca" />
          </linearGradient>
        </defs>
      </svg>
      {/* Speaking sound waves */}
      {isSpeaking && (
        <div className="speak-waves">
          {[0,1,2].map(i => <span key={i} className="speak-wave" style={{ animationDelay: `${i * 0.15}s` }} />)}
        </div>
      )}
    </div>
  );

  return (
    <div className="avatar-panel card">
      <div className={`avatar-ring ${isSpeaking ? 'ring-speaking' : ''}`}>
        {status === 'live' ? (
          <video ref={videoRef} className="avatar-video" autoPlay playsInline muted={false} />
        ) : status === 'connecting' ? (
          <div className="avatar-placeholder">
            <div className="avatar-bot-icon pulsing">
              <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="12" y="20" width="40" height="32" rx="6" stroke="#818cf8" strokeWidth="2.5"/>
                <circle cx="23" cy="34" r="4" fill="#a855f7"/>
                <circle cx="41" cy="34" r="4" fill="#a855f7"/>
                <rect x="26" y="42" width="12" height="3" rx="1.5" fill="#818cf8"/>
                <line x1="22" y1="20" x2="22" y2="14" stroke="#818cf8" strokeWidth="2.5" strokeLinecap="round"/>
                <line x1="42" y1="20" x2="42" y2="14" stroke="#818cf8" strokeWidth="2.5" strokeLinecap="round"/>
                <circle cx="22" cy="12" r="3" fill="#6366f1"/>
                <circle cx="42" cy="12" r="3" fill="#6366f1"/>
                <rect x="28" y="52" width="8" height="6" rx="2" fill="#818cf8"/>
              </svg>
            </div>
            <span className="avatar-status-text">Connecting…</span>
          </div>
        ) : (
          <DemoAvatar />
        )}
      </div>

      {/* Name badge */}
      <div className="avatar-name-badge">
        <span className="avatar-ai-name">Alex</span>
        <span className="avatar-ai-role">AI Interviewer</span>
      </div>

      {(status === 'live' || status === 'demo') && (
        <div className="avatar-connected-badge">
          <span className="status-dot online" />
          {status === 'live'
            ? (isSpeaking ? '🔊 AI Speaking…' : 'Live — Listening')
            : (isSpeaking ? '🔊 Asking question…' : 'AI Interviewer Ready')}
        </div>
      )}
      {status === 'connecting' && (
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '0.5rem' }}>
          <span className="spinner" />
        </div>
      )}
    </div>
  );
}
