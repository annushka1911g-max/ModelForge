"""
Monitoring and health API routes under /api/v1/monitoring.
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.core.health import check_db_connection
from backend.app.configuration.settings import settings

router = APIRouter()
logger = logging.getLogger("modelforge.routes.monitoring")


@router.get("/health", summary="Detailed API health check")
def health_check(db: Session = Depends(get_db)):
    """
    Verifies connectivity to PostgreSQL and reports current deployment status.
    Returns a structured JSON object suitable for readiness monitoring.
    """
    db_status = check_db_connection(db)
    overall_status = "healthy" if db_status["status"] == "connected" else "degraded"

    logger.info("Health check requested — status: %s", overall_status)
    return {
        "status": overall_status,
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "services": {
            "database": db_status,
        },
    }
