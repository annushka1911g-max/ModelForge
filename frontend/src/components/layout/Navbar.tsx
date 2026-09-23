import React from 'react';
import { useAuth } from '../../authentication/useAuth';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          ModelForge
        </span>
        <span className="text-xs bg-blue-950 text-blue-400 border border-blue-800 px-2 py-0.5 rounded font-mono">
          Self-Hosted
        </span>
      </div>

      <div className="flex items-center gap-4">
        {user && (
          <div className="flex items-center gap-3 text-sm">
            <span className="text-slate-300">{user.full_name}</span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
              {user.role}
            </span>
            <button
              onClick={logout}
              className="text-xs text-red-400 hover:text-red-300 ml-2"
            >
              Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
