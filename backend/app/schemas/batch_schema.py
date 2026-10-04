"""
Pydantic schemas for Batch prediction jobs.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.app.models.batch_job import BatchStatus


class BatchJobCreate(BaseModel):
    deployment_id: int


class BatchJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    deployment_id: int
    model_version_id: int
    input_file_url: str
    output_file_url: Optional[str] = None
    total_records: int
    processed_records: int
    status: BatchStatus
    error_message: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

