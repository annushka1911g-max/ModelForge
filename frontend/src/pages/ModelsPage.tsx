import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { modelService } from '../services/modelService';
import { useAuth } from '../authentication/useAuth';
import { Model } from '../types';

export const ModelsPage: React.FC = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Register Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [description, setDescription] = useState('');
  const [framework, setFramework] = useState('SCIKIT_LEARN');
  const [taskType, setTaskType] = useState('CLASSIFICATION');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  const { hasRole } = useAuth();
  const navigate = useNavigate();
  const canManage = hasRole(['ADMIN', 'ML_ENGINEER']);

  const fetchModels = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await modelService.getModels();
      setModels(data);
    } catch (err: any) {
      setError('Failed to load registered models.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !displayName) {
      setModalError('Model identifier name and display name are required.');
      return;
    }

    setIsSubmitting(true);
    setModalError(null);

    try {
      const created = await modelService.createModel({
        name: name.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '-'),
        display_name: displayName.trim(),
        description: description.trim(),
        framework,
        task_type: taskType,
      });
      setIsModalOpen(false);
      setName('');
      setDisplayName('');
      setDescription('');
      navigate(`/models/${created.id}`);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setModalError(typeof detail === 'string' ? detail : 'Failed to register model.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Model Catalog</h1>
          <p className="text-sm text-slate-400">
            Registered machine learning models, framework bindings, and version lineages
          </p>
        </div>
        {canManage && (
          <Button id="btn-register-model" onClick={() => setIsModalOpen(true)}>
            + Register New Model
          </Button>
        )}
      </div>

      {error && (
        <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-sm px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="py-16 text-center text-slate-400">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          Loading model catalog...
        </div>
      ) : models.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center space-y-3">
          <p className="text-slate-300 font-medium">No models registered yet</p>
          <p className="text-sm text-slate-500 max-w-sm mx-auto">
            Get started by registering a model metadata definition, then upload trained model artifacts.
          </p>
          {canManage && (
            <Button onClick={() => setIsModalOpen(true)} className="mt-2">
              Register First Model
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {models.map((model) => (
            <div
              key={model.id}
              onClick={() => navigate(`/models/${model.id}`)}
              className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 hover:border-blue-500/50 hover:bg-slate-800 cursor-pointer transition-all flex flex-col justify-between group shadow-lg"
            >
              <div>
                <div className="flex justify-between items-start gap-2">
                  <h3 className="font-semibold text-slate-100 group-hover:text-blue-400 transition-colors">
                    {model.display_name}
                  </h3>
                  <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded font-mono uppercase">
                    {model.framework}
                  </span>
                </div>
                <div className="font-mono text-xs text-slate-500 mt-1">
                  {model.name}
                </div>
                <p className="text-sm text-slate-400 mt-3 line-clamp-2">
                  {model.description || 'No description provided.'}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-700/50 flex justify-between items-center text-xs text-slate-400">
                <span className="text-slate-400 font-medium">
                  {model.task_type}
                </span>
                <span className="text-blue-400 font-medium group-hover:underline">
                  Manage lineage &rarr;
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal: Register Model */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Register New Model"
      >
        <form onSubmit={handleRegister} className="space-y-4">
          {modalError && (
            <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-xs px-3 py-2 rounded">
              {modalError}
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Model Identifier Name (Slug) *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. iris-classifier"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
              required
            />
            <p className="text-xs text-slate-500 mt-1">Alphanumeric, hyphens, and underscores only</p>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Display Name *
            </label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="e.g. Iris Species Classifier"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Framework *
            </label>
            <select
              value={framework}
              onChange={(e) => setFramework(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
            >
              <option value="SCIKIT_LEARN">Scikit-Learn (.pkl, .joblib)</option>
              <option value="XGBOOST">XGBoost (.json, .model, .joblib)</option>
              <option value="PYTORCH">PyTorch (.pt, .pth)</option>
              <option value="TENSORFLOW">TensorFlow / Keras (.keras, SavedModel)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Task Type *
            </label>
            <select
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
            >
              <option value="CLASSIFICATION">Classification</option>
              <option value="REGRESSION">Regression</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="Model purpose, expected dataset, training context..."
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Registering...' : 'Register Model'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
