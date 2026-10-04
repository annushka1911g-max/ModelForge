import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../authentication/useAuth';
import { NotificationBell } from '../common/NotificationBell';
import { CommandPalette } from '../common/CommandPalette';
import { Search, Command, LogOut, Shield, ChevronDown } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      setPaletteOpen(true);
    }
  }, []);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <>
      <header className="h-16 glass-panel border-b border-slate-800/60 px-6 flex items-center justify-between z-40 flex-shrink-0">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-glow">
            <span className="text-white font-bold text-sm">M</span>
          </div>
          <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-brand-300 to-brand-500 bg-clip-text text-transparent">
            ModelForge
          </span>
          <span className="text-[10px] bg-brand-950/60 text-brand-400 border border-brand-800/50 px-2 py-0.5 rounded-full font-mono hidden sm:inline-flex">
            Self-Hosted
          </span>
        </div>

        {/* Global Search Trigger */}
        <button
          id="global-search-btn"
          onClick={() => setPaletteOpen(true)}
          className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/50 text-sm text-slate-400 hover:text-slate-300 hover:border-slate-600 transition-all w-56"
        >
          <Search className="w-3.5 h-3.5" />
          <span className="flex-1 text-left">Search...</span>
          <kbd className="flex items-center gap-0.5 text-[10px] bg-slate-700 px-1.5 py-0.5 rounded text-slate-500 font-mono">
            <Command className="w-3 h-3" />K
          </kbd>
        </button>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPaletteOpen(true)}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <Search className="w-5 h-5" />
          </button>

          <NotificationBell />

          {user && (
            <div className="relative">
              <button
                id="user-menu-btn"
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-slate-800/60 transition-colors group"
              >
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center text-xs font-bold text-white">
                  {user.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-xs font-medium text-slate-200 leading-none">{user.full_name}</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">{user.role}</p>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-slate-500 group-hover:text-slate-400" />
              </button>

              {userMenuOpen && (
                <div className="absolute right-0 top-12 w-48 glass-panel rounded-xl shadow-glass z-50 overflow-hidden">
                  <div className="px-4 py-3 border-b border-slate-700/50">
                    <p className="text-xs font-medium text-slate-200">{user.full_name}</p>
                    <p className="text-[10px] text-slate-500 mt-0.5 truncate">{user.email}</p>
                  </div>
                  <div className="py-1">
                    <div className="flex items-center gap-2 px-4 py-2 text-xs text-slate-400">
                      <Shield className="w-3.5 h-3.5" /> Role: {user.role}
                    </div>
                    <button
                      id="logout-btn"
                      onClick={() => { setUserMenuOpen(false); logout(); }}
                      className="w-full flex items-center gap-2 px-4 py-2 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
                    >
                      <LogOut className="w-3.5 h-3.5" /> Sign out
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </header>

      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </>
  );
};
