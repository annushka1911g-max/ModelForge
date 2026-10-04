import React, { useEffect, useState } from 'react';
import { inferenceService } from '../services/inferenceService';

export const MetricsSummary: React.FC = () => {
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
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchStats = async () => {
      try {
        const data = await inferenceService.getMonitoringStats();
        if (isMounted) setStats(data);
      } catch (err) {
        console.error('Failed to fetch dashboard metrics:', err);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const successRate = stats.total_predictions > 0
    ? `${((stats.successful_predictions / stats.total_predictions) * 100).toFixed(1)}%`
    : '100%';

  const cards = [
    {
      title: 'Active Deployments',
      value: isLoading ? '...' : `${stats.active_deployments}`,
      change: `${stats.total_deployments} total deployments`,
      badgeColor: 'text-emerald-400',
    },
    {
      title: 'Total Inferences',
      value: isLoading ? '...' : `${stats.total_predictions.toLocaleString()}`,
      change: `${successRate} success rate`,
      badgeColor: 'text-blue-400',
    },
    {
      title: 'Avg Inference Latency',
      value: isLoading ? '...' : `${stats.avg_latency_ms} ms`,
      change: `${stats.failed_predictions} failed calls`,
      badgeColor: stats.failed_predictions > 0 ? 'text-amber-400' : 'text-slate-400',
    },
    {
      title: 'Registered Models',
      value: isLoading ? '...' : `${stats.total_models}`,
      change: `${stats.total_batch_jobs} batch jobs`,
      badgeColor: 'text-indigo-400',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((c, i) => (
        <div key={i} className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 hover:border-slate-600 transition-all">
          <p className="text-sm font-medium text-slate-400">{c.title}</p>
          <p className="text-2xl font-bold text-slate-100 mt-2">{c.value}</p>
          <p className={`text-xs mt-1 ${c.badgeColor}`}>{c.change}</p>
        </div>
      ))}
    </div>
  );
};
