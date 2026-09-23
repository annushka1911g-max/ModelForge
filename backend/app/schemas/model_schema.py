"""
Pydantic schemas for Model and ModelVersion entities.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from backend.app.models.model import MLFramework, TaskType
from backend.app.models.model_version import VersionStatus


class FeatureSpec(BaseModel):
    name: str
    type: str  # "float", "int", "string"
    required: bool = True
    description: Optional[str] = None


class ModelVersionBase(BaseModel):
    version_number: int
    artifact_path: str
    file_hash: str
    file_size_bytes: int
    feature_schema: List[Dict[str, Any]]
    target_schema: Optional[Dict[str, Any]] = None
    training_metrics: Optional[Dict[str, Any]] = None
    status: VersionStatus = VersionStatus.READY
    changelog: Optional[str] = None


class ModelVersionResponse(ModelVersionBase):
    id: int
    model_id: int
    created_by: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModelBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    framework: MLFramework
    task_type: TaskType


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None


class ModelResponse(ModelBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    versions: List[ModelVersionResponse] = []

    model_config = ConfigDict(from_attributes=True)
