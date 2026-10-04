import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Badge } from '../components/common/Badge';
import { deploymentService } from '../services/deploymentService';
import { modelService } from '../services/modelService';
import { Deployment, Model } from '../types';

export const RecentDeployments: React.FC = () => {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [modelsMap, setModelsMap] = useState<Record<number, Model>>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [depList, modelList] = await Promise.all([
          deploymentService.getDeployments(),
          modelService.getModels(),
        ]);
        setDeployments(depList);
        const map: Record<number, Model> = {};
        modelList.forEach((m) => {
          map[m.id] = m;
        });
        setModelsMap(map);
      } catch (err) {
        console.error('Failed to load recent deployments:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'DEPLOYED':
        return <Badge variant="success">DEPLOYED</Badge>;
      case 'STOPPED':
        return <Badge variant="danger">STOPPED</Badge>;
      case 'ROLLING_BACK':
        return <Badge variant="warning">ROLLING_BACK</Badge>;
      default:
        return <Badge variant="info">{status}</Badge>;
    }
  };

  return (
    <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-slate-100">Live Endpoints & Deployments</h2>
        <Link to="/deployments" className="text-xs text-blue-400 hover:text-blue-300">
          View all deployments &rarr;
        </Link>
      </div>

      {isLoading ? (
        <div className="py-8 text-center text-slate-400 text-sm">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
          Loading deployments...
        </div>
      ) : deployments.length === 0 ? (
        <div className="py-8 text-center text-slate-400 text-sm">
          No deployments found. Register a model and deploy a version to get started.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-xs uppercase bg-slate-900/50 text-slate-400">
              <tr>
                <th className="px-4 py-3">Model</th>
                <th className="px-4 py-3">Version</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Inference Endpoint</th>
                <th className="px-4 py-3">Deployed At</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {deployments.map((dep) => {
                const model = modelsMap[dep.model_id];
                return (
                  <tr key={dep.id} className="hover:bg-slate-750/30 transition-colors">
                    <td className="px-4 py-3 font-medium text-slate-200">
                      {model ? model.display_name : `Model #${dep.model_id}`}
                      <div className="text-xs text-slate-400 font-mono">{model?.name}</div>
                    </td>
                    <td className="px-4 py-3">v{dep.current_version_id}</td>
                    <td className="px-4 py-3">{getStatusBadge(dep.status)}</td>
                    <td className="px-4 py-3 font-mono text-xs text-blue-400">
                      {dep.endpoint_path}
                    </td>
                    <td className="px-4 py-3 text-slate-400 text-xs">
                      {dep.deployed_at ? new Date(dep.deployed_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {dep.status === 'DEPLOYED' && (
                        <Link
                          to="/playground"
                          className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-2.5 py-1 rounded transition-colors"
                        >
                          Test in Playground
                        </Link>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
