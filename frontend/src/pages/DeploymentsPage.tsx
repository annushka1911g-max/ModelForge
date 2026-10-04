import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { deploymentService } from '../services/deploymentService';
import { modelService } from '../services/modelService';
import { useAuth } from '../authentication/useAuth';
import { Deployment, Model, ModelVersion } from '../types';

export const DeploymentsPage: React.FC = () => {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [modelsMap, setModelsMap] = useState<Record<number, Model>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Rollback Modal State
  const [rollbackModal, setRollbackModal] = useState<{
    deployment: Deployment;
    versions: ModelVersion[];
    selectedVersionId: number | null;
  } | null>(null);
  const [isRollingBack, setIsRollingBack] = useState(false);

  const { hasRole } = useAuth();
  const canManage = hasRole(['ADMIN', 'ML_ENGINEER']);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
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
    } catch (err: any) {
      setError('Failed to load deployments.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStop = async (deploymentId: number) => {
    try {
      await deploymentService.stopDeployment(deploymentId);
      setSuccessMsg(`Deployment #${deploymentId} stopped successfully.`);
      await loadData();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to stop deployment.');
    }
  };

  const handleRestart = async (deploymentId: number) => {
    try {
      await deploymentService.restartDeployment(deploymentId);
      setSuccessMsg(`Deployment #${deploymentId} restarted successfully.`);
      await loadData();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to restart deployment.');
    }
  };

  const openRollbackModal = async (dep: Deployment) => {
    try {
      const versions = await modelService.getVersions(dep.model_id);
      const candidates = versions.filter((v) => v.id !== dep.current_version_id);
      setRollbackModal({
        deployment: dep,
        versions: candidates,
        selectedVersionId: dep.previous_version_id || (candidates[0]?.id ?? null),
      });
    } catch (err) {
      setError('Failed to fetch model versions for rollback.');
    }
  };

  const executeRollback = async () => {
    if (!rollbackModal) return;
    setIsRollingBack(true);
    try {
      await deploymentService.rollbackDeployment(
        rollbackModal.deployment.id,
        rollbackModal.selectedVersionId || undefined
      );
      setSuccessMsg(`Deployment #${rollbackModal.deployment.id} rolled back successfully.`);
      setRollbackModal(null);
      await loadData();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to rollback deployment.');
    } finally {
      setIsRollingBack(false);
    }
  };

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
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Deployments</h1>
          <p className="text-sm text-slate-400">
            Manage live model inference endpoints, state lifecycle, and instant rollbacks
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-sm px-4 py-3 rounded-lg flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-rose-400 hover:text-rose-200">
            ✕
          </button>
        </div>
      )}

      {successMsg && (
        <div className="bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm px-4 py-3 rounded-lg flex justify-between items-center">
          <span>{successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="text-emerald-400 hover:text-emerald-200">
            ✕
          </button>
        </div>
      )}

      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6">
        {isLoading ? (
          <div className="py-16 text-center text-slate-400">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            Loading deployments...
          </div>
        ) : deployments.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-sm space-y-3">
            <p>No deployments found.</p>
            <Link to="/models">
              <Button>Go to Models to Deploy</Button>
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-slate-900/50 text-slate-400">
                <tr>
                  <th className="px-4 py-3">Deployment</th>
                  <th className="px-4 py-3">Current Version</th>
                  <th className="px-4 py-3">Previous Version</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Inference Endpoint</th>
                  <th className="px-4 py-3">Last Updated</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {deployments.map((dep) => {
                  const model = modelsMap[dep.model_id];
                  return (
                    <tr key={dep.id} className="hover:bg-slate-750/30 transition-colors">
                      <td className="px-4 py-3 font-medium text-slate-200">
                        {model ? (
                          <Link
                            to={`/models/${model.id}`}
                            className="text-blue-400 hover:underline font-semibold"
                          >
                            {model.display_name}
                          </Link>
                        ) : (
                          `Deployment #${dep.id}`
                        )}
                        <div className="text-xs text-slate-500 font-mono">
                          ID: {dep.id} | Model ID: {dep.model_id}
                        </div>
                      </td>
                      <td className="px-4 py-3 font-semibold text-slate-200">
                        v{dep.current_version_id}
                      </td>
                      <td className="px-4 py-3 text-slate-400">
                        {dep.previous_version_id ? `v${dep.previous_version_id}` : 'None'}
                      </td>
                      <td className="px-4 py-3">{getStatusBadge(dep.status)}</td>
                      <td className="px-4 py-3 font-mono text-xs text-blue-400">
                        {dep.endpoint_path}
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-400">
                        {dep.updated_at ? new Date(dep.updated_at).toLocaleString() : 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex justify-end gap-2">
                          {dep.status === 'DEPLOYED' && (
                            <>
                              <Link
                                to="/playground"
                                className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-2.5 py-1.5 rounded transition-colors"
                              >
                                Test
                              </Link>
                              {canManage && (
                                <>
                                  <Button
                                    size="sm"
                                    variant="secondary"
                                    onClick={() => openRollbackModal(dep)}
                                  >
                                    Rollback
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="danger"
                                    onClick={() => handleStop(dep.id)}
                                  >
                                    Stop
                                  </Button>
                                </>
                              )}
                            </>
                          )}
                          {dep.status === 'STOPPED' && canManage && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => handleRestart(dep.id)}
                            >
                              Restart
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Rollback Modal */}
      {rollbackModal && (
        <Modal
          isOpen={true}
          onClose={() => setRollbackModal(null)}
          title={`Rollback Deployment #${rollbackModal.deployment.id}`}
        >
          <div className="space-y-4">
            <p className="text-sm text-slate-300">
              Select a previous model version to roll back to. Incoming real-time inferences will
              immediately switch to the selected target version.
            </p>

            {rollbackModal.versions.length === 0 ? (
              <p className="text-sm text-amber-400 bg-amber-950/40 border border-amber-800 p-3 rounded">
                No alternative versions available for this model to roll back to.
              </p>
            ) : (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Target Version
                </label>
                <select
                  value={rollbackModal.selectedVersionId || ''}
                  onChange={(e) =>
                    setRollbackModal({
                      ...rollbackModal,
                      selectedVersionId: Number(e.target.value),
                    })
                  }
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                >
                  {rollbackModal.versions.map((ver) => (
                    <option key={ver.id} value={ver.id}>
                      Version {ver.version_number} (v{ver.version_number}) — {ver.status}
                      {ver.changelog ? ` — ${ver.changelog}` : ''}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
              <Button
                variant="secondary"
                onClick={() => setRollbackModal(null)}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                disabled={isRollingBack || rollbackModal.versions.length === 0}
                onClick={executeRollback}
              >
                {isRollingBack ? 'Rolling back...' : 'Confirm Rollback'}
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
