import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import AIAssistant from './pages/AIAssistant';
import LeadManagement from './pages/LeadManagement';
import Integrations from './pages/Integrations';
import Login from './pages/Login';
import Register from './pages/Register';
import Landing from './pages/Landing';
import { AuthProvider, useAuth } from './components/AuthContext';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/home" replace />;
  }
  return children;
};

// Main App Layout for authenticated users
const MainLayout = ({ children }) => {
  return (
    <div className="flex h-screen bg-surface-bg overflow-hidden">
      {/* Sidebar Navigation */}
      <Navbar />
      
      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto pt-14 md:pt-0 px-4 py-6 md:px-8 lg:px-10 md:py-8">
        <div className="max-w-layout mx-auto">
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
