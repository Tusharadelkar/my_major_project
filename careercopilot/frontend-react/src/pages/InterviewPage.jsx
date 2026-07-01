import { useState, useEffect, useRef } from 'react';
import { useApp } from '../context/AppContext';
import { getSessionQuestions, submitAudioAnswer, submitTextAnswer } from '../api/interviewApi';
import AvatarPanel from '../components/AvatarPanel';
import AudioRecorder from '../components/AudioRecorder';
import EvalResultCard from '../components/EvalResultCard';
import ScorecardView from '../components/ScorecardView';
import './InterviewPage.css';

export default function InterviewPage() {
  const { sessionId, setSessionId, clearState } = useApp();
  const [manualId, setManualId] = useState('');
  const [questions, setQuestions] = useState([]);
  const [loadingQs, setLoadingQs] = useState(false);
  const [qError, setQError] = useState('');
  const [lastEval, setLastEval] = useState(null);
  const [showingEval, setShowingEval] = useState(false);
  const [typedAnswer, setTypedAnswer] = useState('');
  const [submittingText, setSubmittingText] = useState(false);
  const audioRef = useRef(null);

  const unanswered = questions.filter(q => q.answer_transcript == null);
  const answered = questions.length - unanswered.length;
  const currentQ = unanswered[0] || null;
  const allDone = questions.length > 0 && unanswered.length === 0 && !showingEval;

  // Load questions whenever sessionId changes
  useEffect(() => {
    if (!sessionId) return;
    setLoadingQs(true);
    setQError('');
    getSessionQuestions(sessionId)
      .then(qs => setQuestions(qs))
      .catch(() => setQError('Failed to load questions. Check that the session ID is valid.'))
      .finally(() => setLoadingQs(false));
  }, [sessionId]);

  // Auto-play TTS for current question
  useEffect(() => {
    if (!currentQ?.audio_base64 || showingEval) return;
    if (audioRef.current) {
      audioRef.current.src = `data:audio/mp3;base64,${currentQ.audio_base64}`;
      audioRef.current.play().catch(() => {});
    }
  }, [currentQ?.id, showingEval]);

  const handleAudioComplete = async (blob) => {
    try {
      const result = await submitAudioAnswer(sessionId, currentQ.id, blob);
      setLastEval(result.evaluation);
      setShowingEval(true);
      // Refresh questions list to get updated transcripts/scores
      const updated = await getSessionQuestions(sessionId);
      setQuestions(updated);
    } catch (err) {
      alert('Error submitting audio: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!typedAnswer.trim()) return;
    setSubmittingText(true);
    try {
      const result = await submitTextAnswer(sessionId, currentQ.id, typedAnswer);
      setLastEval(result.evaluation);
      setShowingEval(true);
      setTypedAnswer('');
      const updated = await getSessionQuestions(sessionId);
      setQuestions(updated);
    } catch (err) {
      alert('Error submitting answer: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmittingText(false);
    }
  };

  const handleNext = () => setShowingEval(false);

  const handleReset = () => {
    clearState();
    setQuestions([]);
    setLastEval(null);
    setShowingEval(false);
  };

  // ── No session ──
  if (!sessionId) {
    return (
      <div className="page-wrapper interview-page">
        <h1 className="page-heading gradient-text">AI Mock Interview Console</h1>
        <div className="no-session-card card card-glow">
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🔒</div>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
            No active session. Please upload your resume first, or enter a session ID below.
          </p>
          <form onSubmit={(e) => { e.preventDefault(); const id = parseInt(manualId); if (!isNaN(id)) setSessionId(id); }}
            style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', width: '100%', maxWidth: 420 }}>
            <input
              className="form-input" style={{ flex: 1 }}
              placeholder="Enter Session ID (number)"
              value={manualId} onChange={e => setManualId(e.target.value)}
            />
            <button type="submit" className="btn btn-primary" id="btn-load-session">Load Session</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper interview-page">
      <div className="interview-header">
        <div>
          <h1 className="page-heading gradient-text">AI Mock Interview Console</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Session #{sessionId}</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          {questions.length > 0 && (
            <div className="progress-pill">
              <span className="status-dot online" />
              {answered} / {questions.length} answered
            </div>
          )}
          <button className="btn btn-danger" onClick={handleReset}>↺ Reset Session</button>
        </div>
      </div>

      {/* Hidden audio element for TTS autoplay */}
      <audio ref={audioRef} style={{ display: 'none' }} />

      {loadingQs && (
        <div className="loading-overlay"><span className="spinner spinner-lg" /><span>Loading interview questions…</span></div>
      )}
      {qError && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{qError}</div>}

      {/* ── Final Scorecard ── */}
      {allDone && <ScorecardView questions={questions} />}

      {/* ── Evaluation Result ── */}
      {showingEval && lastEval && (
        <div className="eval-section fade-in-up">
          <EvalResultCard evaluation={lastEval} questionNum={answered} totalQuestions={questions.length} />
          <button
            id="btn-next-question"
            className="btn btn-primary btn-full"
            onClick={handleNext}
            style={{ marginTop: '0.75rem' }}
          >
            {unanswered.length > 0
              ? `Next Question (${answered + 1}/${questions.length}) →`
              : '🏆 View Final Scorecard'}
          </button>
        </div>
      )}

      {/* ── Current Question ── */}
      {!showingEval && !allDone && currentQ && (
        <>
          <div className="question-progress">
            Question <strong>{answered + 1}</strong> of <strong>{questions.length}</strong>
            <div className="progress-track" style={{ marginTop: '0.5rem' }}>
              <div className="progress-fill" style={{ width: `${(answered / questions.length) * 100}%` }} />
            </div>
          </div>

          <div className="interview-grid">
            {/* Avatar */}
            <AvatarPanel questionText={currentQ.question} />

            {/* Question + Answer */}
            <div className="question-answer-col">
              <div className="question-card card card-glow">
                <span className="badge badge-skill-tag">{currentQ.skill_tag || 'General'}</span>
                <p className="question-text">{currentQ.question}</p>
              </div>

              <div className="answer-section card">
                <div className="section-title">🎙️ Record Your Answer</div>
                <AudioRecorder onRecordingComplete={handleAudioComplete} />

                <hr className="divider" style={{ margin: '1.25rem 0' }} />

                <details>
                  <summary>⌨️ Or Type Your Answer Instead</summary>
                  <div className="details-body">
                    <form onSubmit={handleTextSubmit} style={{ marginTop: '0.75rem' }}>
                      <textarea
                        id="typed-answer"
                        className="form-textarea"
                        placeholder="Type your answer here…"
                        value={typedAnswer}
                        onChange={e => setTypedAnswer(e.target.value)}
                        style={{ minHeight: 120 }}
                      />
                      <button
                        id="btn-submit-text"
                        type="submit"
                        className="btn btn-primary btn-full"
                        style={{ marginTop: '0.75rem' }}
                        disabled={submittingText}
                      >
                        {submittingText
                          ? <><span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Grading…</>
                          : '📤 Submit Text Answer'}
                      </button>
                    </form>
                  </div>
                </details>
              </div>
            </div>
          </div>
        </>
      )}

      {/* No questions state */}
      {!loadingQs && !qError && questions.length === 0 && (
        <div className="no-session-card card">
          <span style={{ fontSize: '2rem' }}>⚠️</span>
          <p style={{ color: 'var(--text-muted)' }}>No questions found for this session. Please upload your resume first to generate personalized interview questions.</p>
        </div>
      )}
    </div>
  );
}
