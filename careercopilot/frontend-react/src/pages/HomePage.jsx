import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { createOrGetStudent } from '../api/studentApi';
import './HomePage.css';

const FEATURES = [
  {
    icon: '📊',
    title: 'ATS Job Matching',
    desc: 'Upload your resume alongside target job descriptions to analyze keyword matching, score suitability, and identify improvements instantly.',
  },
  {
    icon: '💬',
    title: 'AI Mock Interviews',
    desc: 'Engage in interactive technical and behavioral question rounds. Get scoring and comprehensive qualitative feedback on each answer.',
  },
  {
    icon: '🎯',
    title: 'Skill-Gap Analysis',
    desc: 'Uncover missing requirements for your dream jobs and receive automated action items to bridge the gap and stay competitive.',
  },
  {
    icon: '🎙️',
    title: 'Voice Answers',
    desc: 'Record spoken answers using your microphone. Groq Whisper transcribes your speech to text for AI-powered grading.',
  },
  {
    icon: '🤖',
    title: 'AI Avatar Interviewer',
    desc: 'A WebRTC-powered D-ID avatar reads questions aloud, simulating a real interview environment.',
  },
  {
    icon: '⚡',
    title: 'Instant Feedback',
    desc: 'Receive detailed technical and confidence scores plus actionable interviewer feedback after every answer.',
  },
];

export default function HomePage() {
  const { studentId, studentName, studentEmail, setStudent } = useApp();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleStart = async (e) => {
    e.preventDefault();
    setError('');
    if (!name.trim() || !email.trim()) { setError('Please enter both your name and email.'); return; }

    setLoading(true);
    try {
      const data = await createOrGetStudent(name.trim(), email.trim());
      setStudent(data.id, data.name, data.email);
    } catch (_) {
      // Fallback: store locally if backend fails
      setStudent(999, name.trim(), email.trim());
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page page-wrapper">
      {/* ── Hero ── */}
      <section className="hero-section fade-in-up">
        <div className="hero-badge">🚀 AI-Powered Career Preparation</div>
        <h1 className="hero-title">
          Land Your Dream Job<br />
          with <span className="gradient-text">CareerCopilot AI</span>
        </h1>
        <p className="hero-subtitle">
          Real-time ATS job matching, personalized mock interviews, and automated skill-gap analysis —
          all in one platform built for students.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary" style={{ fontSize: '1.05rem', padding: '0.85rem 2rem' }}
            onClick={() => studentId ? navigate('/upload') : document.getElementById('session-form').scrollIntoView({ behavior: 'smooth' })}>
            {studentId ? '→ Go to Resume Upload' : 'Get Started Free'}
          </button>
          <button className="btn btn-secondary" style={{ fontSize: '1.05rem', padding: '0.85rem 2rem' }}
            onClick={() => navigate('/interview')}>
            View Demo Interview
          </button>
        </div>
      </section>

      {/* ── Features Grid ── */}
      <section className="features-section">
        <h2 className="features-heading">Everything You Need to Prepare</h2>
        <div className="grid-3">
          {FEATURES.map((f, i) => (
            <div key={i} className="feature-card card fade-in-up" style={{ animationDelay: `${i * 0.07}s` }}>
              <div className="feature-icon">{f.icon}</div>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Session Form or Active Session ── */}
      <section id="session-form" className="session-section">
        {studentId ? (
          <div className="session-active card card-glow fade-in-up">
            <div className="session-active-icon">✓</div>
            <div>
              <h3 style={{ color: '#34d399', marginBottom: '0.25rem' }}>Session Active</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                Logged in as <strong>{studentName}</strong> ({studentEmail})
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem', flexWrap: 'wrap' }}>
              <button className="btn btn-primary" onClick={() => navigate('/upload')}>📄 Upload Resume</button>
              <button className="btn btn-secondary" onClick={() => navigate('/interview')}>💬 Start Interview</button>
            </div>
          </div>
        ) : (
          <div className="session-form-card card card-glow fade-in-up">
            <h2 className="session-form-title">🚀 Initialize Your Session</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '0.95rem' }}>
              Enter your details to create a personalized career profile.
            </p>
            <form onSubmit={handleStart}>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input id="input-name" className="form-input" placeholder="John Doe" value={name} onChange={e => setName(e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input id="input-email" type="email" className="form-input" placeholder="john@example.com" value={email} onChange={e => setEmail(e.target.value)} />
              </div>
              {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}
              <button id="btn-start-session" type="submit" className="btn btn-primary btn-full" disabled={loading}>
                {loading ? <><span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Creating Session…</> : 'Start CareerCopilot Session 🚀'}
              </button>
            </form>
          </div>
        )}
      </section>
    </div>
  );
}
