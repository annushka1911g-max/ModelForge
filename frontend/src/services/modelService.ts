import { apiClient } from './apiClient';
import { Model, ModelVersion } from '../types';

export const modelService = {
  getModels: async (skip: number = 0, limit: number = 100): Promise<Model[]> => {
    const response = await apiClient.get<Model[]>('/models/', {
      params: { skip, limit },
    });
    return response.data;
  },

  getModelById: async (id: number): Promise<Model> => {
    const response = await apiClient.get<Model>(`/models/${id}`);
    return response.data;
  },

  createModel: async (data: {
    name: string;
    display_name: string;
    description?: string;
    framework: string;
    task_type: string;
  }): Promise<Model> => {
    const response = await apiClient.post<Model>('/models/', data);
    return response.data;
  },

  updateModel: async (
    id: number,
    data: { display_name?: string; description?: string }
  ): Promise<Model> => {
    const response = await apiClient.patch<Model>(`/models/${id}`, data);
    return response.data;
  },

  getVersions: async (modelId: number): Promise<ModelVersion[]> => {
    const response = await apiClient.get<ModelVersion[]>(`/models/${modelId}/versions`);
    return response.data;
  },

  uploadVersion: async (modelId: number, formData: FormData): Promise<ModelVersion> => {
    const response = await apiClient.post<ModelVersion>(
      `/models/${modelId}/versions`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};
