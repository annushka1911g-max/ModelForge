import React, { useEffect, useState } from 'react';
import { platformService } from '../services/platformService';
import type { DashboardAnalytics } from '../types';
import {
  Box, Rocket, Zap, Clock, TrendingUp, TrendingDown,
  Activity, CheckCircle, XCircle, Server, Database, HardDrive,
  AlertCircle, ArrowUpRight, RefreshCw
} from 'lucide-react';

const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: number;
  color?: string;
  sub?: string;
}> = ({ title, value, icon, trend, color = 'brand', sub }) => (
  <div className="glass-panel rounded-2xl p-5 flex flex-col gap-3 hover:border-brand-700/30 transition-all">
    <div className="flex items-start justify-between">
      <div className={`p-2.5 rounded-xl bg-${color}-500/10 border border-${color}-500/20`}>
        <div className={`text-${color}-400`}>{icon}</div>
      </div>
      {trend !== undefined && (
        <div className={`flex items-center gap-1 text-xs font-medium ${trend >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
          {trend >= 0 ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
          {Math.abs(trend)}%
        </div>
      )}
    </div>
    <div>
      <p className="text-2xl font-bold text-slate-100">{value}</p>
      <p className="text-sm text-slate-400 mt-0.5">{title}</p>
      {sub && <p className="text-xs text-slate-600 mt-1">{sub}</p>}
    </div>
  </div>
);

const HealthBadge: React.FC<{ status: string }> = ({ status }) => {
  const map: Record<string, { color: string; dot: string; label: string }> = {
    healthy:  { color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20', dot: 'bg-emerald-400', label: 'Healthy' },
    connected:{ color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20', dot: 'bg-emerald-400', label: 'Connected' },
    ready:    { color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20', dot: 'bg-emerald-400', label: 'Ready' },
    degraded: { color: 'text-amber-400 bg-amber-500/10 border-amber-500/20',   dot: 'bg-amber-400',   label: 'Degraded' },
    error:    { color: 'text-red-400 bg-red-500/10 border-red-500/20',         dot: 'bg-red-400',     label: 'Error' },
  };
  const cfg = map[status] ?? map.degraded;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border ${cfg.color}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} animate-pulse`} />
      {cfg.label}
    </span>
  );
};

export const DashboardPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await platformService.getDashboardAnalytics();
      setAnalytics(data);
      setLastRefresh(new Date());
    } catch {
      // fallback handled by UI
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const stats = analytics?.stats;
  const charts = analytics?.charts;
  const health = analytics?.system_health;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Platform Dashboard</h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time MLOps overview · Last updated {lastRefresh.toLocaleTimeString()}
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-600/10 border border-brand-500/20 text-brand-400 text-sm hover:bg-brand-600/20 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Stats Grid */}
      {loading && !analytics ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="glass-panel rounded-2xl p-5 h-28 animate-pulse">
              <div className="w-10 h-10 rounded-xl bg-slate-800 mb-3" />
              <div className="w-16 h-6 bg-slate-800 rounded" />
            </div>
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Total Models" value={stats.total_models} icon={<Box className="w-5 h-5" />} color="brand" />
          <StatCard title="Active Deployments" value={stats.active_deployments} icon={<Rocket className="w-5 h-5" />} color="emerald" />
          <StatCard title="Total Predictions" value={stats.total_predictions.toLocaleString()} icon={<Zap className="w-5 h-5" />} color="violet" />
          <StatCard title="Avg Latency" value={`${stats.avg_latency_ms.toFixed(1)} ms`} icon={<Clock className="w-5 h-5" />} color="amber" />
          <StatCard title="Successful Predictions" value={stats.successful_predictions.toLocaleString()} icon={<CheckCircle className="w-5 h-5" />} color="emerald" sub={`${stats.total_predictions > 0 ? ((stats.successful_predictions / stats.total_predictions) * 100).toFixed(1) : 0}% success rate`} />
          <StatCard title="Failed Predictions" value={stats.failed_predictions} icon={<XCircle className="w-5 h-5" />} color="red" />
          <StatCard title="Batch Jobs" value={stats.total_batch_jobs} icon={<Activity className="w-5 h-5" />} color="sky" sub={`${stats.completed_batch_jobs} completed`} />
          <StatCard title="Total Deployments" value={stats.total_deployments} icon={<Server className="w-5 h-5" />} color="slate" />
        </div>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Predictions Over Time */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-base font-semibold text-slate-200">Predictions Over Time</h2>
            <span className="text-xs text-slate-500">Last 7 days</span>
          </div>
          {charts?.predictions_over_time && charts.predictions_over_time.length > 0 ? (
            <div className="space-y-3">
              {charts.predictions_over_time.slice(0, 7).map((day, i) => {
                const maxTotal = Math.max(...charts.predictions_over_time.map(d => d.total || d.successful + d.failed));
                const total = day.total || (day.successful + day.failed);
                const pct = maxTotal > 0 ? (total / maxTotal) * 100 : 0;
                return (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-xs text-slate-500 w-14 text-right">{day.label}</span>
                    <div className="flex-1 h-7 bg-slate-800/50 rounded-lg overflow-hidden relative">
                      <div
                        className="h-full bg-gradient-to-r from-brand-600 to-brand-500 rounded-lg transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                      <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-slate-400 font-mono">
                        {total}
                      </span>
                    </div>
                    <span className="text-xs text-slate-600 w-16">
                      {day.avg_latency?.toFixed(1)}ms
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="flex items-center justify-center h-32 text-slate-600 text-sm">
              No prediction data yet
            </div>
          )}
        </div>

        {/* System Health */}
        <div className="glass-panel rounded-2xl p-6">
          <h2 className="text-base font-semibold text-slate-200 mb-6">System Health</h2>
          {health ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-slate-300">
                  <Activity className="w-4 h-4 text-slate-500" /> API
                </div>
                <HealthBadge status="healthy" />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-slate-300">
                  <Database className="w-4 h-4 text-slate-500" /> Database
                </div>
                <HealthBadge status={health.services?.database?.status ?? 'unknown'} />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-slate-300">
                  <HardDrive className="w-4 h-4 text-slate-500" /> Storage
                </div>
                <HealthBadge status={health.services?.storage?.status ?? 'unknown'} />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-slate-300">
                  <Server className="w-4 h-4 text-slate-500" /> Inference Engine
                </div>
                <HealthBadge status={health.services?.inference_engine?.status ?? 'unknown'} />
              </div>
              <div className="mt-4 pt-4 border-t border-slate-700/50">
                <div className="flex items-center gap-2">
                  {health.status === 'healthy' ? (
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-amber-400" />
                  )}
                  <span className="text-xs font-medium text-slate-300">
                    Overall: <span className={health.status === 'healthy' ? 'text-emerald-400' : 'text-amber-400'}>
                      {health.status.charAt(0).toUpperCase() + health.status.slice(1)}
                    </span>
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {['API', 'Database', 'Storage', 'Inference'].map(s => (
                <div key={s} className="flex items-center justify-between">
                  <span className="text-sm text-slate-500">{s}</span>
                  <div className="w-16 h-5 bg-slate-800 rounded animate-pulse" />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Latency Distribution & Model Usage */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel rounded-2xl p-6">
          <h2 className="text-base font-semibold text-slate-200 mb-5">Latency Distribution</h2>
          {charts?.latency_distribution ? (
            <div className="space-y-4">
              {Object.entries({
                'P50 (Median)': charts.latency_distribution.p50,
                'P90':          charts.latency_distribution.p90,
                'P95':          charts.latency_distribution.p95,
                'P99':          charts.latency_distribution.p99,
              }).map(([label, val]) => (
                <div key={label}>
                  <div className="flex justify-between text-xs text-slate-400 mb-1">
                    <span>{label}</span>
                    <span className="font-mono">{val?.toFixed(1)}ms</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-brand-600 to-violet-500 rounded-full"
                      style={{ width: `${Math.min((val / (charts.latency_distribution.p99 || 1)) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-slate-600 text-sm py-8">No latency data</div>
          )}
        </div>

        <div className="glass-panel rounded-2xl p-6">
          <h2 className="text-base font-semibold text-slate-200 mb-5">Model Usage</h2>
          {charts?.model_usage && charts.model_usage.length > 0 ? (
            <div className="space-y-3">
              {charts.model_usage.slice(0, 6).map((m, i) => {
                const maxPred = Math.max(...charts.model_usage.map(x => x.predictions));
                return (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-brand-500 flex-shrink-0" />
                    <span className="text-xs text-slate-400 truncate flex-1">{m.name}</span>
                    <div className="w-24 h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-brand-500 to-violet-500 rounded-full"
                        style={{ width: `${maxPred > 0 ? (m.predictions / maxPred) * 100 : 0}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-slate-500 w-8 text-right">{m.predictions}</span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center text-slate-600 text-sm py-8">No model usage data</div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-base font-semibold text-slate-200">Recent Models</h2>
            <a href="/models" className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1">
              View all <ArrowUpRight className="w-3 h-3" />
            </a>
          </div>
          <div className="space-y-3">
            {analytics?.recent_models?.slice(0, 5).map((m: any) => (
              <div key={m.id} className="flex items-center gap-3 py-2">
                <div className="w-8 h-8 rounded-lg bg-brand-500/10 border border-brand-500/20 flex items-center justify-center flex-shrink-0">
                  <Box className="w-4 h-4 text-brand-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-200 truncate">{m.display_name}</p>
                  <p className="text-xs text-slate-500">{m.framework} · {m.task_type}</p>
                </div>
                <span className="text-xs text-slate-600">{new Date(m.created_at).toLocaleDateString()}</span>
              </div>
            )) ?? <p className="text-slate-600 text-sm text-center py-4">No models registered</p>}
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-base font-semibold text-slate-200">Recent Deployments</h2>
            <a href="/deployments" className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1">
              View all <ArrowUpRight className="w-3 h-3" />
            </a>
          </div>
          <div className="space-y-3">
            {analytics?.recent_deployments?.slice(0, 5).map((d: any) => (
              <div key={d.id} className="flex items-center gap-3 py-2">
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${d.status === 'RUNNING' ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-200 truncate">{d.model_name}</p>
                  <p className="text-xs text-slate-500 truncate">{d.endpoint_path}</p>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full border ${
                  d.status === 'RUNNING'
                    ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
                    : 'text-slate-500 bg-slate-800 border-slate-700'
                }`}>{d.status}</span>
              </div>
            )) ?? <p className="text-slate-600 text-sm text-center py-4">No deployments yet</p>}
          </div>
        </div>
      </div>
    </div>
  );
};
