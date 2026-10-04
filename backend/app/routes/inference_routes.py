"""
Real-time Inference and Prediction Logs API routes.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from backend.app.authentication.rbac import get_current_user
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.inference_schema import (
    PredictionLogResponse,
    PredictionRequest,
    PredictionResponse,
)
from backend.app.services.inference_service import InferenceService

router = APIRouter()
logger = logging.getLogger("modelforge.routes.inference")


@router.post(
    "/{deployment_id}/predict",
    response_model=PredictionResponse,
    summary="Run single prediction",
    operation_id="predict",
)
def predict(
    deployment_id: int,
    request_in: PredictionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client_ip = request.client.host if request.client else "unknown"
    svc = InferenceService(db)
    return svc.predict(deployment_id, request_in.features, client_ip)


@router.get(
    "/{deployment_id}/logs",
    response_model=List[PredictionLogResponse],
    summary="Get prediction logs",
    operation_id="get_prediction_logs",
)
def get_prediction_logs(
    deployment_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    svc = InferenceService(db)
    return svc.get_prediction_logs(deployment_id, skip, limit)


@router.get(
    "/{deployment_id}/health",
    summary="Deployment health check",
    operation_id="deployment_health",
)
def deployment_health(deployment_id: int, db: Session = Depends(get_db)):
    from backend.app.services.deployment_service import DeploymentService

    svc = DeploymentService(db)
    deployment = svc.get_deployment(deployment_id)
    return {
        "deployment_id": deployment.id,
        "status": deployment.status.value,
        "model_id": deployment.model_id,
        "current_version_id": deployment.current_version_id,
    }
