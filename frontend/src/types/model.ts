export type MLFramework = 'SCIKIT_LEARN' | 'XGBOOST' | 'TENSORFLOW' | 'PYTORCH';
export type TaskType = 'CLASSIFICATION' | 'REGRESSION';
export type VersionStatus = 'READY' | 'FAILED' | 'ARCHIVED';

export interface FeatureSchemaItem {
  name: string;
  type: string; // 'float' | 'int' | 'string'
  required: boolean;
  description?: string;
}

export interface ModelVersion {
  id: number;
  model_id: number;
  version_number: number;
  artifact_path: string;
  file_hash: string;
  file_size_bytes: number;
  feature_schema: FeatureSchemaItem[];
  target_schema?: Record<string, any>;
  training_metrics?: Record<string, any>;
  status: VersionStatus;
  changelog?: string;
  created_at: string;
}

export interface Model {
  id: number;
  name: string;
  display_name: string;
  description?: string;
  framework: MLFramework;
  task_type: TaskType;
  created_by?: number;
  tags?: string[];
  is_starred?: boolean;
  created_at: string;
  updated_at: string;
  versions?: ModelVersion[];
}
