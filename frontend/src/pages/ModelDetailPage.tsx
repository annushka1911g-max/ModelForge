import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { modelService } from '../services/modelService';
import { deploymentService } from '../services/deploymentService';
import { useAuth } from '../authentication/useAuth';
import { Model, ModelVersion } from '../types';

export const ModelDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const modelId = Number(id);

  const [model, setModel] = useState<Model | null>(null);
  const [versions, setVersions] = useState<ModelVersion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Schema Inspection Modal
  const [selectedSchema, setSelectedSchema] = useState<any | null>(null);

  // Upload Version Modal
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [artifactFile, setArtifactFile] = useState<File | null>(null);
  const [featureSchemaText, setFeatureSchemaText] = useState(
    JSON.stringify(
      {
        features: [
          { name: 'sepal_length', type: 'float' },
          { name: 'sepal_width', type: 'float' },
          { name: 'petal_length', type: 'float' },
          { name: 'petal_width', type: 'float' },
        ],
      },
      null,
      2
    )
  );
  const [trainingMetricsText, setTrainingMetricsText] = useState(
    JSON.stringify({ accuracy: 0.96, precision: 0.95, recall: 0.96, f1_score: 0.95 }, null, 2)
  );
  const [changelog, setChangelog] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const { hasRole } = useAuth();
  const navigate = useNavigate();
  const canManage = hasRole(['ADMIN', 'ML_ENGINEER']);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [m, v] = await Promise.all([
        modelService.getModelById(modelId),
        modelService.getVersions(modelId),
      ]);
      setModel(m);
      setVersions(v);
    } catch (err: any) {
      setError('Failed to load model details.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!isNaN(modelId)) {
      loadData();
    }
  }, [modelId]);

  const handleUploadVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!artifactFile) {
      setUploadError('Please select a model artifact file.');
      return;
    }

    try {
      JSON.parse(featureSchemaText);
    } catch {
      setUploadError('Feature schema must be valid JSON.');
      return;
    }

    if (trainingMetricsText.trim()) {
      try {
        JSON.parse(trainingMetricsText);
      } catch {
        setUploadError('Training metrics must be valid JSON.');
        return;
      }
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append('file', artifactFile);
      formData.append('feature_schema', featureSchemaText);
      if (trainingMetricsText.trim()) {
        formData.append('training_metrics', trainingMetricsText);
      }
      if (changelog.trim()) {
        formData.append('changelog', changelog);
      }

      await modelService.uploadVersion(modelId, formData);
      setIsUploadOpen(false);
      setArtifactFile(null);
      setChangelog('');
      setActionSuccess('New version uploaded successfully.');
      await loadData();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setUploadError(typeof detail === 'string' ? detail : 'Failed to upload version.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeploy = async (versionId: number) => {
    try {
      await deploymentService.deployVersion(modelId, versionId);
      navigate('/deployments');
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to deploy version.');
    }
  };

  if (isLoading) {
    return (
      <div className="py-20 text-center text-slate-400">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        Loading model details...
      </div>
    );
  }

  if (error || !model) {
    return (
      <div className="space-y-4">
        <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-sm px-4 py-3 rounded-lg">
          {error || 'Model not found.'}
        </div>
        <Link to="/models" className="text-blue-400 text-sm hover:underline">
          &larr; Back to Models
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <Link to="/models" className="text-slate-400 hover:text-slate-200 text-sm">
              Models
            </Link>
            <span className="text-slate-600">/</span>
            <h1 className="text-2xl font-bold text-slate-100">{model.display_name}</h1>
            <span className="text-xs font-mono bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
              {model.framework}
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Task: <span className="text-slate-200">{model.task_type}</span> | Identifier:{' '}
            <span className="font-mono text-slate-300">{model.name}</span>
          </p>
        </div>

        {canManage && (
          <div className="flex gap-3">
            <Button
              variant="secondary"
              id="btn-upload-version"
              onClick={() => setIsUploadOpen(true)}
            >
              + Upload Version
            </Button>
          </div>
        )}
      </div>

      {actionSuccess && (
        <div className="bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm px-4 py-3 rounded-lg flex justify-between items-center">
          <span>{actionSuccess}</span>
          <button
            onClick={() => setActionSuccess(null)}
            className="text-emerald-400 hover:text-emerald-200 text-xs"
          >
            ✕
          </button>
        </div>
      )}

      {/* Model Description */}
      {model.description && (
        <div className="bg-slate-800/50 border border-slate-700/60 rounded-xl p-4 text-sm text-slate-300">
          {model.description}
        </div>
      )}

      {/* Version History Table */}
      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">Version History & Lineage</h2>

        {versions.length === 0 ? (
          <div className="text-center py-8 text-slate-400 text-sm">
            No versions uploaded yet. Upload a model binary artifact to deploy.
          </div>
        ) : (
          <div className="space-y-4">
            {versions.map((ver) => (
              <div
                key={ver.id}
                className="p-5 bg-slate-900/70 border border-slate-700/70 rounded-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:border-slate-600 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-base text-slate-100">
                      Version {ver.version_number} (v{ver.version_number})
                    </span>
                    <Badge variant={ver.status === 'READY' ? 'success' : 'warning'}>
                      {ver.status}
                    </Badge>
                  </div>
                  <div className="text-xs text-slate-400 font-mono flex flex-wrap gap-x-4 gap-y-1">
                    <span>Artifact: {ver.artifact_path}</span>
                    <span>Size: {(ver.file_size_bytes / 1024).toFixed(1)} KB</span>
                    <span>SHA256: {ver.file_hash.substring(0, 16)}...</span>
                  </div>
                  {ver.changelog && (
                    <p className="text-xs text-slate-300 italic mt-1">"{ver.changelog}"</p>
                  )}
                  {ver.training_metrics && (
                    <div className="text-xs text-blue-400 flex flex-wrap gap-3 mt-1">
                      {Object.entries(ver.training_metrics).map(([k, val]: any) => (
                        <span key={k}>
                          {k}: {typeof val === 'number' ? val.toFixed(3) : val}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 self-end md:self-center">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => setSelectedSchema(ver.feature_schema)}
                  >
                    View Schema
                  </Button>
                  {canManage && ver.status === 'READY' && (
                    <Button size="sm" onClick={() => handleDeploy(ver.id)}>
                      Deploy v{ver.version_number}
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Inspect Schema Modal */}
      <Modal
        isOpen={!!selectedSchema}
        onClose={() => setSelectedSchema(null)}
        title="Model Feature Schema"
      >
        <div className="space-y-3">
          <p className="text-xs text-slate-400">
            Expected JSON feature input required for real-time and batch predictions:
          </p>
          <pre className="bg-slate-900 border border-slate-700 rounded-lg p-4 font-mono text-xs text-emerald-400 overflow-auto max-h-80">
            {JSON.stringify(selectedSchema, null, 2)}
          </pre>
          <div className="flex justify-end pt-2">
            <Button variant="secondary" onClick={() => setSelectedSchema(null)}>
              Close
            </Button>
          </div>
        </div>
      </Modal>

      {/* Upload Version Modal */}
      <Modal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        title={`Upload Artifact — ${model.display_name}`}
      >
        <form onSubmit={handleUploadVersion} className="space-y-4">
          {uploadError && (
            <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-xs px-3 py-2 rounded">
              {uploadError}
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Model Artifact Binary File *
            </label>
            <input
              type="file"
              onChange={(e) => setArtifactFile(e.target.files?.[0] || null)}
              className="w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer"
              required
            />
            <p className="text-xs text-slate-500 mt-1">
              Accepts .pkl, .joblib, .json, .pt, or model binaries
            </p>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Feature Schema (JSON) *
            </label>
            <textarea
              value={featureSchemaText}
              onChange={(e) => setFeatureSchemaText(e.target.value)}
              rows={6}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 font-mono text-xs text-slate-200 focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Training Metrics (JSON, optional)
            </label>
            <textarea
              value={trainingMetricsText}
              onChange={(e) => setTrainingMetricsText(e.target.value)}
              rows={3}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 font-mono text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Changelog / Version Notes
            </label>
            <input
              type="text"
              value={changelog}
              onChange={(e) => setChangelog(e.target.value)}
              placeholder="e.g. Retrained with updated hyperparams"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsUploadOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isUploading}>
              {isUploading ? 'Uploading...' : 'Upload & Register Version'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
