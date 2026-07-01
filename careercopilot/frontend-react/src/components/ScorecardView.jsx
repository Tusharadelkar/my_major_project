import './ScorecardView.css';

function ProgressRing({ value, max = 5, color = '#818cf8' }) {
  const pct = Math.round((value / max) * 100);
  const r = 36, circ = 2 * Math.PI * r;
  const dash = circ - (pct / 100) * circ;
  return (
    <svg width="90" height="90" viewBox="0 0 90 90">
      <circle cx="45" cy="45" r={r} stroke="#1e2d4a" strokeWidth="7" fill="none" />
      <circle
        cx="45" cy="45" r={r}
        stroke={color} strokeWidth="7" fill="none"
        strokeDasharray={circ}
        strokeDashoffset={dash}
        strokeLinecap="round"
        transform="rotate(-90 45 45)"
        style={{ transition: 'stroke-dashoffset 0.8s ease' }}
      />
      <text x="45" y="50" textAnchor="middle" fill={color} fontSize="15" fontWeight="700">{value}/{max}</text>
    </svg>
  );
}

export default function ScorecardView({ questions }) {
  const answered = questions.filter(q => q.answer_transcript != null);
  const techScores = answered.map(q => q.technical_score || 0);
  const confScores = answered.map(q => q.confidence_score || 0);
  const avgTech = techScores.length ? (techScores.reduce((a, b) => a + b, 0) / techScores.length) : 0;
  const avgConf = confScores.length ? (confScores.reduce((a, b) => a + b, 0) / confScores.length) : 0;

  return (
    <div className="scorecard fade-in-up">
      <div className="completion-banner">
        <div className="completion-icon">🎉</div>
        <h2>Mock Interview Complete!</h2>
        <p>Congratulations! You've answered all {questions.length} questions. Review your performance below.</p>
      </div>

      <div className="scorecard-overview">
        <div className="overview-ring">
          <ProgressRing value={parseFloat(avgTech.toFixed(1))} color="#818cf8" />
          <span className="ring-label">Avg Technical</span>
        </div>
        <div className="overview-ring">
          <ProgressRing value={parseFloat(avgConf.toFixed(1))} color="#34d399" />
          <span className="ring-label">Avg Confidence</span>
        </div>
        <div className="overview-stat">
          <span className="stat-number">{answered.length}</span>
          <span className="stat-label">Questions Answered</span>
        </div>
        <div className="overview-stat">
          <span className="stat-number">
            {Math.round(((avgTech + avgConf) / 10) * 100)}%
          </span>
          <span className="stat-label">Overall Score</span>
        </div>
      </div>

      <div className="section-title" style={{ marginTop: '2rem' }}>Question-by-Question Breakdown</div>
      <div className="breakdown-list">
        {questions.map((q, i) => (
          <details key={q.id} className="breakdown-item card">
            <summary>
              <span className="q-num">Q{i + 1}</span>
              <span className="q-text">{q.question}</span>
              <span className="badge badge-skill-tag" style={{ marginLeft: 'auto', flexShrink: 0 }}>{q.skill_tag}</span>
            </summary>
            <div className="details-body breakdown-body">
              <div className="breakdown-scores">
                <span>Tech: <strong style={{ color: '#818cf8' }}>{q.technical_score ?? '–'}/5</strong></span>
                <span>Confidence: <strong style={{ color: '#34d399' }}>{q.confidence_score ?? '–'}/5</strong></span>
              </div>
              <div className="breakdown-answer">
                <div className="eval-section-label">Your Answer</div>
                <p style={{ fontStyle: 'italic', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  {q.answer_transcript || '(No answer recorded)'}
                </p>
              </div>
              <div>
                <div className="eval-section-label">Feedback</div>
                <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)' }}>
                  {q.feedback || 'No feedback recorded.'}
                </p>
              </div>
            </div>
          </details>
        ))}
      </div>
    </div>
  );
}
