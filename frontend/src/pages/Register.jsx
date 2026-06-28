import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser } from '../api/client';
import { UserPlus, Eye, EyeOff } from 'lucide-react';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await registerUser(name, email, password);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to register');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-bg p-4">
      <div className="w-full max-w-md bg-surface-card rounded-modal border border-border shadow-modal p-8 md:p-10 animate-fade-in">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-primary-light rounded-2xl flex items-center justify-center mx-auto mb-5">
            <UserPlus className="text-primary" size={26} />
          </div>
          <h1 className="text-2xl font-bold text-heading">Create Account</h1>
          <p className="text-muted mt-2 text-[15px]">Join the SynapseSync platform</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 flex items-center gap-2.5 p-3.5 bg-error-light border border-error/15 rounded-button text-error text-sm">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-heading mb-1.5">Full Name</label>
            <input
              type="text"
              required
              className="w-full h-12 px-4 bg-surface-card border border-border rounded-input text-heading placeholder-muted/50 focus:outline-none focus:border-primary focus:shadow-input-focus transition-all duration-200 text-[15px]"
              placeholder="John Doe"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-heading mb-1.5">Email</label>
            <input
              type="email"
              required
              className="w-full h-12 px-4 bg-surface-card border border-border rounded-input text-heading placeholder-muted/50 focus:outline-none focus:border-primary focus:shadow-input-focus transition-all duration-200 text-[15px]"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-heading mb-1.5">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                required
                className="w-full h-12 px-4 pr-12 bg-surface-card border border-border rounded-input text-heading placeholder-muted/50 focus:outline-none focus:border-primary focus:shadow-input-focus transition-all duration-200 text-[15px]"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-0 top-0 h-12 px-3.5 flex items-center justify-center text-muted hover:text-heading transition-colors"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full h-11 px-4 bg-primary text-white rounded-button font-medium hover:bg-primary-hover transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed mt-2 text-[15px]"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        {/* Footer Link */}
        <p className="mt-7 text-center text-sm text-muted">
          Already have an account?{' '}
          <Link to="/login" className="text-primary font-medium hover:text-primary-hover transition-colors">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
