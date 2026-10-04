"""
Monitoring, Health, Metrics, and Stats API routes.
"""
import logging
from typing import Any, Dict, List, Optional

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
    from backend.app.core.health import check_storage_connection, check_inference_engine
    db_status = check_db_connection(db)
    storage_status = check_storage_connection()
    inference_status = check_inference_engine()
    overall_status = "healthy" if db_status["status"] == "connected" else "degraded"
    return {
        "status": overall_status,
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "services": {
            "database": db_status,
            "storage": storage_status,
            "inference_engine": inference_status,
        },
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


@router.get("/dashboard-analytics", summary="Comprehensive Dashboard telemetry & charts data")
def dashboard_analytics(db: Session = Depends(get_db)):
    from datetime import datetime, timezone, timedelta
    from collections import defaultdict
    import numpy as np
    from sqlalchemy import func
    from backend.app.core.health import get_system_health
    from backend.app.models.batch_job import BatchJob, BatchStatus
    from backend.app.models.deployment import Deployment, DeploymentStatus
    from backend.app.models.model import Model
    from backend.app.models.model_version import ModelVersion
    from backend.app.models.prediction_log import PredictionLog

    # Overview counts
    total_models = db.query(Model).count()
    total_versions = db.query(ModelVersion).count()
    total_deployments = db.query(Deployment).count()
    active_deployments = db.query(Deployment).filter(Deployment.status == DeploymentStatus.DEPLOYED).count()
    stopped_deployments = db.query(Deployment).filter(Deployment.status == DeploymentStatus.STOPPED).count()
    total_batch_jobs = db.query(BatchJob).count()
    failed_batch_jobs = db.query(BatchJob).filter(BatchJob.status == BatchStatus.FAILED).count()

    total_predictions = db.query(PredictionLog).count()
    successful_predictions = db.query(PredictionLog).filter(PredictionLog.status_code == 200).count()
    failed_predictions = db.query(PredictionLog).filter(PredictionLog.status_code != 200).count()
    avg_latency = float(db.query(func.avg(PredictionLog.latency_ms)).scalar() or 0.0)

    success_rate = round((successful_predictions / total_predictions * 100), 1) if total_predictions > 0 else 100.0

    # Predictions over time (last 7 days by day, or last 24h by 4h buckets)
    now = datetime.now(timezone.utc)
    recent_logs = (
        db.query(PredictionLog)
        .order_by(PredictionLog.created_at.desc())
        .limit(1000)
        .all()
    )

    time_buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"total": 0, "successful": 0, "failed": 0, "latencies": []})
    for l in recent_logs:
        if l.created_at:
            bucket_key = l.created_at.strftime("%b %d")
            time_buckets[bucket_key]["total"] += 1
            if l.status_code == 200:
                time_buckets[bucket_key]["successful"] += 1
            else:
                time_buckets[bucket_key]["failed"] += 1
            if l.latency_ms:
                time_buckets[bucket_key]["latencies"].append(l.latency_ms)

    # Sort chronological
    chart_predictions_over_time = []
    for k, v in list(time_buckets.items())[-7:]:
        avg_lat = float(np.mean(v["latencies"])) if v["latencies"] else 0.0
        chart_predictions_over_time.append({
            "label": k,
            "total": v["total"],
            "successful": v["successful"],
            "failed": v["failed"],
            "avg_latency": round(avg_lat, 2),
        })

    # Latency percentiles
    all_latencies = [l.latency_ms for l in recent_logs if l.latency_ms and l.latency_ms > 0]
    latency_dist = {
        "min": round(float(np.min(all_latencies)), 2) if all_latencies else 0.0,
        "p50": round(float(np.percentile(all_latencies, 50)), 2) if all_latencies else 0.0,
        "p90": round(float(np.percentile(all_latencies, 90)), 2) if all_latencies else 0.0,
        "p95": round(float(np.percentile(all_latencies, 95)), 2) if all_latencies else 0.0,
        "max": round(float(np.max(all_latencies)), 2) if all_latencies else 0.0,
    }

    # Model usage distribution
    models = db.query(Model).all()
    model_name_map = {m.id: m.display_name for m in models}
    deployments = db.query(Deployment).all()
    dep_to_model = {d.id: d.model_id for d in deployments}

    model_counts: Dict[str, int] = defaultdict(int)
    for l in recent_logs:
        mid = dep_to_model.get(l.deployment_id)
        mname = model_name_map.get(mid, f"Model #{mid}" if mid else "Unknown")
        model_counts[mname] += 1

    model_usage = [{"name": k, "predictions": v} for k, v in model_counts.items()]

    # Recent items
    recent_deployments = [
        {
            "id": d.id,
            "model_name": model_name_map.get(d.model_id, f"Model #{d.model_id}"),
            "version_id": d.current_version_id,
            "status": d.status.value,
            "endpoint_path": d.endpoint_path,
            "deployed_at": d.deployed_at.isoformat() if d.deployed_at else None,
        }
        for d in deployments[:5]
    ]

    recent_models = [
        {
            "id": m.id,
            "name": m.name,
            "display_name": m.display_name,
            "framework": m.framework.value,
            "task_type": m.task_type.value,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "is_starred": m.is_starred,
            "tags": m.tags or [],
        }
        for m in models[:5]
    ]

    return {
        "stats": {
            "total_models": total_models,
            "total_model_versions": total_versions,
            "total_deployments": total_deployments,
            "active_deployments": active_deployments,
            "stopped_deployments": stopped_deployments,
            "total_predictions": total_predictions,
            "successful_predictions": successful_predictions,
            "failed_predictions": failed_predictions,
            "success_rate": success_rate,
            "avg_latency_ms": round(avg_latency, 2),
            "total_batch_jobs": total_batch_jobs,
            "failed_batch_jobs": failed_batch_jobs,
        },
        "charts": {
            "predictions_over_time": chart_predictions_over_time,
            "deployment_activity": {
                "active": active_deployments,
                "stopped": stopped_deployments,
                "total": total_deployments,
            },
            "latency_distribution": latency_dist,
            "model_usage": model_usage,
        },
        "system_health": get_system_health(db),
        "recent_deployments": recent_deployments,
        "recent_models": recent_models,
    }


