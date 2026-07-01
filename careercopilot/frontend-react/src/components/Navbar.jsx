import { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import client from '../api/client';
import './Navbar.css';

export default function Navbar() {
  const { studentName, sessionId, clearState } = useApp();
  const [backendOnline, setBackendOnline] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setMenuOpen(false);
  }, [location]);

  useEffect(() => {
    const check = () =>
      client.get('/health', { timeout: 3000 })
        .then(r => setBackendOnline(r.data?.status === 'ok'))
        .catch(() => setBackendOnline(false));
    check();
    const interval = setInterval(check, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="navbar-brand">
          <span className="brand-icon">🤖</span>
          <span className="brand-name">CareerCopilot <span className="brand-ai">AI</span></span>
        </NavLink>

        <button className="nav-hamburger" onClick={() => setMenuOpen(o => !o)} aria-label="Toggle menu">
          <span /><span /><span />
        </button>

        <div className={`navbar-links ${menuOpen ? 'open' : ''}`}>
          <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            🏠 Home
          </NavLink>
          <NavLink to="/upload" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            📄 Resume
          </NavLink>
          <NavLink to="/interview" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            💬 Interview
          </NavLink>
        </div>

        <div className="navbar-right">
          {studentName && (
            <div className="nav-user">
              <span className="user-avatar">{studentName[0].toUpperCase()}</span>
              <span className="user-name">{studentName}</span>
            </div>
          )}
          <div className="status-pill">
            <span className={`status-dot ${backendOnline === null ? 'offline' : backendOnline ? 'online' : 'offline'}`} />
            <span className="status-label">
              {backendOnline === null ? 'Checking…' : backendOnline ? 'API Online' : 'API Offline'}
            </span>
          </div>
          {studentName && (
            <button className="btn btn-danger" style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem' }} onClick={clearState}>
              Sign Out
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
