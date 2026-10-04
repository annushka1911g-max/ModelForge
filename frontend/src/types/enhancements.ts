/**
 * Type definitions for ModelForge enhancements:
 * Experiments, Audit Logs, API Keys, Notifications, Search, System Health, and Drift.
 */

export interface Experiment {
  id: number;
  name: string;
  description?: string;
  model_id?: number;
  parameters?: Record<string, any>;
  metrics?: Record<string, any>;
  dataset_name?: string;
  dataset_version?: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  created_by?: number;
  created_at: string;
  completed_at?: string;
}

export interface ExperimentComparison {
  experiments: Experiment[];
  parameter_keys: string[];
  metric_keys: string[];
}

export interface AuditLog {
  id: number;
  user_id?: number;
  user_email?: string;
  action: string;
  resource: string;
  resource_id?: string;
  client_ip?: string;
  event_metadata?: Record<string, any>;
  timestamp: string;
}

export interface ApiKey {
  id: number;
  name: string;
  key_prefix: string;
  is_active: boolean;
  created_at: string;
  last_used_at?: string;
  expires_at?: string;
}

export interface ApiKeyCreated extends ApiKey {
  key: string;
}

export interface NotificationItem {
  id: number;
  title: string;
  message: string;
  notification_type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';
  is_read: boolean;
  link?: string;
  created_at: string;
}

export interface SearchItem {
  id: number | string;
  title: string;
  subtitle: string;
  type: 'model' | 'deployment' | 'experiment';
  url: string;
}

export interface GlobalSearchResults {
  models: SearchItem[];
  deployments: SearchItem[];
  experiments: SearchItem[];
}

export interface SystemHealthState {
  status: 'healthy' | 'degraded' | 'error';
  app?: string;
  environment?: string;
  services: {
    api?: { status: string; details?: string };
    database?: { status: string; version?: string };
    storage?: { status: string; type?: string };
    inference_engine?: { status: string; cached_models?: number };
  };
}

export interface DashboardAnalytics {
  stats: {
    total_models: number;
    active_deployments: number;
    total_deployments: number;
    total_predictions: number;
    successful_predictions: number;
    failed_predictions: number;
    avg_latency_ms: number;
    total_batch_jobs: number;
    completed_batch_jobs: number;
    failed_batch_jobs: number;
  };
  charts: {
    predictions_over_time: Array<{
      date: string;
      label: string;
      total: number;
      successful: number;
      failed: number;
      avg_latency: number;
    }>;
    model_usage: Array<{
      name: string;
      predictions: number;
    }>;
    deployment_activity: {
      active: number;
      stopped: number;
      total: number;
    };
    latency_distribution: {
      p50: number;
      p90: number;
      p95: number;
      p99: number;
      min: number;
      max: number;
    };
  };
  system_health: SystemHealthState;
  recent_models: any[];
  recent_deployments: any[];
}

export interface PerformanceAnalytics {
  time_range: string;
  total_inferences: number;
  successful_inferences: number;
  failed_inferences: number;
  failure_rate: number;
  avg_latency_ms: number;
  p50_latency_ms: number;
  p90_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;
  min_latency_ms: number;
  max_latency_ms: number;
  hourly_throughput: Array<{
    hour: string;
    total: number;
    successful: number;
    failed: number;
    avg_latency: number;
  }>;
  status_breakdown: Record<string, number>;
}

export interface CsvValidationResult {
  valid: boolean;
  total_rows: number;
  columns_found: string[];
  missing_columns: string[];
  extra_columns: string[];
  errors: string[];
  preview: Array<Record<string, any>>;
}

export interface FeatureImportanceData {
  deployment_id: number;
  framework: string;
  feature_importances: Record<string, number>;
}

export interface DriftMetricsData {
  deployment_id: number;
  total_inferences: number;
  feature_drift: Record<string, {
    mean: number;
    std: number;
    min: number;
    max: number;
    count: number;
  }>;
  target_distribution: Record<string, number>;
}
