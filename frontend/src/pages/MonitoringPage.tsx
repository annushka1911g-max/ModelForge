import React from 'react';

export const MonitoringPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Telemetry & Monitoring</h1>
          <p className="text-sm text-slate-400">Live Grafana and Prometheus observability metrics</p>
        </div>
        <a
          href="http://localhost:3001"
          target="_blank"
          rel="noreferrer"
          className="text-xs bg-slate-800 hover:bg-slate-700 text-blue-400 border border-slate-700 px-3 py-1.5 rounded-lg transition-colors"
        >
          Open Grafana Console &rarr;
        </a>
      </div>

      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6 h-96 flex items-center justify-center text-slate-500">
        <p>Grafana Embedded Dashboard View Placeholder</p>
      </div>
    </div>
  );
};
