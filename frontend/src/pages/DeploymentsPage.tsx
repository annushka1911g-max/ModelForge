import React from 'react';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';

export const DeploymentsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Deployments</h1>
          <p className="text-sm text-slate-400">Manage live model inference endpoints and one-click rollbacks</p>
        </div>
      </div>

      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="text-xs uppercase bg-slate-900/50 text-slate-400">
            <tr>
              <th className="px-4 py-3">Deployment</th>
              <th className="px-4 py-3">Version</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">API Endpoint</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            <tr>
              <td className="px-4 py-3 font-semibold text-slate-200">churn-prediction-xgb</td>
              <td className="px-4 py-3">v2</td>
              <td className="px-4 py-3"><Badge variant="success">DEPLOYED</Badge></td>
              <td className="px-4 py-3 font-mono text-xs text-blue-400">/api/v1/deployments/1/predict</td>
              <td className="px-4 py-3 text-right space-x-2">
                <Button size="sm" variant="secondary">Rollback to v1</Button>
                <Button size="sm" variant="danger">Stop</Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
