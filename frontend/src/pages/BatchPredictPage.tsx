import React, { useEffect, useState } from 'react';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { deploymentService } from '../services/deploymentService';
import { modelService } from '../services/modelService';
import { inferenceService } from '../services/inferenceService';
import { Deployment, Model, BatchJob } from '../types';

export const BatchPredictPage: React.FC = () => {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [modelsMap, setModelsMap] = useState<Record<number, Model>>({});
  const [selectedDepId, setSelectedDepId] = useState<number | null>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentJob, setCurrentJob] = useState<BatchJob | null>(null);
  const [pastJobs, setPastJobs] = useState<BatchJob[]>([]);
  const [error, setError] = useState<string | null>(null);

  const loadDeploymentsAndJobs = async () => {
    try {
      const [depList, modelList, jobsList] = await Promise.all([
        deploymentService.getDeployments(),
        modelService.getModels(),
        inferenceService.listBatchJobs(),
      ]);
      const active = depList.filter((d) => d.status === 'DEPLOYED');
      setDeployments(active);
      setPastJobs(jobsList);

      const map: Record<number, Model> = {};
      modelList.forEach((m) => {
        map[m.id] = m;
      });
      setModelsMap(map);

      if (active.length > 0 && selectedDepId === null) {
        setSelectedDepId(active[0].id);
      }
    } catch (err) {
      console.error('Failed to load batch console data:', err);
    }
  };

  useEffect(() => {
    loadDeploymentsAndJobs();
  }, []);

  // Poll active batch job
  useEffect(() => {
    if (!currentJob || currentJob.status === 'COMPLETED' || currentJob.status === 'FAILED') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updated = await inferenceService.getBatchJobStatus(currentJob.id);
        setCurrentJob(updated);
        if (updated.status === 'COMPLETED' || updated.status === 'FAILED') {
          // Refresh list of jobs
          const allJobs = await inferenceService.listBatchJobs();
          setPastJobs(allJobs);
        }
      } catch (err) {
        console.error('Failed to poll batch status:', err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [currentJob]);

  const handleSubmitBatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDepId) {
      setError('Please select an active deployment.');
      return;
    }
    if (!selectedFile) {
      setError('Please select a CSV file.');
      return;
    }
    if (!selectedFile.name.endsWith('.csv')) {
      setError('Only .csv files are supported for batch inference.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setCurrentJob(null);

    try {
      const job = await inferenceService.submitBatchJob(selectedDepId, selectedFile);
      setCurrentJob(job);
      setSelectedFile(null);
      // Reload jobs list
      const allJobs = await inferenceService.listBatchJobs();
      setPastJobs(allJobs);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Batch submission failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const downloadSampleIris = () => {
    const csvContent =
      'sepal_length,sepal_width,petal_length,petal_width\n5.1,3.5,1.4,0.2\n4.9,3.0,1.4,0.2\n6.2,3.4,5.4,2.3\n5.9,3.0,5.1,1.8\n';
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'sample_iris_batch.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <Badge variant="success">COMPLETED</Badge>;
      case 'FAILED':
        return <Badge variant="danger">FAILED</Badge>;
      case 'PROCESSING':
        return <Badge variant="warning">PROCESSING</Badge>;
      case 'PENDING':
        return <Badge variant="info">PENDING</Badge>;
      default:
        return <Badge variant="info">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Batch Prediction Console</h1>
        <p className="text-sm text-slate-400">
          Upload bulk dataset CSVs for high-throughput batch inference and automated result generation
        </p>
      </div>

      {error && (
        <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-sm px-4 py-3 rounded-lg flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-rose-400 hover:text-rose-200">
            ✕
          </button>
        </div>
      )}

      {/* Upload and Target Deployment Box */}
      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6 space-y-6">
        <form onSubmit={handleSubmitBatch} className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-slate-200 mb-1">
                Target Deployment
              </label>
              <select
                id="batch-deployment-select"
                value={selectedDepId || ''}
                onChange={(e) => setSelectedDepId(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
              >
                {deployments.map((d) => {
                  const model = modelsMap[d.model_id];
                  return (
                    <option key={d.id} value={d.id}>
                      #{d.id} — {model ? model.display_name : `Model ${d.model_id}`} (v{d.current_version_id})
                    </option>
                  );
                })}
              </select>
            </div>

            <div className="flex items-end justify-start md:justify-end">
              <button
                type="button"
                onClick={downloadSampleIris}
                className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-2 rounded-lg border border-slate-600 transition-colors"
              >
                Download Sample Iris CSV
              </button>
            </div>
          </div>

          {/* File Upload Drop Area */}
          <div className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center bg-slate-900/50 hover:border-slate-500 transition-colors">
            <input
              id="batch-csv-input"
              type="file"
              accept=".csv"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="hidden"
            />
            <label
              htmlFor="batch-csv-input"
              className="cursor-pointer flex flex-col items-center justify-center space-y-2"
            >
              <div className="w-12 h-12 rounded-full bg-blue-900/40 text-blue-400 flex items-center justify-center font-bold text-xl">
                CSV
              </div>
              <p className="text-sm font-medium text-slate-200">
                {selectedFile ? (
                  <span className="text-emerald-400 font-bold">{selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                ) : (
                  'Click to select or drag & drop CSV file'
                )}
              </p>
              <p className="text-xs text-slate-500">
                Header columns must match the model's required feature schema
              </p>
            </label>
          </div>

          <Button
            id="batch-submit-btn"
            type="submit"
            disabled={isSubmitting || !selectedFile}
            className="w-full flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Submitting Batch Job...
              </>
            ) : (
              'Submit Batch Job'
            )}
          </Button>
        </form>
      </div>

      {/* Active Job Progress */}
      {currentJob && (
        <div className="bg-slate-800/90 border border-slate-700 rounded-xl p-6 space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-bold text-slate-100">
                Batch Job #{currentJob.id}
              </h2>
              {getStatusBadge(currentJob.status)}
            </div>
            {currentJob.status === 'COMPLETED' && currentJob.output_file_url && (
              <a
                href={inferenceService.downloadBatchResultsUrl(currentJob.id)}
                download
                className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-colors inline-flex items-center gap-2 shadow"
              >
                Download Results CSV &darr;
              </a>
            )}
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
            <div className="bg-slate-900 p-3 rounded border border-slate-700/60">
              <span className="text-slate-500 block">Total Records</span>
              <span className="text-base text-slate-200 font-bold">{currentJob.total_records}</span>
            </div>
            <div className="bg-slate-900 p-3 rounded border border-slate-700/60">
              <span className="text-slate-500 block">Processed Records</span>
              <span className="text-base text-blue-400 font-bold">{currentJob.processed_records}</span>
            </div>
            <div className="bg-slate-900 p-3 rounded border border-slate-700/60">
              <span className="text-slate-500 block">Created At</span>
              <span className="text-slate-300">{new Date(currentJob.created_at).toLocaleTimeString()}</span>
            </div>
            <div className="bg-slate-900 p-3 rounded border border-slate-700/60">
              <span className="text-slate-500 block">Completed At</span>
              <span className="text-slate-300">
                {currentJob.completed_at ? new Date(currentJob.completed_at).toLocaleTimeString() : 'In Progress...'}
              </span>
            </div>
          </div>

          {currentJob.error_message && (
            <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-xs p-3 rounded font-mono">
              <strong>Failure reason:</strong> {currentJob.error_message}
            </div>
          )}
        </div>
      )}

      {/* Past Batch Jobs History */}
      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">Batch Execution History</h2>

        {pastJobs.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-sm">
            No batch jobs executed yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-slate-900/50 text-slate-400">
                <tr>
                  <th className="px-4 py-3">Job ID</th>
                  <th className="px-4 py-3">Deployment</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Records</th>
                  <th className="px-4 py-3">Submitted At</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50 font-mono text-xs">
                {pastJobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-750/30">
                    <td className="px-4 py-3 text-slate-200 font-bold">#{job.id}</td>
                    <td className="px-4 py-3 text-slate-300">Dep #{job.deployment_id} (v{job.model_version_id})</td>
                    <td className="px-4 py-3">{getStatusBadge(job.status)}</td>
                    <td className="px-4 py-3">
                      {job.processed_records} / {job.total_records}
                    </td>
                    <td className="px-4 py-3 text-slate-400">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right font-sans">
                      {job.status === 'COMPLETED' && job.output_file_url ? (
                        <a
                          href={inferenceService.downloadBatchResultsUrl(job.id)}
                          download
                          className="text-xs bg-slate-700 hover:bg-slate-600 text-emerald-300 px-2.5 py-1 rounded transition-colors inline-block"
                        >
                          Download CSV
                        </a>
                      ) : (
                        <span className="text-slate-500 text-xs">
                          {job.status === 'FAILED' ? 'Failed' : 'Processing'}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
