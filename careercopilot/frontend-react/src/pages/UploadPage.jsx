import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { uploadResume } from '../api/resumeApi';
import './UploadPage.css';

function AtsRing({ score }) {
  const r = 56, circ = 2 * Math.PI * r;
  const dash = circ - (score / 100) * circ;
  const color = score >= 80 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444';
  return (
    <svg width="140" height="140" viewBox="0 0 140 140" className="ats-ring-svg">
      <circle cx="70" cy="70" r={r} stroke="#1e2d4a" strokeWidth="10" fill="none" />
      <circle cx="70" cy="70" r={r}
        stroke={color} strokeWidth="10" fill="none"
        strokeDasharray={circ} strokeDashoffset={dash}
        strokeLinecap="round" transform="rotate(-90 70 70)"
        style={{ transition: 'stroke-dashoffset 0.9s ease' }}
      />
      <text x="70" y="66" textAnchor="middle" fill={color} fontSize="26" fontWeight="800">{score}%</text>
      <text x="70" y="84" textAnchor="middle" fill="#64748b" fontSize="11">ATS SCORE</text>
    </svg>
  );
}

export default function UploadPage() {
  const { studentId, setSessionId } = useApp();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [file, setFile] = useState(null);
  const [jobDesc, setJobDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  const handleFileChange = (e) => {
    const f = e.target.files?.[0];
    if (f) setFile(f);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f && (f.name.endsWith('.pdf') || f.name.endsWith('.docx'))) setFile(f);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!file) { setError('Please upload a resume file (PDF or DOCX).'); return; }
    if (!jobDesc.trim()) { setError('Please paste a target job description.'); return; }

    setLoading(true);
    setResults(null);
    try {
      const data = await uploadResume(file, jobDesc, studentId);
      setResults(data);
      setSessionId(data.session_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to connect to backend. Make sure the server is running.');
    } finally {
      setLoading(false);
    }
  };

  const atsColor = results
    ? results.ats_score >= 80 ? 'success' : results.ats_score >= 50 ? 'warning' : 'error'
    : null;

  return (
    <div className="upload-page page-wrapper">
      <h1 className="page-heading gradient-text">Resume & ATS Analyzer</h1>
      <p className="page-subheading">Upload your resume (PDF/DOCX) and paste the target job description to get an instant ATS match score and skill gap report.</p>

      <div className="upload-grid">
        {/* ── Left: Input Panel ── */}
        <div className="upload-input-col">
          <form onSubmit={handleSubmit} className="upload-form">
            {/* Drop zone */}
            <div
              className={`drop-zone ${file ? 'has-file' : ''}`}
              onDragOver={e => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input ref={fileInputRef} type="file" accept=".pdf,.docx" onChange={handleFileChange} hidden id="file-input" />
              {file ? (
                <>
                  <span className="drop-zone-icon">📄</span>
                  <span className="drop-zone-filename">{file.name}</span>
                  <span className="drop-zone-hint">Click to change file</span>
                </>
              ) : (
                <>
                  <span className="drop-zone-icon">⬆️</span>
                  <span className="drop-zone-label">Drag & Drop or Click to Upload</span>
                  <span className="drop-zone-hint">Supported: PDF, DOCX</span>
                </>
              )}
            </div>

            <div className="form-group" style={{ marginTop: '1.25rem' }}>
              <label className="form-label" htmlFor="job-desc">Target Job Description</label>
              <textarea
                id="job-desc"
                className="form-textarea"
                placeholder="Paste the full job description or requirements list here…"
                value={jobDesc}
                onChange={e => setJobDesc(e.target.value)}
                style={{ minHeight: 200 }}
              />
            </div>

            {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}

            <button id="btn-run-ats" type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading
                ? <><span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Analyzing Resume…</>
                : '⚡ Run ATS Evaluation'}
            </button>
          </form>
        </div>

        {/* ── Right: Results Panel ── */}
        <div className="upload-results-col">
          <div className="section-title">Evaluation Results</div>

          {loading && (
            <div className="loading-overlay">
              <span className="spinner spinner-lg" />
              <span>Processing resume, calling AI LLM, and calculating scores…</span>
            </div>
          )}

          {!loading && !results && (
            <div className="results-empty card">
              <span style={{ fontSize: '3rem' }}>📊</span>
              <p>Upload a resume and paste a job description, then click <strong>Run ATS Evaluation</strong> to see results here.</p>
            </div>
          )}

          {!loading && results && (
            <div className="results-content fade-in-up">
              {/* Score Ring */}
              <div className="score-ring-card card card-glow">
                <AtsRing score={results.ats_score} />
                <div className={`alert alert-${atsColor}`} style={{ marginTop: '1rem' }}>
                  {results.ats_score >= 80 && '🎉 Great match! Your resume is highly relevant.'}
                  {results.ats_score >= 50 && results.ats_score < 80 && `⚠ Moderate match (${results.ats_score}%). Consider adding missing skills.`}
                  {results.ats_score < 50 && `❌ Low match (${results.ats_score}%). High modifications needed.`}
                </div>
                <div className="progress-track" style={{ marginTop: '0.5rem' }}>
                  <div className="progress-fill" style={{ width: `${results.ats_score}%` }} />
                </div>
              </div>

              {/* Skill Gaps */}
              <div className="skills-grid">
                <div className="skills-col card">
                  <div className="section-title">✅ Matched Skills ({results.matched_skills.length})</div>
                  <div className="badges-wrap">
                    {results.matched_skills.length > 0
                      ? results.matched_skills.map(s => <span key={s} className="badge badge-matched">{s}</span>)
                      : <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No direct matches found.</span>
                    }
                  </div>
                </div>
                <div className="skills-col card">
                  <div className="section-title">❌ Missing Skills ({results.missing_skills.length})</div>
                  <div className="badges-wrap">
                    {results.missing_skills.length > 0
                      ? results.missing_skills.map(s => <span key={s} className="badge badge-missing">{s}</span>)
                      : <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No missing skills!</span>
                    }
                  </div>
                </div>
              </div>

              {/* Parsed Resume Details */}
              <details className="card">
                <summary>🔍 View AI Parsed Resume Details</summary>
                <div className="details-body parsed-details">
                  <div>
                    <div className="section-title" style={{ fontSize: '1rem' }}>Extracted Skills</div>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                      {results.parsed_resume.skills?.join(', ') || '(none found)'}
                    </p>
                  </div>
                  {['experience', 'projects', 'education'].map(key => (
                    results.parsed_resume[key]?.length > 0 && (
                      <div key={key}>
                        <div className="section-title" style={{ fontSize: '1rem', textTransform: 'capitalize' }}>{key}</div>
                        <ul className="parsed-list">
                          {results.parsed_resume[key].map((item, i) => <li key={i}>{item}</li>)}
                        </ul>
                      </div>
                    )
                  ))}
                </div>
              </details>

              {/* CTA to Interview */}
              <button className="btn btn-primary btn-full" style={{ marginTop: '0.5rem' }} onClick={() => navigate('/interview')}>
                💬 Start Mock Interview →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
