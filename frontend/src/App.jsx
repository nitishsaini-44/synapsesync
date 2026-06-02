import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import AIAssistant from './pages/AIAssistant';
import LeadManagement from './pages/LeadManagement';
import Login from './pages/Login';
import Register from './pages/Register';
import { AuthProvider, useAuth } from './components/AuthContext';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

// Main App Layout for authenticated users
const MainLayout = ({ children }) => {
  return (
    <div className="flex h-screen bg-dark-bg text-slate-100 overflow-hidden">
      {/* Sidebar Navigation */}
      <Navbar />
      
      {/* Main Content Area — pt-14 offsets the fixed mobile top bar */}
      <main className="flex-1 overflow-y-auto bg-dark-bg pt-14 md:pt-0 p-4 md:p-8">
        <div className="max-w-6xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
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
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
