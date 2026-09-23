export type DeploymentStatus = 'DEPLOYED' | 'STOPPED' | 'FAILED' | 'ROLLING_BACK';

export interface Deployment {
  id: number;
  model_id: number;
  current_version_id: number;
  previous_version_id?: number;
  status: DeploymentStatus;
  endpoint_path: string;
  deployed_by?: number;
  deployed_at: string;
  last_rollback_at?: string;
  updated_at: string;
}
