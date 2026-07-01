import { useState, useRef, useEffect } from 'react';
import './AudioRecorder.css';

/**
 * AudioRecorder — uses MediaRecorder API.
 * Calls onRecordingComplete(blob) when user stops recording.
 * On mount, proactively checks/requests mic permission so the user
 * sees the browser prompt early (not just when they click Record).
 */
export default function AudioRecorder({ onRecordingComplete, disabled }) {
  const [state, setState] = useState('idle'); // idle | requesting | recording | processing | error
  const [errorMsg, setErrorMsg] = useState('');
  const [duration, setDuration] = useState(0);
  const [micGranted, setMicGranted] = useState(null); // null=unknown, true=granted, false=denied
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);

  useEffect(() => () => clearInterval(timerRef.current), []);

  // ── Check permission state on mount (non-blocking) ──
  useEffect(() => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      // Insecure context — mark as denied so we show the warning immediately
      setMicGranted(false);
      setErrorMsg(
        window.location.protocol !== 'https:' && window.location.hostname !== 'localhost'
          ? 'Microphone access requires a secure connection. Please open the app via http://localhost:5173 instead of a network IP address.'
          : 'Your browser does not support microphone recording. Please use Chrome, Edge, or Firefox.'
      );
      setState('error');
      return;
    }

    // Use Permissions API to query status without prompting
    if (navigator.permissions && navigator.permissions.query) {
      navigator.permissions.query({ name: 'microphone' }).then((result) => {
        if (result.state === 'granted') {
          setMicGranted(true);
        } else if (result.state === 'denied') {
          setMicGranted(false);
          setErrorMsg(
            'Microphone permission was previously denied. Click the 🔒 lock icon in your browser address bar → Site settings → Allow microphone, then refresh the page.'
          );
          setState('error');
        } else {
          // 'prompt' — permission not yet asked; show a friendly banner
          setMicGranted(null);
        }
        // Watch for permission changes (e.g. user revokes in settings)
        result.onchange = () => {
          if (result.state === 'granted') {
            setMicGranted(true);
            if (state === 'error') { setState('idle'); setErrorMsg(''); }
          } else if (result.state === 'denied') {
            setMicGranted(false);
          }
        };
      }).catch(() => {
        // Permissions API not available — will ask on first click, that's fine
        setMicGranted(null);
      });
    }
  }, []);

  // ── Proactive "Grant Mic Access" button (fires before recording) ──
  const requestMicPermission = async () => {
    setState('requesting');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Immediately stop all tracks — we just wanted the permission grant
      stream.getTracks().forEach(t => t.stop());
      setMicGranted(true);
      setState('idle');
      setErrorMsg('');
    } catch (err) {
      const message = buildErrorMessage(err);
      setMicGranted(false);
      setErrorMsg(message);
      setState('error');
    }
  };

  const startRecording = async () => {
    setErrorMsg('');

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      const isSecure = window.location.protocol === 'https:' || window.location.hostname === 'localhost';
      const msg = isSecure
        ? 'Your browser does not support microphone recording. Please use Chrome, Edge, or Firefox.'
        : 'Microphone access requires a secure connection. Please open the app via http://localhost:5173 instead of a network IP address.';
      setErrorMsg(msg);
      setState('error');
      return;
    }

    chunksRef.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setMicGranted(true);
      const mr = new MediaRecorder(stream);
      mediaRecorderRef.current = mr;

      mr.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      mr.onstop = () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
        setState('processing');
        onRecordingComplete(blob);
      };

      mr.start();
      setState('recording');
      setDuration(0);
      timerRef.current = setInterval(() => setDuration(d => d + 1), 1000);
    } catch (err) {
      console.error(`Microphone error [${err.name}]:`, err.message);
      setErrorMsg(buildErrorMessage(err));
      setState('error');
    }
  };

  const buildErrorMessage = (err) => {
    switch (err.name) {
      case 'NotAllowedError':
      case 'PermissionDeniedError':
        return 'Microphone permission was denied. Click the 🔒 lock icon in your browser address bar → Site settings → Allow microphone, then refresh or try again.';
      case 'NotFoundError':
      case 'DevicesNotFoundError':
        return 'No microphone detected. Please connect a microphone and try again.';
      case 'NotReadableError':
      case 'TrackStartError':
        return 'Your microphone is already in use by another application. Please close it and try again.';
      case 'OverconstrainedError':
        return 'Your microphone does not meet the required audio constraints. Please try a different microphone.';
      case 'SecurityError':
        return 'Microphone access is blocked by your browser security policy. Please open the app via http://localhost:5173.';
      default:
        return `Could not access microphone (${err.name}: ${err.message}). Please check your browser settings and try again.`;
    }
  };

  const stopRecording = () => {
    clearInterval(timerRef.current);
    mediaRecorderRef.current?.stop();
  };

  const resetToIdle = () => {
    setErrorMsg('');
    setState('idle');
  };

  const fmt = (s) => `${Math.floor(s / 60).toString().padStart(2,'0')}:${(s % 60).toString().padStart(2,'0')}`;

  return (
    <div className="audio-recorder">
      {/* ── Permission prompt banner (shown before first use) ── */}
      {micGranted === null && state === 'idle' && (
        <div className="mic-permission-banner">
          <span className="mic-perm-icon">🎤</span>
          <div className="mic-perm-text">
            <strong>Microphone access needed</strong>
            <span>Click below to grant mic permission before recording.</span>
          </div>
          <button className="btn mic-perm-btn" onClick={requestMicPermission}>
            Allow Mic
          </button>
        </div>
      )}

      {/* Requesting permission spinner */}
      {state === 'requesting' && (
        <div className="loading-overlay" style={{ padding: '1rem' }}>
          <span className="spinner" />
          <span>Requesting microphone access…</span>
        </div>
      )}

      {state === 'idle' && micGranted !== false && (
        <button
          className="btn btn-primary record-btn"
          onClick={startRecording}
          disabled={disabled}
        >
          <span className="record-icon">🎙️</span>
          Start Recording
        </button>
      )}

      {state === 'recording' && (
        <div className="recording-active">
          <div className="recording-waves">
            {[...Array(5)].map((_, i) => (
              <span key={i} className="wave-bar" style={{ animationDelay: `${i * 0.1}s` }} />
            ))}
          </div>
          <span className="recording-timer">{fmt(duration)}</span>
          <button className="btn stop-btn" onClick={stopRecording}>
            ⏹ Stop &amp; Submit
          </button>
        </div>
      )}

      {state === 'processing' && (
        <div className="loading-overlay" style={{ padding: '1.25rem' }}>
          <span className="spinner" />
          <span>Transcribing &amp; grading your answer…</span>
        </div>
      )}

      {state === 'error' && (
        <div className="mic-error">
          <div className="mic-error__icon">🎤</div>
          <p className="mic-error__message">{errorMsg}</p>
          {micGranted !== false && (
            <button className="btn mic-error__retry" onClick={resetToIdle}>
              Try Again
            </button>
          )}
          {micGranted === false && (
            <a
              className="btn mic-error__retry"
              href="https://support.google.com/chrome/answer/2693767"
              target="_blank"
              rel="noreferrer"
            >
              How to fix →
            </a>
          )}
        </div>
      )}
    </div>
  );
}
