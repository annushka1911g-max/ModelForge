import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../authentication/useAuth';
import { authService } from '../services/authService';
import { Button } from '../components/common/Button';
import { UserRole } from '../types';

export const RegisterPage: React.FC = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('ML_ENGINEER');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !email || !password) {
      setError('Please fill in all required fields.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await authService.register({
        full_name: fullName,
        email,
        password,
        role,
      });

      // Automatically sign in upon registration
      const loginRes = await authService.login(email, password);
      login(loginRes.access_token, loginRes.user);
      navigate('/dashboard');
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
          ? detail.map((d: any) => d.msg || d.message).join(', ')
          : 'Registration failed. The email may already be in use.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-md w-full shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            Create ModelForge Account
          </h1>
          <p className="text-sm text-slate-400">Join the self-hosted MLOps workspace</p>
        </div>

        {error && (
          <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-sm px-4 py-3 rounded-lg flex items-start gap-2">
            <span className="text-rose-400 font-bold">!</span>
            <span>{error}</span>
          </div>
        )}

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Full Name</label>
            <input
              id="register-fullname"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
              placeholder="Jane Doe"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
            <input
              id="register-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
              placeholder="jane@example.com"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
            <input
              id="register-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
              placeholder="Min. 8 characters"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Initial Role</label>
            <select
              id="register-role"
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
            >
              <option value="ML_ENGINEER">ML Engineer (Deploy, Models, Predict)</option>
              <option value="ADMIN">Administrator (Full Access)</option>
              <option value="VIEWER">Viewer (Read-only)</option>
            </select>
          </div>
          <Button id="register-submit" type="submit" disabled={isLoading} className="w-full flex items-center justify-center gap-2">
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Creating Account...
              </>
            ) : (
              'Create Account'
            )}
          </Button>
        </form>

        <p className="text-xs text-center text-slate-500">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-400 hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
};
