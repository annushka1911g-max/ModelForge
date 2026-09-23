"""
Pydantic schemas for Inference and Prediction logs.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, ConfigDict


class PredictionRequest(BaseModel):
    features: Dict[str, Any]


class PredictionResponse(BaseModel):
    prediction: Union[List[Any], Any]
    probabilities: Optional[List[float]] = None
    model_version: int
    latency_ms: float
    timestamp: datetime


class PredictionLogResponse(BaseModel):
    id: int
    deployment_id: int
    model_version_id: int
    input_features: Dict[str, Any]
    prediction_output: Any
    latency_ms: float
    status_code: int
    error_message: Optional[str] = None
    client_ip: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
