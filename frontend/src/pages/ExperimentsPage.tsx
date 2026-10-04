import React, { useEffect, useState } from 'react';
import { platformService } from '../services/platformService';
import type { Experiment } from '../types';
import { FlaskConical, Plus, Check, X, Clock, PlayCircle } from 'lucide-react';

const STATUS_STYLES: Record<string, string> = {
  COMPLETED:  'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  RUNNING:    'text-blue-400 bg-blue-500/10 border-blue-500/20',
  PENDING:    'text-amber-400 bg-amber-500/10 border-amber-500/20',
  FAILED:     'text-red-400 bg-red-500/10 border-red-500/20',
  CANCELLED:  'text-slate-400 bg-slate-800 border-slate-700',
};

const STATUS_ICONS: Record<string, React.ReactNode> = {
  COMPLETED: <Check className="w-3 h-3" />,
  RUNNING:   <PlayCircle className="w-3 h-3" />,
  PENDING:   <Clock className="w-3 h-3" />,
  FAILED:    <X className="w-3 h-3" />,
  CANCELLED: <X className="w-3 h-3" />,
};

const initialForm = {
  name: '',
  description: '',
  dataset_name: '',
  dataset_version: '',
  status: 'PENDING',
  parameters: '{}',
  metrics: '{}',
};

