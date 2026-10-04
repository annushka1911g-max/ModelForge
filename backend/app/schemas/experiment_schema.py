"""
Pydantic schemas for Experiment Tracking.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from backend.app.models.experiment import ExperimentStatus


class ExperimentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    model_id: Optional[int] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    dataset_name: Optional[str] = None
    dataset_version: Optional[str] = None
    status: ExperimentStatus = ExperimentStatus.RUNNING


class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    dataset_name: Optional[str] = None
    dataset_version: Optional[str] = None
    status: Optional[ExperimentStatus] = None
    completed_at: Optional[datetime] = None


class ExperimentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model_id: Optional[int] = None
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]
    dataset_name: Optional[str] = None
    dataset_version: Optional[str] = None
    status: ExperimentStatus
    created_by: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
