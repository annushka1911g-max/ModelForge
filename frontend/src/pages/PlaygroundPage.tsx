import React, { useEffect, useState } from 'react';
import { Button } from '../components/common/Button';
import { deploymentService } from '../services/deploymentService';
import { modelService } from '../services/modelService';
import { inferenceService } from '../services/inferenceService';
import { Deployment, Model, PredictionResponse } from '../types';

export const PlaygroundPage: React.FC = () => {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [modelsMap, setModelsMap] = useState<Record<number, Model>>({});
  const [selectedDepId, setSelectedDepId] = useState<number | null>(null);

  const [inputJson, setInputJson] = useState<string>(
    JSON.stringify(
      {
        features: {
          sepal_length: 5.1,
          sepal_width: 3.5,
          petal_length: 1.4,
          petal_width: 0.2,
        },
      },
      null,
      2
    )
  );

  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDeployments = async () => {
      try {
        const [depList, modelList] = await Promise.all([
          deploymentService.getDeployments(),
          modelService.getModels(),
        ]);
        const active = depList.filter((d) => d.status === 'DEPLOYED');
        setDeployments(active);

        const map: Record<number, Model> = {};
        modelList.forEach((m) => {
          map[m.id] = m;
        });
        setModelsMap(map);

        if (active.length > 0 && selectedDepId === null) {
          setSelectedDepId(active[0].id);
        }
      } catch (err) {
        console.error('Failed to load deployments for playground:', err);
      }
    };

    fetchDeployments();
  }, []);

  const handleSelectDeployment = async (depId: number) => {
    setSelectedDepId(depId);
    setError(null);
    setResponse(null);

    const dep = deployments.find((d) => d.id === depId);
    if (!dep) return;

    try {
      const versions = await modelService.getVersions(dep.model_id);
      const currentVer = versions.find((v) => v.id === dep.current_version_id);
      if (currentVer && currentVer.feature_schema) {
        const sampleFeatures: Record<string, any> = {};
        const schemaList = Array.isArray(currentVer.feature_schema)
          ? currentVer.feature_schema
          : (currentVer.feature_schema as any)?.features || [];

        schemaList.forEach((f: any) => {
          if (f.name === 'sepal_length') sampleFeatures[f.name] = 5.1;
          else if (f.name === 'sepal_width') sampleFeatures[f.name] = 3.5;
          else if (f.name === 'petal_length') sampleFeatures[f.name] = 1.4;
          else if (f.name === 'petal_width') sampleFeatures[f.name] = 0.2;
          else if (f.type === 'float') sampleFeatures[f.name] = 1.0;
          else if (f.type === 'int') sampleFeatures[f.name] = 1;
          else if (f.type === 'bool') sampleFeatures[f.name] = true;
          else sampleFeatures[f.name] = 'sample';
        });

        if (Object.keys(sampleFeatures).length > 0) {
          setInputJson(JSON.stringify({ features: sampleFeatures }, null, 2));
        }
      }
    } catch (err) {
      console.warn('Could not auto-generate feature sample:', err);
    }
  };

  const handlePredict = async () => {
    if (!selectedDepId) {
      setError('Please select an active deployment.');
      return;
    }

    let payload: any;
    try {
      payload = JSON.parse(inputJson);
    } catch {
      setError('Invalid JSON syntax in input features.');
      return;
    }

    // Support both { features: { ... } } and raw { ... }
    const features = payload.features || payload;
    if (!features || typeof features !== 'object' || Array.isArray(features)) {
      setError('JSON must include an object of feature key-value pairs.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await inferenceService.predict(selectedDepId, { features });
      setResponse(res);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
          ? detail.map((d: any) => d.message || d.msg).join(', ')
          : 'Prediction request failed.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const setSampleIris = () => {
    setInputJson(
      JSON.stringify(
        {
          features: {
            sepal_length: 5.1,
            sepal_width: 3.5,
            petal_length: 1.4,
            petal_width: 0.2,
          },
        },
        null,
        2
      )
    );
    setError(null);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Inference Playground</h1>
        <p className="text-sm text-slate-400">
          Interactively test live model deployments with custom feature vectors
        </p>
      </div>

      {deployments.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-400">
          No active deployments found. Deploy a model version from the{' '}
          <a href="/models" className="text-blue-400 underline">
            Models
          </a>{' '}
          page first.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Request Inputs */}
          <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6 space-y-4">
            <div className="flex justify-between items-center">
              <label className="text-sm font-semibold text-slate-200">
                Target Deployment
              </label>
              <button
                type="button"
                onClick={setSampleIris}
                className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
              >
                Load Iris Sample
              </button>
            </div>

            <select
              id="playground-deployment-select"
              value={selectedDepId || ''}
              onChange={(e) => handleSelectDeployment(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
            >
              {deployments.map((d) => {
                const model = modelsMap[d.model_id];
                return (
                  <option key={d.id} value={d.id}>
                    #{d.id} — {model ? model.display_name : `Model ${d.model_id}`} (v{d.current_version_id}) — {d.endpoint_path}
                  </option>
                );
              })}
            </select>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-sm font-semibold text-slate-200">
                  Input Features (JSON)
                </label>
                <span className="text-xs text-slate-500 font-mono">POST /predict</span>
              </div>
              <textarea
                id="playground-input-json"
                value={inputJson}
                onChange={(e) => setInputJson(e.target.value)}
                rows={12}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 font-mono text-sm text-slate-100 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <Button
              id="playground-run-btn"
              onClick={handlePredict}
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Executing Inference...
                </>
              ) : (
                'Run Prediction'
              )}
            </Button>
          </div>

          {/* Right Column: Prediction Output */}
          <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6 space-y-4 flex flex-col">
            <h2 className="text-sm font-semibold text-slate-200">Prediction Response</h2>

            {error && (
              <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-sm px-4 py-3 rounded-lg space-y-1">
                <div className="font-semibold text-rose-400">Prediction Error:</div>
                <div className="text-xs font-mono">{error}</div>
              </div>
            )}

            {response ? (
              <div className="space-y-4 flex-1 flex flex-col">
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="bg-slate-900 border border-slate-700/80 rounded-lg p-3">
                    <span className="text-xs text-slate-400">Predicted Class / Value</span>
                    <p className="text-xl font-bold text-emerald-400 font-mono mt-1">
                      {JSON.stringify(response.prediction)}
                    </p>
                  </div>
                  <div className="bg-slate-900 border border-slate-700/80 rounded-lg p-3">
                    <span className="text-xs text-slate-400">Latency</span>
                    <p className="text-xl font-bold text-blue-400 font-mono mt-1">
                      {response.latency_ms} ms
                    </p>
                  </div>
                  <div className="bg-slate-900 border border-slate-700/80 rounded-lg p-3 col-span-2 sm:col-span-1">
                    <span className="text-xs text-slate-400">Model Version</span>
                    <p className="text-xl font-bold text-slate-200 font-mono mt-1">
                      v{response.model_version}
                    </p>
                  </div>
                </div>

                {response.probabilities && (
                  <div className="bg-slate-900 border border-slate-700/80 rounded-lg p-3">
                    <span className="text-xs text-slate-400 block mb-2">Class Probabilities</span>
                    <div className="space-y-1.5 font-mono text-xs text-slate-300">
                      {Array.isArray(response.probabilities) &&
                        response.probabilities.map((prob: number, idx: number) => (
                          <div key={idx} className="flex justify-between items-center">
                            <span>Class {idx}:</span>
                            <span className="text-emerald-400 font-semibold">
                              {(prob * 100).toFixed(2)}% ({prob})
                            </span>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                <div className="flex-1 flex flex-col">
                  <span className="text-xs text-slate-400 mb-1">Raw API Payload</span>
                  <div className="flex-1 bg-slate-900 border border-slate-700 rounded-lg p-3 font-mono text-xs text-emerald-300 overflow-auto max-h-56">
                    <pre>{JSON.stringify(response, null, 2)}</pre>
                  </div>
                </div>
              </div>
            ) : !error && (
              <div className="flex-1 flex items-center justify-center text-slate-500 text-sm border border-dashed border-slate-700 rounded-lg p-8">
                Click "Run Prediction" to execute inference on the selected model deployment.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
