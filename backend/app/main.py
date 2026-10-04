"""
ModelForge — FastAPI Backend Application Entry Point.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.app.configuration.settings import settings
from backend.app.core.logging import setup_logging, RequestLoggingMiddleware
from backend.app.core.errors import register_error_handlers
from backend.app.core.health import check_db_connection
from backend.app.database.session import get_db, engine
from backend.app.routes.api_router import api_router

# ── Bootstrap Logging ────────────────────────────────────────────────────────
setup_logging()
logger = logging.getLogger("modelforge.main")


# ── Application Lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Handles startup and shutdown events for the application.
    - Startup: validate DB connection, log configuration.
    - Shutdown: dispose DB engine connection pool gracefully.
    """
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info("╔══════════════════════════════════════╗")
    logger.info("║     ModelForge Backend Starting Up    ║")
    logger.info("╚══════════════════════════════════════╝")
    logger.info("Environment : %s", settings.ENVIRONMENT)
    logger.info("Debug Mode  : %s", settings.DEBUG)
    logger.info("Database    : %s", settings.POSTGRES_DB)
    logger.info("API Prefix  : %s", settings.API_V1_STR)

    # Verify database connectivity on startup
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
        if result == 1:
            logger.info("✓ Database connection verified successfully.")
            # Automatically create tables if not present (for fresh cloud database deploys like Render/Neon/Supabase)
            try:
                from backend.app.database.base import Base
                import backend.app.models  # noqa: F401
                Base.metadata.create_all(bind=engine)
                logger.info("✓ Database schema verified / initialized.")
            except Exception as schema_err:
                logger.warning("Database schema initialization notice: %s", schema_err)
        else:
            logger.error("✗ Database connectivity check returned unexpected result.")
    except Exception as exc:
        logger.error("✗ Database connection FAILED on startup: %s", exc, exc_info=True)

    # Initialize artifact storage
    try:
        from backend.app.services.storage_service import StorageService
        storage = StorageService()
        storage.ensure_buckets()
        logger.info("✓ Artifact storage initialized.")
    except Exception as exc:
        logger.warning("Artifact storage initialization failed: %s", exc)

    # Ensure default users and demo accounts exist
    try:
        from backend.app.database.seed import seed_database
        seed_database()
        logger.info("✓ Default demo users verified.")
    except Exception as exc:
        logger.warning("Default user seeding skipped: %s", exc)

    # Register custom Prometheus metrics
    try:
        from prometheus_client import Counter, Histogram, Gauge
        app.state.prom_prediction_count = Counter(
            "modelforge_predictions_total", "Total predictions served", ["deployment_id", "status"]
        )
        app.state.prom_prediction_latency = Histogram(
            "modelforge_prediction_latency_ms", "Prediction latency in milliseconds",
            buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 5000],
        )
        app.state.prom_active_deployments = Gauge(
            "modelforge_active_deployments", "Number of active deployments"
        )
        logger.info("✓ Prometheus metrics registered.")
    except Exception as exc:
        logger.warning("Prometheus metrics registration failed: %s", exc)

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("ModelForge Backend shutting down — disposing DB connection pool...")
    engine.dispose()
    logger.info("Shutdown complete.")



# ── Application Factory ───────────────────────────────────────────────────────
def create_application() -> FastAPI:
    """
    Creates and configures the FastAPI application instance.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        description="A self-hosted MLOps platform for one-click model deployment.",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Middleware ─────────────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(RequestLoggingMiddleware)

    # ── Exception Handlers ─────────────────────────────────────────────────
    register_error_handlers(application)

    # ── API Routers ────────────────────────────────────────────────────────
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()


# ── System-Level Health Endpoints ─────────────────────────────────────────────
@app.get("/health", summary="Comprehensive System Health Check", include_in_schema=False)
def health(db=Depends(get_db)):
    """
    Comprehensive health check validating API, Database, Storage, and Inference Engine.
    """
    from backend.app.core.health import get_system_health
    return {
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        **get_system_health(db),
    }


@app.get("/health/live", summary="Liveness probe", include_in_schema=False)
@app.get("/healthz", tags=["System Health"], summary="Liveness probe")
def liveness():
    """
    Lightweight liveness check. Returns immediately without touching the database.
    Used by load balancers / Docker HEALTHCHECK.
    """
    return {
        "status": "alive",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health/ready", summary="Readiness probe", include_in_schema=False)
@app.get("/readyz", tags=["System Health"], summary="Readiness probe with DB check")
def readiness(db=Depends(get_db)):
    """
    Readiness check that verifies PostgreSQL connectivity.
    Returns degraded status if DB is unreachable.
    """
    db_status = check_db_connection(db)
    overall_status = "ready" if db_status["status"] == "connected" else "degraded"

    return {
        "status": overall_status,
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "services": {
            "database": db_status,
        },
    }
