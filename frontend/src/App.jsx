import React, { useEffect, useState, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import AIAssistant from './pages/AIAssistant';
import LeadManagement from './pages/LeadManagement';
import Integrations from './pages/Integrations';
import Login from './pages/Login';
import Register from './pages/Register';
import Landing from './pages/Landing';
import { AuthProvider, useAuth } from './components/AuthContext';
import { getUserSettings } from './api/client';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/home" replace />;
  }
  return children;
};

// ── Google Reconnect Banner ──────────────────────────────────────────────────
// Fetches /user/settings and shows a sticky warning when needs_google_reconnect
// is true (i.e. the token is 6+ days old). Polls every 60 s so it disappears
// automatically once the user reconnects from the Integrations page.
const ReconnectBanner = () => {
  const [show, setShow] = useState(false);
  const { user } = useAuth();

  const checkReconnect = useCallback(async () => {
    if (!user) return;
    try {
      const res = await getUserSettings();
      setShow(res?.data?.needs_google_reconnect === true);
    } catch {
      // silently ignore — banner visibility is non-critical
    }
  }, [user]);

  useEffect(() => {
    checkReconnect();

    // Poll every 60 s — auto-hides as soon as backend returns false
    const interval = setInterval(checkReconnect, 60_000);
    return () => clearInterval(interval);
  }, [checkReconnect]);

  if (!show) return null;

  return (
    <div
      id="google-reconnect-banner"
      role="alert"
      className={[
        // Clear the fixed mobile top-bar (h-14) so the banner isn't hidden behind it
        'mt-14 md:mt-0',
        // Layout: stack on mobile, row on md+
        'w-full flex flex-col md:flex-row md:items-center md:justify-between',
        'gap-2 md:gap-4',
        // Colours & spacing
        'bg-amber-50 border-b border-amber-200',
        'px-4 py-3 md:py-2.5',
        'text-sm z-20',
      ].join(' ')}
    >
      {/* Message row */}
      <div className="flex items-start md:items-center gap-2 text-amber-700 font-medium min-w-0">
        <AlertTriangle size={16} className="shrink-0 text-amber-500 mt-0.5 md:mt-0" />
        <span className="leading-snug">
          {/* Short version on mobile, full version on md+ */}
          <span className="md:hidden">
            Google connection expires soon.
          </span>
          <span className="hidden md:inline">
            Your Google connection expires in less than 24 hours. Reconnect to keep automation running.
          </span>
        </span>
      </div>

      {/* Action button — full-width pill on mobile, compact link on md+ */}
      <Link
        to="/integrations"
        className={[
          'flex items-center justify-center gap-1.5 font-semibold transition-colors',
          // Mobile: full-width amber button
          'w-full rounded-lg bg-amber-500 text-white py-2 px-4',
          // md+: revert to inline text link style
          'md:w-auto md:rounded-none md:bg-transparent md:text-amber-700',
          'md:hover:text-amber-900 md:py-0 md:px-0',
          'whitespace-nowrap',
        ].join(' ')}
      >
        <RefreshCw size={14} />
        Reconnect Now
      </Link>
    </div>
  );
};

// Main App Layout for authenticated users
const MainLayout = ({ children }) => {
  return (
    <div className="flex h-screen bg-surface-bg overflow-hidden">
      {/* Sidebar Navigation */}
      <Navbar />

      {/* Main Content Area — stacked: banner + scrollable content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <ReconnectBanner />
        <main className="flex-1 overflow-y-auto pt-14 md:pt-0 px-4 py-6 md:px-8 lg:px-10 md:py-8">
          <div className="max-w-layout mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/home" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <MainLayout><Dashboard /></MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/assistant" element={
            <ProtectedRoute>
              <MainLayout><AIAssistant /></MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/leads" element={
            <ProtectedRoute>
              <MainLayout><LeadManagement /></MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/integrations" element={
            <ProtectedRoute>
              <MainLayout><Integrations /></MainLayout>
            </ProtectedRoute>
          } />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