@router.get("/performance", summary="Model Performance Analytics")
def get_performance_analytics(
    model_id: Optional[int] = None,
    version_id: Optional[int] = None,
    time_range: str = "24h",
    db: Session = Depends(get_db),
):
    from datetime import datetime, timezone, timedelta
    import numpy as np
    from sqlalchemy import func
    from backend.app.models.deployment import Deployment
    from backend.app.models.model import Model
    from backend.app.models.model_version import ModelVersion
    from backend.app.models.prediction_log import PredictionLog

    query = db.query(PredictionLog)
    now = datetime.now(timezone.utc)
    if time_range == "24h":
        cutoff = now - timedelta(hours=24)
    elif time_range == "7d":
        cutoff = now - timedelta(days=7)
    elif time_range == "30d":
        cutoff = now - timedelta(days=30)
    elif time_range == "90d":
        cutoff = now - timedelta(days=90)
    else:
        cutoff = now - timedelta(hours=24)

    query = query.filter(PredictionLog.created_at >= cutoff)

    if version_id:
        query = query.filter(PredictionLog.model_version_id == version_id)
    elif model_id:
        deployment_ids = [d.id for d in db.query(Deployment.id).filter(Deployment.model_id == model_id).all()]
        query = query.filter(PredictionLog.deployment_id.in_(deployment_ids))

    logs = query.order_by(PredictionLog.created_at.asc()).all()
    total_calls = len(logs)
    successful = sum(1 for l in logs if l.status_code == 200)
    failed = total_calls - successful
    failure_rate = round((failed / total_calls) * 100, 2) if total_calls > 0 else 0.0

    latencies = [l.latency_ms for l in logs if l.latency_ms and l.latency_ms > 0]
    avg_latency = float(np.mean(latencies)) if latencies else 0.0
    p95_latency = float(np.percentile(latencies, 95)) if latencies else 0.0

    # Retrieve metrics from version if specified or latest version
    training_metrics: Dict[str, Any] = {}
    if version_id:
        ver = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
        if ver and ver.training_metrics:
            training_metrics = ver.training_metrics
    elif model_id:
        ver = db.query(ModelVersion).filter(ModelVersion.model_id == model_id).order_by(ModelVersion.version_number.desc()).first()
        if ver and ver.training_metrics:
            training_metrics = ver.training_metrics

    # Time series breakdown
    from collections import defaultdict
    buckets = defaultdict(lambda: {"count": 0, "failures": 0, "latencies": []})
    for l in logs:
        fmt = "%H:00" if time_range == "24h" else "%b %d"
        k = l.created_at.strftime(fmt)
        buckets[k]["count"] += 1
        if l.status_code != 200:
            buckets[k]["failures"] += 1
        if l.latency_ms:
            buckets[k]["latencies"].append(l.latency_ms)

    timeseries = []
    for k, v in buckets.items():
        avg_lat = float(np.mean(v["latencies"])) if v["latencies"] else 0.0
        timeseries.append({
            "timestamp": k,
            "inferences": v["count"],
            "failures": v["failures"],
            "avg_latency": round(avg_lat, 2),
        })

    return {
        "time_range": time_range,
        "total_inferences": total_calls,
        "successful_inferences": successful,
        "failed_inferences": failed,
        "failure_rate": failure_rate,
        "avg_latency_ms": round(avg_latency, 2),
        "p95_latency_ms": round(p95_latency, 2),
        "training_metrics": training_metrics,
        "timeseries": timeseries,
    }
