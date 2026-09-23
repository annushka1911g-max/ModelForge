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
        else:
            logger.error("✗ Database connectivity check returned unexpected result.")
    except Exception as exc:
        logger.error("✗ Database connection FAILED on startup: %s", exc, exc_info=True)

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


# ── System-Level Health Endpoints (outside versioned prefix) ──────────────────
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
