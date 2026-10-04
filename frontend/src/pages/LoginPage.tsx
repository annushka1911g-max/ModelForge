import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../authentication/useAuth';
import { authService } from '../services/authService';
import { Button } from '../components/common/Button';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide both email and password.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await authService.login(email, password);
      login(res.access_token, res.user);
      navigate('/dashboard');
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  const fillCredentials = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-md w-full shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/60 border border-blue-800/60 text-blue-400 text-xs font-mono mb-1">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
            ModelForge v1.0
          </div>
          <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            Welcome to ModelForge
          </h1>
          <p className="text-sm text-slate-400">Sign in to manage and serve production ML models</p>
        </div>

        {error && (
          <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-sm px-4 py-3 rounded-lg flex items-start gap-2">
            <span className="text-rose-400 font-bold">!</span>
            <span>{error}</span>
          </div>
        )}

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
              placeholder="admin@modelforge.local"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
              placeholder="••••••••"
              required
            />
          </div>
          <Button id="login-submit" type="submit" disabled={isLoading} className="w-full flex items-center justify-center gap-2">
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Signing In...
              </>
            ) : (
              'Sign In'
            )}
          </Button>
        </form>

        <div className="border-t border-slate-800 pt-4 space-y-2">
          <p className="text-xs font-medium text-slate-400 text-center">Quick Demo Credentials:</p>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => fillCredentials('admin@modelforge.io', 'AdminPassword123!')}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-blue-300 border border-slate-700 py-1.5 px-2 rounded transition-colors"
            >
              Admin
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('engineer@modelforge.io', 'EngineerPassword123!')}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-slate-700 py-1.5 px-2 rounded transition-colors"
            >
              ML Engineer
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('viewer@modelforge.io', 'ViewerPassword123!')}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-purple-300 border border-slate-700 py-1.5 px-2 rounded transition-colors"
            >
              Viewer
            </button>
          </div>
        </div>

        <p className="text-xs text-center text-slate-500">
          Don't have an account?{' '}
          <Link to="/register" className="text-blue-400 hover:underline">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
};
