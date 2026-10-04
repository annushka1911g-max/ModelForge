import { apiClient } from './apiClient';
import { Deployment } from '../types';

export const deploymentService = {
  getDeployments: async (): Promise<Deployment[]> => {
    const response = await apiClient.get<Deployment[]>('/deployments/');
    return response.data;
  },

  getDeployment: async (id: number): Promise<Deployment> => {
    const response = await apiClient.get<Deployment>(`/deployments/${id}`);
    return response.data;
  },

  deployVersion: async (modelId: number, versionId: number): Promise<Deployment> => {
    const response = await apiClient.post<Deployment>('/deployments/', {
      model_id: modelId,
      current_version_id: versionId,
    });
    return response.data;
  },

  stopDeployment: async (deploymentId: number): Promise<Deployment> => {
    const response = await apiClient.post<Deployment>(`/deployments/${deploymentId}/stop`);
    return response.data;
  },

  restartDeployment: async (deploymentId: number): Promise<Deployment> => {
    const response = await apiClient.post<Deployment>(`/deployments/${deploymentId}/restart`);
    return response.data;
  },

  rollbackDeployment: async (deploymentId: number, targetVersionId?: number): Promise<Deployment> => {
    const response = await apiClient.post<Deployment>(`/deployments/${deploymentId}/rollback`, {
      target_version_id: targetVersionId ?? null,
    });
    return response.data;
  },

  getDeploymentHealth: async (deploymentId: number): Promise<any> => {
    const response = await apiClient.get(`/deployments/${deploymentId}/health`);
    return response.data;
  },
};
