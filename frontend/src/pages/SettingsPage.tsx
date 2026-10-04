import React, { useEffect, useState } from 'react';
import { platformService } from '../services/platformService';
import { useAuth } from '../authentication/useAuth';
import type { ApiKey } from '../types';
import {
  Settings, KeyRound, Plus, Trash2, Eye, EyeOff, Copy,
  CheckCircle, AlertTriangle, User, Shield, Moon
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'apikeys' | 'preferences'>('profile');
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [keysLoading, setKeysLoading] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [showKey, setShowKey] = useState(false);
  const [copied, setCopied] = useState(false);
  const [creating, setCreating] = useState(false);
  const [revoking, setRevoking] = useState<number | null>(null);

  const fetchKeys = async () => {
    setKeysLoading(true);
    try {
      const data = await platformService.listApiKeys();
      setApiKeys(data);
    } finally {
      setKeysLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'apikeys') fetchKeys();
  }, [activeTab]);

  const createKey = async () => {
    if (!newKeyName.trim()) return;
    setCreating(true);
    try {
      const result = await platformService.createApiKey(newKeyName.trim());
      setCreatedKey(result.key);
      setNewKeyName('');
      fetchKeys();
    } finally {
      setCreating(false);
    }
  };

  const revokeKey = async (id: number) => {
    setRevoking(id);
    try {
      await platformService.revokeApiKey(id);
      setApiKeys(prev => prev.map(k => k.id === id ? { ...k, is_active: false } : k));
    } finally {
      setRevoking(null);
    }
  };

  const copyKey = () => {
    if (createdKey) {
      navigator.clipboard.writeText(createdKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const tabs = [
    { id: 'profile' as const,     label: 'Profile',      icon: <User className="w-4 h-4" /> },
    { id: 'apikeys' as const,     label: 'API Keys',     icon: <KeyRound className="w-4 h-4" /> },
    { id: 'preferences' as const, label: 'Preferences',  icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Settings className="w-6 h-6 text-slate-400" /> Settings
        </h1>
        <p className="text-sm text-slate-500 mt-1">Manage your account, API keys, and preferences</p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar tabs */}
        <div className="w-48 flex-shrink-0">
          <nav className="space-y-1">
            {tabs.map(tab => (
              <button
                key={tab.id}
                id={`settings-tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all text-left ${
                  activeTab === tab.id
                    ? 'bg-brand-600/15 text-brand-300 border border-brand-500/20'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                }`}
              >
                <span className={activeTab === tab.id ? 'text-brand-400' : 'text-slate-500'}>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {activeTab === 'profile' && (
            <div className="glass-panel rounded-2xl p-6 space-y-5">
              <h2 className="text-base font-semibold text-slate-200">Account Profile</h2>
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center text-2xl font-bold text-white shadow-glow">
                  {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div>
                  <p className="text-lg font-semibold text-slate-200">{user?.full_name}</p>
                  <p className="text-sm text-slate-400">{user?.email}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="glass-panel-subtle rounded-xl p-4">
                  <p className="text-xs text-slate-500 mb-1">Role</p>
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4 text-brand-400" />
                    <span className="text-sm font-medium text-brand-300">{user?.role}</span>
                  </div>
                </div>
                <div className="glass-panel-subtle rounded-xl p-4">
                  <p className="text-xs text-slate-500 mb-1">Status</p>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm font-medium text-emerald-400">Active</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'apikeys' && (
            <div className="space-y-4">
              <div className="glass-panel rounded-2xl p-6">
                <h2 className="text-base font-semibold text-slate-200 mb-1">API Keys</h2>
                <p className="text-xs text-slate-500 mb-5">Use API keys for programmatic access. Keys are only shown once on creation.</p>

                {/* Create Key */}
                <div className="flex gap-3">
                  <input
                    value={newKeyName}
                    onChange={e => setNewKeyName(e.target.value)}
                    placeholder="Key name (e.g., 'Production Service')"
                    className="flex-1 px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-brand-500"
                    onKeyDown={e => e.key === 'Enter' && createKey()}
                    id="api-key-name-input"
                  />
                  <button
                    onClick={createKey}
                    disabled={creating || !newKeyName.trim()}
                    id="create-api-key-btn"
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-600/15 border border-brand-500/30 text-brand-400 text-sm hover:bg-brand-600/25 transition-all disabled:opacity-40"
                  >
                    <Plus className="w-4 h-4" /> Create
                  </button>
                </div>

                {/* Newly created key */}
                {createdKey && (
                  <div className="mt-4 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                      <span className="text-sm font-medium text-emerald-400">API key created — copy it now</span>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <code className="flex-1 text-xs font-mono bg-slate-900 rounded-lg px-3 py-2 text-emerald-300 break-all">
                        {showKey ? createdKey : '•'.repeat(createdKey.length)}
                      </code>
                      <button onClick={() => setShowKey(!showKey)} className="p-2 text-slate-500 hover:text-slate-300">
                        {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                      <button onClick={copyKey} className="p-2 text-slate-500 hover:text-slate-300">
                        {copied ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                    <p className="text-xs text-amber-400 flex items-center gap-1 mt-2">
                      <AlertTriangle className="w-3 h-3" /> This key will not be shown again. Store it securely.
                    </p>
                    <button onClick={() => setCreatedKey(null)} className="mt-2 text-xs text-slate-500 hover:text-slate-300">Dismiss</button>
                  </div>
                )}
              </div>

              {/* Keys List */}
              <div className="glass-panel rounded-2xl overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700/50">
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Name</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Key Prefix</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Status</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Created</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Last Used</th>
                      <th className="px-4 py-3" />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {keysLoading ? (
                      [...Array(3)].map((_, i) => (
                        <tr key={i}><td colSpan={6} className="px-4 py-3"><div className="h-4 bg-slate-800 rounded animate-pulse" /></td></tr>
                      ))
                    ) : apiKeys.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-slate-500 text-sm">
                          No API keys. Create one above.
                        </td>
                      </tr>
                    ) : (
                      apiKeys.map(k => (
                        <tr key={k.id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-4 py-3 text-sm text-slate-200 font-medium">{k.name}</td>
                          <td className="px-4 py-3 text-xs text-slate-400 font-mono">{k.key_prefix}...</td>
                          <td className="px-4 py-3">
                            {k.is_active ? (
                              <span className="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full">Active</span>
                            ) : (
                              <span className="text-xs text-slate-500 bg-slate-800 border border-slate-700 px-2 py-0.5 rounded-full">Revoked</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-xs text-slate-500">{new Date(k.created_at).toLocaleDateString()}</td>
                          <td className="px-4 py-3 text-xs text-slate-600">{k.last_used_at ? new Date(k.last_used_at).toLocaleDateString() : 'Never'}</td>
                          <td className="px-4 py-3">
                            {k.is_active && (
                              <button
                                onClick={() => revokeKey(k.id)}
                                disabled={revoking === k.id}
                                className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300 disabled:opacity-50 transition-colors"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                                {revoking === k.id ? 'Revoking...' : 'Revoke'}
                              </button>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'preferences' && (
            <div className="glass-panel rounded-2xl p-6 space-y-6">
              <h2 className="text-base font-semibold text-slate-200">Preferences</h2>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-200">Dark Mode</p>
                  <p className="text-xs text-slate-500 mt-0.5">ModelForge runs in dark mode by default for optimal readability</p>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700">
                  <Moon className="w-4 h-4 text-brand-400" />
                  <span className="text-xs text-slate-300">Always Dark</span>
                </div>
              </div>
              <div className="border-t border-slate-700/50 pt-4">
                <p className="text-xs text-slate-500">More preferences coming soon...</p>
              </div>
              <div className="p-4 bg-brand-500/5 border border-brand-500/10 rounded-xl">
                <p className="text-xs text-slate-500 font-mono">ModelForge v2.0 · Self-Hosted MLOps Platform</p>
                <p className="text-xs text-slate-600 mt-1">Backend: FastAPI · Frontend: React + Vite + Tailwind</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
