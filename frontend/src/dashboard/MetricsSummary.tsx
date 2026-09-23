import React from 'react';

export const MetricsSummary: React.FC = () => {
  const stats = [
    { title: 'Active Deployments', value: '3', change: '+1 this week' },
    { title: 'Total Inferences', value: '14,230', change: '99.8% success' },
    { title: 'Avg Latency', value: '18.4 ms', change: '-2.1 ms vs p95' },
    { title: 'Registered Models', value: '8', change: '4 frameworks' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((s, i) => (
        <div key={i} className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5">
          <p className="text-sm font-medium text-slate-400">{s.title}</p>
          <p className="text-2xl font-bold text-slate-100 mt-2">{s.value}</p>
          <p className="text-xs text-blue-400 mt-1">{s.change}</p>
        </div>
      ))}
    </div>
  );
};
