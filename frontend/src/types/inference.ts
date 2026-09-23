export interface PredictionRequest {
  features: Record<string, any>;
}

export interface PredictionResponse {
  prediction: any;
  probabilities?: number[];
  model_version: number;
  latency_ms: number;
  timestamp: string;
}

export interface PredictionLog {
  id: number;
  deployment_id: number;
  model_version_id: number;
  input_features: Record<string, any>;
  prediction_output: any;
  latency_ms: number;
  status_code: number;
  error_message?: string;
  client_ip?: string;
  created_at: string;
}

export type BatchStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export interface BatchJob {
  id: number;
  deployment_id: number;
  model_version_id: number;
  input_file_url: string;
  output_file_url?: string;
  total_records: number;
  processed_records: number;
  status: BatchStatus;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}
