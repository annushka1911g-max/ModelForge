import { apiClient } from './apiClient';
import { PredictionRequest, PredictionResponse, PredictionLog, BatchJob } from '../types';

export const inferenceService = {
  predict: async (_deploymentId: number, _request: PredictionRequest): Promise<PredictionResponse> => {
    throw new Error('inferenceService.predict not yet implemented');
  },
  getLogs: async (_deploymentId: number): Promise<PredictionLog[]> => {
    throw new Error('inferenceService.getLogs not yet implemented');
  },
  submitBatchJob: async (_deploymentId: number, _formData: FormData): Promise<BatchJob> => {
    throw new Error('inferenceService.submitBatchJob not yet implemented');
  },
  getBatchJobStatus: async (_jobId: number): Promise<BatchJob> => {
    throw new Error('inferenceService.getBatchJobStatus not yet implemented');
  },
};
