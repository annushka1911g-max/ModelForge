import React from 'react';
import { Badge } from '../components/common/Badge';

export const RecentDeployments: React.FC = () => {
  return (
    <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6">
      <h2 className="text-lg font-semibold text-slate-100 mb-4">Active Deployments</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="text-xs uppercase bg-slate-900/50 text-slate-400">
            <tr>
              <th className="px-4 py-3">Model</th>
              <th className="px-4 py-3">Version</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Endpoint</th>
              <th className="px-4 py-3">Deployed At</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            <tr>
              <td className="px-4 py-3 font-medium text-slate-200">churn-prediction-xgb</td>
              <td className="px-4 py-3">v2</td>
              <td className="px-4 py-3"><Badge variant="success">DEPLOYED</Badge></td>
              <td className="px-4 py-3 font-mono text-xs text-blue-400">/api/v1/deployments/1/predict</td>
              <td className="px-4 py-3 text-slate-400">Today, 14:20</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
