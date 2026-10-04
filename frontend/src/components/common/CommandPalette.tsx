import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, Command, X, Box, Zap, FlaskConical, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { platformService } from '../../services/platformService';
import type { SearchItem } from '../../types';

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
}

const typeIcon = (type: string) => {
  switch (type) {
    case 'model': return <Box className="w-4 h-4 text-brand-400" />;
    case 'deployment': return <Zap className="w-4 h-4 text-emerald-400" />;
    case 'experiment': return <FlaskConical className="w-4 h-4 text-amber-400" />;
    default: return null;
  }
};

export const CommandPalette: React.FC<CommandPaletteProps> = ({ open, onClose }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<{ models: SearchItem[]; deployments: SearchItem[]; experiments: SearchItem[] }>({ models: [], deployments: [], experiments: [] });
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const allResults: SearchItem[] = [...results.models, ...results.deployments, ...results.experiments];

  useEffect(() => {
    if (open) {
      setQuery('');
      setResults({ models: [], deployments: [], experiments: [] });
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  const doSearch = useCallback(async (q: string) => {
    if (!q.trim() || q.length < 2) {
      setResults({ models: [], deployments: [], experiments: [] });
      return;
    }
    setLoading(true);
    try {
      const data = await platformService.search(q);
      setResults(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const t = setTimeout(() => doSearch(query), 300);
    return () => clearTimeout(t);
  }, [query, doSearch]);

  const handleSelect = (item: SearchItem) => {
    navigate(item.url);
    onClose();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20" onClick={onClose}>
      <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" />
      <div
        className="relative w-full max-w-2xl glass-panel rounded-2xl shadow-glass overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input */}
        <div className="flex items-center gap-3 px-4 py-4 border-b border-slate-700/50">
          <Search className="w-5 h-5 text-slate-400 flex-shrink-0" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search models, deployments, experiments..."
            className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-base outline-none"
            onKeyDown={(e) => { if (e.key === 'Escape') onClose(); }}
          />
          {loading && <span className="text-xs text-slate-500 animate-pulse">searching...</span>}
          <button onClick={onClose} className="p-1 text-slate-500 hover:text-slate-300 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results */}
        <div className="max-h-96 overflow-y-auto">
          {allResults.length === 0 && query.length >= 2 && !loading ? (
            <div className="py-12 text-center text-slate-500 text-sm">
              No results found for "{query}"
            </div>
          ) : allResults.length === 0 && query.length < 2 ? (
            <div className="py-8 px-4 text-center">
              <div className="flex items-center justify-center gap-2 text-slate-500 text-sm">
                <Command className="w-4 h-4" />
                <span>Type at least 2 characters to search across models, deployments and experiments</span>
              </div>
            </div>
          ) : (
            <div className="py-2">
              {allResults.map((item) => (
                <button
                  key={`${item.type}-${item.id}`}
                  onClick={() => handleSelect(item)}
                  className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-800/60 transition-colors group text-left"
                >
                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center border border-slate-700/50">
                    {typeIcon(item.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-200 truncate">{item.title}</p>
                    <p className="text-xs text-slate-500 truncate">{item.subtitle}</p>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors" />
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="px-4 py-2 border-t border-slate-700/50 flex items-center gap-4 text-xs text-slate-600">
          <span><kbd className="font-mono">↑↓</kbd> navigate</span>
          <span><kbd className="font-mono">↵</kbd> select</span>
          <span><kbd className="font-mono">Esc</kbd> close</span>
        </div>
      </div>
    </div>
  );
};
