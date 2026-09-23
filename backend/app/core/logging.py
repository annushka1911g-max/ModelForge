"""
Structured logging configuration and request logger middleware for ModelForge.
"""
import time
import logging
import sys
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.app.configuration.settings import settings


def setup_logging() -> logging.Logger:
    """
    Configures standardized logging across ModelForge components.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    log_format = (
        "[%(asctime)s] [%(process)d] [%(levelname)s] "
        "[%(name)s:%(funcName)s:%(lineno)d] %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Set logger levels for third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if not settings.DEBUG else logging.INFO)

    logger = logging.getLogger("modelforge")
    logger.setLevel(log_level)
    logger.info("Logging configured successfully for environment: %s", settings.ENVIRONMENT)
    return logger


logger = logging.getLogger("modelforge")


def get_logger(name: str) -> logging.Logger:
    """
    Returns a child logger under the modelforge namespace.
    """
    return logging.getLogger(f"modelforge.{name}")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs incoming HTTP requests, response status, and processing duration in milliseconds.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            status_code = response.status_code

            # Log request metrics
            logger.info(
                "%s %s -> %d (%.2fms) [client: %s]",
                method,
                path,
                status_code,
                duration_ms,
                client_ip,
            )
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "%s %s -> FAILED with %s (%.2fms) [client: %s]",
                method,
                path,
                type(exc).__name__,
                duration_ms,
                client_ip,
                exc_info=True,
            )
            raise exc
