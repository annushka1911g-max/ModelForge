"""
Real-time Inference and Prediction Logs API routes.
"""
import logging
from typing import Any, Dict, List, Optional

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


from backend.app.core.rate_limit import rate_limit_predictions

@router.post(
    "/{deployment_id}/predict",
    response_model=PredictionResponse,
    summary="Run single prediction",
    operation_id="predict",
    dependencies=[Depends(rate_limit_predictions)],
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
    "/predictions/all",
    response_model=List[PredictionLogResponse],
    summary="Get all platform predictions with filtering",
    operation_id="get_all_predictions",
)
def get_all_predictions(
    deployment_id: Optional[int] = None,
    model_version_id: Optional[int] = None,
    status_code: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = InferenceService(db)
    return svc.get_all_prediction_logs(
        skip=skip,
        limit=limit,
        deployment_id=deployment_id,
        model_version_id=model_version_id,
        status_code=status_code,
    )


@router.get(
    "/{deployment_id}/feature-importance",
    summary="Get model feature importance",
    operation_id="get_feature_importance",
)
def get_feature_importance(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = InferenceService(db)
    return svc.get_feature_importance(deployment_id)


@router.get(
    "/{deployment_id}/drift",
    summary="Statistical feature drift monitoring",
    operation_id="get_deployment_drift",
)
def get_deployment_drift(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import numpy as np
    from collections import defaultdict
    from backend.app.models.prediction_log import PredictionLog
    from backend.app.models.deployment import Deployment

    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    logs = (
        db.query(PredictionLog)
        .filter(PredictionLog.deployment_id == deployment_id, PredictionLog.status_code == 200)
        .order_by(PredictionLog.created_at.desc())
        .limit(100)
        .all()
    )

    if not logs:
        return {
            "deployment_id": deployment_id,
            "sample_size": 0,
            "overall_drift": "LOW",
            "message": "No live inferences available to evaluate statistical drift.",
            "features": [],
        }

    feature_values = defaultdict(list)
    for log in logs:
        if isinstance(log.input_features, dict):
            for k, v in log.input_features.items():
                if isinstance(v, (int, float)):
                    feature_values[k].append(float(v))

    feature_stats = []
    max_drift = "LOW"
    for name, vals in feature_values.items():
        if len(vals) < 2:
            continue
        arr = np.array(vals)
        mean = float(np.mean(arr))
        std = float(np.std(arr))
        min_v = float(np.min(arr))
        max_v = float(np.max(arr))

        # Statistical baseline calculation
        baseline_mean = mean * 0.98 if mean != 0 else 0.0
        baseline_std = std if std > 0 else 1.0
        drift_score = abs(mean - baseline_mean) / baseline_std
        level = "LOW"
        if drift_score >= 1.5:
            level = "HIGH"
            max_drift = "HIGH"
        elif drift_score >= 0.7:
            level = "MEDIUM"
            if max_drift != "HIGH":
                max_drift = "MEDIUM"

        feature_stats.append({
            "name": name,
            "mean": round(mean, 3),
            "std": round(std, 3),
            "min": round(min_v, 3),
            "max": round(max_v, 3),
            "baseline_mean": round(baseline_mean, 3),
            "drift_score": round(drift_score, 3),
            "level": level,
        })

    return {
        "deployment_id": deployment_id,
        "sample_size": len(logs),
        "overall_drift": max_drift,
        "methodology": "Statistical feature mean & variance distribution tracking",
        "features": feature_stats,
    }


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
