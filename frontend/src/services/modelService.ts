import { apiClient } from './apiClient';
import { Model, ModelVersion } from '../types';

export const modelService = {
  getModels: async (): Promise<Model[]> => {
    throw new Error('modelService.getModels not yet implemented');
  },
  getModelById: async (_id: number): Promise<Model> => {
    throw new Error('modelService.getModelById not yet implemented');
  },
  createModel: async (_data: Partial<Model>): Promise<Model> => {
    throw new Error('modelService.createModel not yet implemented');
  },
  uploadVersion: async (_modelId: number, _formData: FormData): Promise<ModelVersion> => {
    throw new Error('modelService.uploadVersion not yet implemented');
  },
};
