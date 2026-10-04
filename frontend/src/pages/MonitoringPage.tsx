import React, { useEffect, useState } from 'react';
import { inferenceService } from '../services/inferenceService';

export const MonitoringPage: React.FC = () => {
  const [stats, setStats] = useState({
    total_models: 0,
    total_deployments: 0,
    active_deployments: 0,
    total_predictions: 0,
    successful_predictions: 0,
    failed_predictions: 0,
    avg_latency_ms: 0,
    total_batch_jobs: 0,
  });
  const [logs, setLogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [statsData, logsData] = await Promise.all([
        inferenceService.getMonitoringStats(),
        inferenceService.getRecentLogs(50),
      ]);
      setStats(statsData);
      setLogs(logsData);
    } catch (err) {
      console.error('Failed to load telemetry:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, []);

  const successRate =
    stats.total_predictions > 0
      ? ((stats.successful_predictions / stats.total_predictions) * 100).toFixed(1)
      : '100.0';

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
            Telemetry & Observability
          </h1>
          <p className="text-sm text-slate-400">
            Real-time inference health, latency distributions, and live prediction logs
          </p>
        </div>

        <div className="flex gap-2">
          <a
            href="http://localhost:9090"
            target="_blank"
            rel="noreferrer"
            className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 rounded-lg transition-colors"
          >
            Prometheus UI &rarr;
          </a>
          <a
            href="http://localhost:3001"
            target="_blank"
            rel="noreferrer"
            className="text-xs bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 px-3 py-1.5 rounded-lg transition-colors font-medium"
          >
            Grafana Dashboard &rarr;
          </a>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-4">
          <span className="text-xs text-slate-400">Total Inferences</span>
          <p className="text-2xl font-bold text-slate-100 mt-1 font-mono">
            {isLoading ? '...' : stats.total_predictions}
          </p>
          <span className="text-xs text-blue-400 mt-1 block">Live API requests</span>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-4">
          <span className="text-xs text-slate-400">Success Rate</span>
          <p className="text-2xl font-bold text-emerald-400 mt-1 font-mono">
            {isLoading ? '...' : `${successRate}%`}
          </p>
          <span className="text-xs text-emerald-500 mt-1 block">
            {stats.successful_predictions} successful
          </span>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-4">
          <span className="text-xs text-slate-400">Failed Inferences</span>
          <p className={`text-2xl font-bold mt-1 font-mono ${stats.failed_predictions > 0 ? 'text-rose-400' : 'text-slate-100'}`}>
            {isLoading ? '...' : stats.failed_predictions}
          </p>
          <span className="text-xs text-slate-500 mt-1 block">Validation & execution errors</span>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-4">
          <span className="text-xs text-slate-400">Avg Latency</span>
          <p className="text-2xl font-bold text-blue-400 mt-1 font-mono">
            {isLoading ? '...' : `${stats.avg_latency_ms} ms`}
          </p>
          <span className="text-xs text-slate-500 mt-1 block">Model execution time</span>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-4 col-span-2 lg:col-span-1">
          <span className="text-xs text-slate-400">Active Endpoints</span>
          <p className="text-2xl font-bold text-emerald-400 mt-1 font-mono">
            {isLoading ? '...' : stats.active_deployments}
          </p>
          <span className="text-xs text-slate-500 mt-1 block">
            {stats.total_deployments} total registered
          </span>
        </div>
      </div>

      {/* Live Prediction Logs */}
      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-slate-100">Live Prediction Access Log</h2>
          <span className="text-xs font-mono text-slate-400">Auto-refreshing every 8s</span>
        </div>

        {isLoading ? (
          <div className="py-12 text-center text-slate-400">Loading prediction logs...</div>
        ) : logs.length === 0 ? (
          <div className="text-center py-10 text-slate-500 text-sm">
            No prediction logs recorded yet. Run a prediction from Playground or API to populate logs.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-slate-900/50 text-slate-400">
                <tr>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">Deployment</th>
                  <th className="px-4 py-3">Version</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Latency</th>
                  <th className="px-4 py-3">Client IP</th>
                  <th className="px-4 py-3">Error / Note</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50 font-mono text-xs">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-750/30">
                    <td className="px-4 py-3 text-slate-400">
                      {log.created_at ? new Date(log.created_at).toLocaleTimeString() : 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-slate-200">Dep #{log.deployment_id}</td>
                    <td className="px-4 py-3 text-slate-300">v{log.model_version_id}</td>
                    <td className="px-4 py-3">
                      {log.status_code === 200 ? (
                        <span className="text-emerald-400 font-bold">200 OK</span>
                      ) : (
                        <span className="text-rose-400 font-bold">{log.status_code} ERR</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-blue-400">{log.latency_ms} ms</td>
                    <td className="px-4 py-3 text-slate-400">{log.client_ip || 'unknown'}</td>
                    <td className="px-4 py-3 text-slate-400 font-sans truncate max-w-xs">
                      {log.error_message || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
