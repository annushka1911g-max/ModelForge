import React, { useEffect, useState } from 'react';
import { platformService } from '../services/platformService';
import { Zap, X, ChevronRight } from 'lucide-react';

interface PredictionLog {
  id: number;
  deployment_id: number;
  model_version_id?: number;
  input_features?: any;
  prediction_output?: any;
  latency_ms?: number;
  status_code: number;
  error_message?: string;
  client_ip?: string;
  created_at: string;
}

export const PredictionsPage: React.FC = () => {
  const [logs, setLogs] = useState<PredictionLog[]>([]);
  const [loading, setLoading] = useState(true);

  const [statusFilter, setStatusFilter] = useState<'all' | 'success' | 'error'>('all');
  const [selected, setSelected] = useState<PredictionLog | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await platformService.getAllPredictionLogs({ limit: 500 });
      setLogs(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLogs(); }, []);

  const filtered = logs.filter(log => {
    const matchStatus = statusFilter === 'all' || (statusFilter === 'success' ? log.status_code === 200 : log.status_code !== 200);
    return matchStatus;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Zap className="w-6 h-6 text-violet-400" /> Prediction Logs
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            All real-time inference requests across deployments · {logs.length} total
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="flex gap-1 p-1 bg-slate-800/60 rounded-xl border border-slate-700">
          {(['all', 'success', 'error'] as const).map(f => (
            <button
              key={f}
              onClick={() => setStatusFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                statusFilter === f
                  ? 'bg-brand-600 text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        <span className="text-xs text-slate-500 self-center ml-auto">
          {filtered.length} results
        </span>
      </div>

      <div className="flex gap-6">
        {/* Table */}
        <div className={`flex-1 glass-panel rounded-2xl overflow-hidden ${selected ? 'lg:max-w-2xl' : ''}`}>
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Time</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Deployment</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Latency</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {loading ? (
                [...Array(6)].map((_, i) => (
                  <tr key={i}><td colSpan={5} className="px-4 py-3"><div className="h-4 bg-slate-800 rounded animate-pulse" /></td></tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-16 text-center">
                    <Zap className="w-8 h-8 text-slate-700 mx-auto mb-2" />
                    <p className="text-slate-500 text-sm">No predictions found</p>
                  </td>
                </tr>
              ) : (
                filtered.slice(0, 200).map(log => (
                  <tr
                    key={log.id}
                    onClick={() => setSelected(selected?.id === log.id ? null : log)}
                    className={`cursor-pointer transition-colors ${
                      selected?.id === log.id
                        ? 'bg-brand-600/10 border-l-2 border-brand-500'
                        : 'hover:bg-slate-800/30'
                    }`}
                  >
                    <td className="px-4 py-3 text-xs text-slate-500 font-mono">
                      {new Date(log.created_at).toLocaleTimeString()}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      #{log.deployment_id}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                        log.status_code === 200
                          ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
                          : 'text-red-400 bg-red-500/10 border-red-500/20'
                      }`}>
                        {log.status_code}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs font-mono text-slate-400">
                      {log.latency_ms?.toFixed(1)}ms
                    </td>
                    <td className="px-4 py-3">
                      <ChevronRight className="w-4 h-4 text-slate-600" />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Detail Drawer */}
        {selected && (
          <div className="w-80 flex-shrink-0 glass-panel rounded-2xl p-5 self-start">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-slate-200">Prediction Detail</h3>
              <button onClick={() => setSelected(null)} className="text-slate-500 hover:text-slate-300">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-xs text-slate-500 mb-1">Timestamp</p>
                <p className="text-xs font-mono text-slate-300">{new Date(selected.created_at).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-1">Deployment</p>
                <p className="text-xs text-slate-300">#{selected.deployment_id}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-1">Latency</p>
                <p className="text-sm font-semibold text-amber-400">{selected.latency_ms?.toFixed(2)} ms</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-1">Status</p>
                <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${
                  selected.status_code === 200
                    ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
                    : 'text-red-400 bg-red-500/10 border-red-500/20'
                }`}>{selected.status_code}</span>
              </div>
              {selected.input_features && (
                <div>
                  <p className="text-xs text-slate-500 mb-1">Input Features</p>
                  <pre className="text-[10px] font-mono text-slate-400 bg-slate-900/50 rounded-lg p-3 overflow-auto max-h-40 border border-slate-800">
                    {JSON.stringify(selected.input_features, null, 2)}
                  </pre>
                </div>
              )}
              {selected.prediction_output && (
                <div>
                  <p className="text-xs text-slate-500 mb-1">Prediction Output</p>
                  <pre className="text-[10px] font-mono text-emerald-400 bg-slate-900/50 rounded-lg p-3 overflow-auto max-h-40 border border-slate-800">
                    {JSON.stringify(selected.prediction_output, null, 2)}
                  </pre>
                </div>
              )}
              {selected.error_message && (
                <div>
                  <p className="text-xs text-slate-500 mb-1">Error</p>
                  <p className="text-xs text-red-400 bg-red-500/10 rounded-lg p-2 border border-red-500/20">
                    {selected.error_message}
                  </p>
                </div>
              )}
              {selected.client_ip && (
                <div>
                  <p className="text-xs text-slate-500 mb-1">Client IP</p>
                  <p className="text-xs font-mono text-slate-400">{selected.client_ip}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
