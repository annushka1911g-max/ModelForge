import { apiClient } from './apiClient';
import { PredictionRequest, PredictionResponse, PredictionLog, BatchJob } from '../types';

export const inferenceService = {
  predict: async (deploymentId: number, request: PredictionRequest): Promise<PredictionResponse> => {
    const response = await apiClient.post<PredictionResponse>(
      `/deployments/${deploymentId}/predict`,
      request
    );
    return response.data;
  },

  getLogs: async (deploymentId: number, skip: number = 0, limit: number = 100): Promise<PredictionLog[]> => {
    const response = await apiClient.get<PredictionLog[]>(
      `/deployments/${deploymentId}/logs`,
      { params: { skip, limit } }
    );
    return response.data;
  },

  submitBatchJob: async (deploymentId: number, file: File): Promise<BatchJob> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<BatchJob>(
      `/batch/${deploymentId}/predict-batch`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  getBatchJobStatus: async (jobId: number): Promise<BatchJob> => {
    const response = await apiClient.get<BatchJob>(`/batch/jobs/${jobId}`);
    return response.data;
  },

  listBatchJobs: async (deploymentId?: number): Promise<BatchJob[]> => {
    const response = await apiClient.get<BatchJob[]>('/batch/jobs', {
      params: deploymentId ? { deployment_id: deploymentId } : undefined,
    });
    return response.data;
  },

  downloadBatchResultsUrl: (jobId: number): string => {
    const base = apiClient.defaults.baseURL || '/api/v1';
    return `${base}/batch/jobs/${jobId}/download`;
  },

  getMonitoringStats: async (): Promise<{
    total_models: number;
    total_deployments: number;
    active_deployments: number;
    total_predictions: number;
    successful_predictions: number;
    failed_predictions: number;
    avg_latency_ms: number;
    total_batch_jobs: number;
  }> => {
    const response = await apiClient.get('/monitoring/stats');
    return response.data;
  },

  getRecentLogs: async (limit: number = 50): Promise<any[]> => {
    const response = await apiClient.get('/monitoring/logs', {
      params: { limit },
    });
    return response.data;
  },
};
