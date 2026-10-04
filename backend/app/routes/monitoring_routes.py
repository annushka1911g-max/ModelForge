"""
Monitoring, Health, Metrics, and Stats API routes.
"""
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend.app.configuration.settings import settings
from backend.app.core.health import check_db_connection
from backend.app.database.session import get_db

router = APIRouter()
logger = logging.getLogger("modelforge.routes.monitoring")


@router.get("/health", summary="Detailed API health check", operation_id="monitoring_health")
def health_check(db: Session = Depends(get_db)):
    db_status = check_db_connection(db)
    overall_status = "healthy" if db_status["status"] == "connected" else "degraded"
    return {
        "status": overall_status,
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "services": {"database": db_status},
    }


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    operation_id="prometheus_metrics",
    response_class=PlainTextResponse,
)
def prometheus_metrics():
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    return PlainTextResponse(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/stats", summary="System statistics", operation_id="system_stats")
def system_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    from backend.app.models.batch_job import BatchJob
    from backend.app.models.deployment import Deployment, DeploymentStatus
    from backend.app.models.model import Model
    from backend.app.models.prediction_log import PredictionLog

    total_predictions = db.query(PredictionLog).count()
    successful_predictions = db.query(PredictionLog).filter(PredictionLog.status_code == 200).count()
    failed_predictions = db.query(PredictionLog).filter(PredictionLog.status_code != 200).count()
    avg_latency = db.query(func.avg(PredictionLog.latency_ms)).scalar() or 0.0

    return {
        "total_models": db.query(Model).count(),
        "total_deployments": db.query(Deployment).count(),
        "active_deployments": db.query(Deployment).filter(
            Deployment.status == DeploymentStatus.DEPLOYED
        ).count(),
        "total_predictions": total_predictions,
        "successful_predictions": successful_predictions,
        "failed_predictions": failed_predictions,
        "avg_latency_ms": round(float(avg_latency), 2),
        "total_batch_jobs": db.query(BatchJob).count(),
    }


@router.get("/logs", summary="Recent prediction logs for monitoring", operation_id="monitoring_logs")
def recent_prediction_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    from backend.app.models.prediction_log import PredictionLog
    logs = (
        db.query(PredictionLog)
        .order_by(PredictionLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": log.id,
            "deployment_id": log.deployment_id,
            "model_version_id": log.model_version_id,
            "latency_ms": round(log.latency_ms, 2),
            "status_code": log.status_code,
            "error_message": log.error_message,
            "client_ip": log.client_ip,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
