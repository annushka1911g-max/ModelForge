import React from 'react';
import { MetricsSummary } from './MetricsSummary';
import { RecentDeployments } from './RecentDeployments';

export const DashboardOverview: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-100">Platform Overview</h1>
      </div>
      <MetricsSummary />
      <RecentDeployments />
    </div>
  );
};
