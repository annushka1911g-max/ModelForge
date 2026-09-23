import { apiClient } from './apiClient';
import { Deployment } from '../types';

export const deploymentService = {
  getDeployments: async (): Promise<Deployment[]> => {
    throw new Error('deploymentService.getDeployments not yet implemented');
  },
  deployVersion: async (_modelId: number, _versionId: number): Promise<Deployment> => {
    throw new Error('deploymentService.deployVersion not yet implemented');
  },
  rollbackDeployment: async (_deploymentId: number): Promise<Deployment> => {
    throw new Error('deploymentService.rollbackDeployment not yet implemented');
  },
  stopDeployment: async (_deploymentId: number): Promise<Deployment> => {
    throw new Error('deploymentService.stopDeployment not yet implemented');
  },
};
