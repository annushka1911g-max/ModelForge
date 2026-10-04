import { apiClient } from './apiClient';
import {
  AuditLog,
  ApiKey,
  ApiKeyCreated,
  NotificationItem,
  GlobalSearchResults,
  DashboardAnalytics,
  PerformanceAnalytics,
  Experiment,
  ExperimentComparison,
  CsvValidationResult,
  FeatureImportanceData,
  DriftMetricsData,
  SystemHealthState,
} from '../types';

export const platformService = {
  // ── System Health & Monitoring ─────────────────────────────────────────────
  async getSystemHealth(): Promise<SystemHealthState> {
    const res = await apiClient.get<SystemHealthState>('/monitoring/health');
    return res.data;
  },

  async getDashboardAnalytics(): Promise<DashboardAnalytics> {
    const res = await apiClient.get<DashboardAnalytics>('/monitoring/dashboard-analytics');
    return res.data;
  },

  async getPerformanceAnalytics(timeRange: string = '24h', modelId?: number): Promise<PerformanceAnalytics> {
    const params: Record<string, any> = { time_range: timeRange };
    if (modelId) params.model_id = modelId;
    const res = await apiClient.get<PerformanceAnalytics>('/monitoring/performance', { params });
    return res.data;
  },

  // ── Global Search ──────────────────────────────────────────────────────────
  async search(query: string): Promise<GlobalSearchResults> {
    const res = await apiClient.get<GlobalSearchResults>('/search/', { params: { q: query } });
    return res.data;
  },

  // ── Audit Logs ─────────────────────────────────────────────────────────────
  async listAuditLogs(params?: {
    skip?: number;
    limit?: number;
    action?: string;
    resource?: string;
    user_email?: string;
  }): Promise<AuditLog[]> {
    const res = await apiClient.get<AuditLog[]>('/audit-logs/', { params });
    return res.data;
  },

  // ── API Keys ───────────────────────────────────────────────────────────────
  async listApiKeys(): Promise<ApiKey[]> {
    const res = await apiClient.get<ApiKey[]>('/api-keys/');
    return res.data;
  },

  async createApiKey(name: string): Promise<ApiKeyCreated> {
    const res = await apiClient.post<ApiKeyCreated>('/api-keys/', { name });
    return res.data;
  },

  async revokeApiKey(id: number): Promise<ApiKey> {
    const res = await apiClient.delete<ApiKey>(`/api-keys/${id}`);
    return res.data;
  },

  // ── Notifications ──────────────────────────────────────────────────────────
  async listNotifications(unreadOnly: boolean = false): Promise<NotificationItem[]> {
    const res = await apiClient.get<NotificationItem[]>('/notifications/', {
      params: { unread_only: unreadOnly },
    });
    return res.data;
  },

  async getUnreadNotificationCount(): Promise<number> {
    const res = await apiClient.get<{ unread_count: number }>('/notifications/unread-count');
    return res.data.unread_count;
  },

  async markNotificationRead(id: number): Promise<void> {
    await apiClient.post(`/notifications/${id}/read`);
  },

  async markAllNotificationsRead(): Promise<void> {
    await apiClient.post('/notifications/read-all');
  },

  // ── Experiment Tracking ────────────────────────────────────────────────────
  async listExperiments(params?: {
    skip?: number;
    limit?: number;
    model_id?: number;
    status?: string;
    search?: string;
  }): Promise<Experiment[]> {
    const res = await apiClient.get<Experiment[]>('/experiments/', { params });
    return res.data;
  },

  async createExperiment(data: {
    name: string;
    description?: string;
    model_id?: number;
    parameters?: Record<string, any>;
    metrics?: Record<string, any>;
    dataset_name?: string;
    dataset_version?: string;
    status?: string;
  }): Promise<Experiment> {
    const res = await apiClient.post<Experiment>('/experiments/', data);
    return res.data;
  },

  async compareExperiments(ids: number[]): Promise<ExperimentComparison> {
    const res = await apiClient.get<ExperimentComparison>('/experiments/compare', {
      params: { ids: ids.join(',') },
    });
    return res.data;
  },

  // ── Model Enhancements (Tags, Favorite, Version Comparison) ───────────────
  async toggleModelFavorite(modelId: number): Promise<{ is_starred: boolean }> {
    const res = await apiClient.post<{ id: number; is_starred: boolean }>(`/models/${modelId}/favorite`);
    return res.data;
  },

  async addModelTag(modelId: number, tag: string): Promise<string[]> {
    const res = await apiClient.post<{ id: number; tags: string[] }>(`/models/${modelId}/tags`, { tag });
    return res.data.tags;
  },

  async removeModelTag(modelId: number, tag: string): Promise<string[]> {
    const res = await apiClient.delete<{ id: number; tags: string[] }>(`/models/${modelId}/tags/${encodeURIComponent(tag)}`);
    return res.data.tags;
  },

  async compareModelVersions(modelId: number, v1: number, v2: number): Promise<any> {
    const res = await apiClient.get(`/models/${modelId}/versions/compare`, {
      params: { v1, v2 },
    });
    return res.data;
  },

  // ── Batch Validation ───────────────────────────────────────────────────────
  async validateBatchCsv(deploymentId: number, file: File): Promise<CsvValidationResult> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<CsvValidationResult>(
      `/batch/${deploymentId}/validate-csv`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return res.data;
  },

  // ── Inference & Drift & Explainability ─────────────────────────────────────
  async getFeatureImportance(deploymentId: number): Promise<FeatureImportanceData> {
    const res = await apiClient.get<FeatureImportanceData>(`/deployments/${deploymentId}/feature-importance`);
    return res.data;
  },

  async getDriftMetrics(deploymentId: number): Promise<DriftMetricsData> {
    const res = await apiClient.get<DriftMetricsData>(`/deployments/${deploymentId}/drift`);
    return res.data;
  },

  async getAllPredictionLogs(params?: {
    skip?: number;
    limit?: number;
    deployment_id?: number;
  }): Promise<any[]> {
    const res = await apiClient.get<any[]>('/deployments/predictions/all', { params });
    return res.data;
  },

  // ── Deployment Center Enhancements ─────────────────────────────────────────
  async getDeploymentHistory(deploymentId: number): Promise<any[]> {
    const res = await apiClient.get<any[]>(`/deployments/${deploymentId}/history`);
    return res.data;
  },

  async getDeploymentHealthMetrics(deploymentId: number): Promise<any> {
    const res = await apiClient.get<any>(`/deployments/${deploymentId}/health-metrics`);
    return res.data;
  },
};
