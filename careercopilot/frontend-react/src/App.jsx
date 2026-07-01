import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import UploadPage from './pages/UploadPage';
import InterviewPage from './pages/InterviewPage';

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/interview" element={<InterviewPage />} />
          </Routes>
        </main>
      </BrowserRouter>
    </AppProvider>
  );
}
