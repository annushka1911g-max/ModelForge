import React, { useEffect, useState } from 'react';
import { platformService } from '../services/platformService';
import type { AuditLog } from '../types';
import { ScrollText, Filter, RefreshCw, User, Clock } from 'lucide-react';

const ACTION_COLOR: Record<string, string> = {
  MODEL_CREATE:         'text-brand-400 bg-brand-500/10 border-brand-500/20',
  MODEL_UPDATE:         'text-sky-400 bg-sky-500/10 border-sky-500/20',
  DEPLOY:               'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  STOP_DEPLOYMENT:      'text-amber-400 bg-amber-500/10 border-amber-500/20',
  ROLLBACK_DEPLOYMENT:  'text-violet-400 bg-violet-500/10 border-violet-500/20',
  API_KEY_CREATE:       'text-sky-400 bg-sky-500/10 border-sky-500/20',
  API_KEY_REVOKE:       'text-red-400 bg-red-500/10 border-red-500/20',
};

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState('');
  const [resource, setResource] = useState('');
  const [userEmail, setUserEmail] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await platformService.listAuditLogs({
        limit: 200,
        action: action || undefined,
        resource: resource || undefined,
        user_email: userEmail || undefined,
      });
      setLogs(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLogs(); }, [action, resource, userEmail]);

  const uniqueActions = [...new Set(logs.map(l => l.action))].sort();
  const uniqueResources = [...new Set(logs.map(l => l.resource))].sort();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <ScrollText className="w-6 h-6 text-slate-400" /> Audit Logs
          </h1>
          <p className="text-sm text-slate-500 mt-1">Immutable record of all platform actions with actor and timestamp</p>
        </div>
        <button
          onClick={fetchLogs}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 text-slate-400 text-sm hover:text-slate-200 transition-all"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <Filter className="w-4 h-4 text-slate-500" />
        <select
          value={action}
          onChange={e => setAction(e.target.value)}
          className="px-3 py-2 rounded-xl bg-slate-800/60 border border-slate-700 text-sm text-slate-200 outline-none focus:border-brand-500"
        >
          <option value="">All Actions</option>
          {uniqueActions.map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <select
          value={resource}
          onChange={e => setResource(e.target.value)}
          className="px-3 py-2 rounded-xl bg-slate-800/60 border border-slate-700 text-sm text-slate-200 outline-none focus:border-brand-500"
        >
          <option value="">All Resources</option>
          {uniqueResources.map(r => <option key={r} value={r}>{r}</option>)}
        </select>
        <input
          value={userEmail}
          onChange={e => setUserEmail(e.target.value)}
          placeholder="Filter by email..."
          className="px-3 py-2 rounded-xl bg-slate-800/60 border border-slate-700 text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-brand-500"
        />
        <span className="text-xs text-slate-500 ml-auto">{logs.length} events</span>
      </div>

      {/* Table */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700/50">
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Timestamp</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Actor</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Action</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Resource</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Details</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">IP</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {loading ? (
              [...Array(6)].map((_, i) => (
                <tr key={i}><td colSpan={6} className="px-4 py-3"><div className="h-4 bg-slate-800 rounded animate-pulse" /></td></tr>
              ))
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-16 text-center">
                  <ScrollText className="w-8 h-8 text-slate-700 mx-auto mb-2" />
                  <p className="text-slate-500 text-sm">No audit logs found</p>
                </td>
              </tr>
            ) : (
              logs.map(log => (
                <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3 text-xs text-slate-500 font-mono whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3 h-3" />
                      {new Date(log.timestamp).toLocaleString()}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">
                    <div className="flex items-center gap-1.5">
                      <User className="w-3 h-3 text-slate-600" />
                      <span className="truncate max-w-36">{log.user_email ?? `user:${log.user_id}`}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold border uppercase tracking-wider ${ACTION_COLOR[log.action] ?? 'text-slate-400 bg-slate-800 border-slate-700'}`}>
                      {log.action.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400 font-mono capitalize">{log.resource}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">
                    {log.event_metadata && Object.keys(log.event_metadata).length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {Object.entries(log.event_metadata).slice(0, 2).map(([k, v]) => (
                          <span key={k} className="font-mono bg-slate-800 px-1 py-0.5 rounded text-slate-400">
                            {k}={String(v).slice(0, 20)}
                          </span>
                        ))}
                      </div>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3 text-[10px] text-slate-600 font-mono">{log.client_ip ?? '—'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
