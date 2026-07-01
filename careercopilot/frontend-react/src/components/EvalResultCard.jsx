import './EvalResultCard.css';

function Stars({ count, max = 5 }) {
  return (
    <div className="stars">
      {[...Array(max)].map((_, i) => (
        <span key={i} className={`star ${i < count ? 'filled' : 'empty'}`}>★</span>
      ))}
      <span className="star-label">{count}/{max}</span>
    </div>
  );
}

export default function EvalResultCard({ evaluation, questionNum, totalQuestions }) {
  const { technical_score, confidence_score, feedback, transcript } = evaluation;

  return (
    <div className="eval-card card card-glow fade-in-up">
      <div className="eval-header">
        <span className="eval-badge">✅ Answer Evaluated</span>
        <span className="eval-progress">Q{questionNum} of {totalQuestions}</span>
      </div>

      <div className="eval-scores">
        <div className="score-block">
          <div className="score-label-sm">Technical Score</div>
          <Stars count={technical_score} />
        </div>
        <div className="score-divider" />
        <div className="score-block">
          <div className="score-label-sm">Confidence Score</div>
          <Stars count={confidence_score} />
        </div>
      </div>

      <div className="eval-feedback">
        <div className="eval-section-label">🗣 Interviewer Feedback</div>
        <p className="feedback-text">{feedback}</p>
      </div>

      {transcript && (
        <details>
          <summary>📝 Your Transcript</summary>
          <div className="details-body transcript-text">{transcript}</div>
        </details>
      )}
    </div>
  );
}
