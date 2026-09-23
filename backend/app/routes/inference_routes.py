"""
Real-time Inference and Prediction Logs API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.inference_schema import (
    PredictionRequest,
    PredictionResponse,
    PredictionLogResponse,
)

router = APIRouter()


@router.post("/{deployment_id}/predict", response_model=PredictionResponse)
def predict(deployment_id: int, request_in: PredictionRequest, request: Request, db: Session = Depends(get_db)):
    """
    Execute real-time prediction against deployed model.
    """
    raise NotImplementedError("Predict endpoint to be implemented")


@router.get("/{deployment_id}/logs", response_model=List[PredictionLogResponse])
def get_prediction_logs(deployment_id: int, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve historical prediction logs for this deployment.
    """
    raise NotImplementedError("Get prediction logs endpoint to be implemented")
