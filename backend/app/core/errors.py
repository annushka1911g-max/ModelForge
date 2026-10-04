"""
Centralized HTTP exception handlers and error response schemas.
"""
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Optional

logger = logging.getLogger("modelforge.errors")


class ErrorDetail(BaseModel):
    """Standard error response body."""
    status: str = "error"
    message: str
    code: Optional[str] = None
    details: Optional[Any] = None


def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handles FastAPI HTTPException with standardized structure
    while preserving {"detail": ...} for backward compatibility with existing tests.
    """
    from fastapi.exceptions import HTTPException

    if isinstance(exc, HTTPException):
        detail_msg = exc.detail if isinstance(exc.detail, str) else "Request error"
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            429: "TOO_MANY_REQUESTS",
            500: "INTERNAL_SERVER_ERROR",
            501: "NOT_IMPLEMENTED",
        }
        code = getattr(exc, "code", code_map.get(exc.status_code, "HTTP_ERROR"))
        content = {
            "detail": exc.detail,
            "status": "error",
            "message": detail_msg,
            "code": code,
            "details": exc.detail if not isinstance(exc.detail, str) else None,
        }

        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=exc.headers,
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Unexpected error",
            "status": "error",
            "message": "An unexpected server error occurred",
            "code": "INTERNAL_SERVER_ERROR",
            "details": None,
        },
    )


def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handles Pydantic validation errors — returns structured 422 with all field errors.
    """
    field_errors = []
    for error in exc.errors():
        field_errors.append({
            "field": " -> ".join(str(e) for e in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    logger.warning("Validation error on %s: %s", request.url.path, field_errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorDetail(
            message="Request validation failed",
            code="VALIDATION_ERROR",
            details=field_errors,
        ).model_dump(exclude_none=True),
    )


def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global catch-all handler — logs exception and returns 500.
    """
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorDetail(
            message="An internal server error occurred",
            code="INTERNAL_SERVER_ERROR",
        ).model_dump(exclude_none=True),
    )


def register_error_handlers(app: FastAPI) -> None:
    """
    Registers all error handlers on the FastAPI application.
    """
    from fastapi.exceptions import HTTPException
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    logger.info("Exception handlers registered.")
