"""
Pydantic schemas for Deployment entity.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.app.models.deployment import DeploymentStatus


class DeploymentBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_id: int
    current_version_id: int


class DeploymentCreate(DeploymentBase):
    pass


class DeploymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    model_id: int
    current_version_id: int
    previous_version_id: Optional[int] = None
    status: DeploymentStatus
    endpoint_path: str
    deployed_by: Optional[int] = None
    deployed_at: datetime
    last_rollback_at: Optional[datetime] = None
    updated_at: datetime


class RollbackRequest(BaseModel):
    target_version_id: Optional[int] = None