export const ExperimentsPage: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<number[]>([]);
  const [comparison, setComparison] = useState<any>(null);
  const [showComparison, setShowComparison] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const fetchExperiments = async () => {
    setLoading(true);
    try {
      const data = await platformService.listExperiments({ search: search || undefined, status: statusFilter || undefined });
      setExperiments(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchExperiments(); }, [search, statusFilter]);

  const handleSubmit = async () => {
    if (!form.name.trim()) { setError('Name is required'); return; }
    setSubmitting(true);
    setError(null);
    try {
      const params = JSON.parse(form.parameters);
      const metrics = JSON.parse(form.metrics);
      await platformService.createExperiment({
        name: form.name,
        description: form.description || undefined,
        dataset_name: form.dataset_name || undefined,
        dataset_version: form.dataset_version || undefined,
        status: form.status,
        parameters: params,
        metrics,
      });
      setShowModal(false);
      setForm(initialForm);
      fetchExperiments();
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to create experiment');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCompare = async () => {
    if (selected.length < 2) return;
    const data = await platformService.compareExperiments(selected);
    setComparison(data);
    setShowComparison(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <FlaskConical className="w-6 h-6 text-amber-400" />
            Experiments
          </h1>
          <p className="text-sm text-slate-500 mt-1">Track hyperparameters, metrics, and model performance across training runs</p>
        </div>
        <div className="flex gap-2">
          {selected.length >= 2 && (
            <button
              onClick={handleCompare}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600/15 border border-violet-500/30 text-violet-400 text-sm hover:bg-violet-600/25 transition-all"
            >
              Compare {selected.length} Selected
            </button>
          )}
          <button
            onClick={() => setShowModal(true)}
            id="create-experiment-btn"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-brand-600 to-brand-700 text-white text-sm font-medium hover:from-brand-500 hover:to-brand-600 transition-all shadow-glow"
          >
            <Plus className="w-4 h-4" /> New Experiment
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search experiments..."
          className="px-3 py-2 rounded-xl bg-slate-800/60 border border-slate-700 text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-brand-500 transition-colors"
        />
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="px-3 py-2 rounded-xl bg-slate-800/60 border border-slate-700 text-sm text-slate-200 outline-none focus:border-brand-500 transition-colors"
        >
          <option value="">All Statuses</option>
          {['PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'].map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Experiment Table */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700/50">
              <th className="px-4 py-3 text-left">
                <input
                  type="checkbox"
                  checked={selected.length === experiments.length && experiments.length > 0}
                  onChange={e => setSelected(e.target.checked ? experiments.map(x => x.id) : [])}
                  className="rounded border-slate-700 bg-slate-800 text-brand-500"
                />
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Name</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Dataset</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Key Metrics</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {loading ? (
              [...Array(4)].map((_, i) => (
                <tr key={i}><td colSpan={6} className="px-4 py-4"><div className="h-5 bg-slate-800 rounded animate-pulse" /></td></tr>
              ))
            ) : experiments.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-16 text-center">
                  <FlaskConical className="w-8 h-8 text-slate-700 mx-auto mb-2" />
                  <p className="text-slate-500 text-sm">No experiments yet. Create one to start tracking runs.</p>
                </td>
              </tr>
            ) : (
              experiments.map(exp => (
                <tr key={exp.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selected.includes(exp.id)}
                      onChange={e => setSelected(prev => e.target.checked ? [...prev, exp.id] : prev.filter(id => id !== exp.id))}
                      className="rounded border-slate-700 bg-slate-800 text-brand-500"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-sm font-medium text-slate-200">{exp.name}</p>
                    {exp.description && <p className="text-xs text-slate-500 truncate max-w-48">{exp.description}</p>}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border ${STATUS_STYLES[exp.status] ?? STATUS_STYLES.PENDING}`}>
                      {STATUS_ICONS[exp.status]}
                      {exp.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-xs text-slate-400">{exp.dataset_name || '—'}</p>
                    {exp.dataset_version && <p className="text-xs text-slate-600">{exp.dataset_version}</p>}
                  </td>
                  <td className="px-4 py-3">
                    {exp.metrics && Object.keys(exp.metrics).length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {Object.entries(exp.metrics).slice(0, 3).map(([k, v]) => (
                          <span key={k} className="text-[10px] px-1.5 py-0.5 bg-slate-800 rounded text-slate-400 font-mono">
                            {k}: {typeof v === 'number' ? v.toFixed(3) : String(v)}
                          </span>
                        ))}
                      </div>
                    ) : <span className="text-xs text-slate-600">—</span>}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">
                    {new Date(exp.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Comparison View */}
      {showComparison && comparison && (
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-slate-200">Experiment Comparison</h2>
            <button onClick={() => setShowComparison(false)} className="text-slate-500 hover:text-slate-300">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="px-3 py-2 text-left text-xs text-slate-500">Metric / Param</th>
                  {comparison.experiments?.map((e: Experiment) => (
                    <th key={e.id} className="px-3 py-2 text-left text-xs text-brand-400">{e.name}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {comparison.metric_keys?.map((key: string) => (
                  <tr key={key}>
                    <td className="px-3 py-2 text-xs font-mono text-slate-400">{key}</td>
                    {comparison.experiments?.map((e: Experiment) => {
                      const val = e.metrics?.[key];
                      return (
                        <td key={e.id} className="px-3 py-2 text-xs font-mono text-slate-300">
                          {typeof val === 'number' ? val.toFixed(4) : val ?? '—'}
                        </td>
                      );
                    })}
                  </tr>
                ))}
                {comparison.parameter_keys?.map((key: string) => (
                  <tr key={key} className="opacity-60">
                    <td className="px-3 py-2 text-xs font-mono text-slate-500">param: {key}</td>
                    {comparison.experiments?.map((e: Experiment) => {
                      const val = e.parameters?.[key];
                      return (
                        <td key={e.id} className="px-3 py-2 text-xs font-mono text-slate-400">
                          {val !== undefined ? String(val) : '—'}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" onClick={() => setShowModal(false)}>
          <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" />
          <div
            className="relative w-full max-w-lg glass-panel rounded-2xl shadow-glass p-6"
            onClick={e => e.stopPropagation()}
          >
            <h2 className="text-base font-semibold text-slate-200 mb-5">Create Experiment</h2>
            <div className="space-y-4">
              {error && <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">{error}</p>}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Name *</label>
                <input
                  value={form.name}
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-sm text-slate-200 outline-none focus:border-brand-500"
                  placeholder="e.g., RF-v1-baseline"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Description</label>
                <textarea
                  value={form.description}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  rows={2}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-sm text-slate-200 outline-none focus:border-brand-500 resize-none"
                  placeholder="Optional description..."
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Dataset Name</label>
                  <input
                    value={form.dataset_name}
                    onChange={e => setForm(f => ({ ...f, dataset_name: e.target.value }))}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-sm text-slate-200 outline-none focus:border-brand-500"
                    placeholder="iris_dataset"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Dataset Version</label>
                  <input
                    value={form.dataset_version}
                    onChange={e => setForm(f => ({ ...f, dataset_version: e.target.value }))}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-sm text-slate-200 outline-none focus:border-brand-500"
                    placeholder="v1.0"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Parameters (JSON)</label>
                <textarea
                  value={form.parameters}
                  onChange={e => setForm(f => ({ ...f, parameters: e.target.value }))}
                  rows={2}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-300 font-mono outline-none focus:border-brand-500 resize-none"
                  placeholder='{"n_estimators": 100, "max_depth": 5}'
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Metrics (JSON)</label>
                <textarea
                  value={form.metrics}
                  onChange={e => setForm(f => ({ ...f, metrics: e.target.value }))}
                  rows={2}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-300 font-mono outline-none focus:border-brand-500 resize-none"
                  placeholder='{"accuracy": 0.95, "f1_score": 0.94}'
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Status</label>
                <select
                  value={form.status}
                  onChange={e => setForm(f => ({ ...f, status: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-sm text-slate-200 outline-none focus:border-brand-500"
                >
                  {['PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'].map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 rounded-xl bg-slate-800 text-slate-400 text-sm hover:text-slate-200 hover:bg-slate-700 transition-colors">
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-brand-600 to-brand-700 text-white text-sm font-medium hover:from-brand-500 hover:to-brand-600 transition-all disabled:opacity-50"
              >
                {submitting ? 'Creating...' : 'Create Experiment'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
