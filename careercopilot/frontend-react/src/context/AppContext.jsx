import { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext(null);

const STORAGE_KEY = 'careercopilot_state';

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch (_) {}
  return { studentId: null, studentName: '', studentEmail: '', sessionId: null };
}

export function AppProvider({ children }) {
  const [state, setState] = useState(loadFromStorage);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  const setStudent = (id, name, email) =>
    setState(s => ({ ...s, studentId: id, studentName: name, studentEmail: email }));

  const setSessionId = (id) =>
    setState(s => ({ ...s, sessionId: id }));

  const clearState = () => {
    setState({ studentId: null, studentName: '', studentEmail: '', sessionId: null });
  };

  return (
    <AppContext.Provider value={{ ...state, setStudent, setSessionId, clearState }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  return useContext(AppContext);
}
