"""
Model Catalog and Model Version API routes.
"""
import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.authentication.rbac import get_current_user, require_roles
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.schemas.model_schema import (
    ModelCreate,
    ModelResponse,
    ModelUpdate,
    ModelVersionResponse,
)
from backend.app.services.model_service import ModelService

router = APIRouter()
logger = logging.getLogger("modelforge.routes.models")


@router.post(
    "/",
    response_model=ModelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new model",
    operation_id="create_model",
)
def create_model(
    model_in: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = ModelService(db)
    return svc.create_model(model_in, current_user.id)


@router.get("/", response_model=List[ModelResponse], summary="List all models", operation_id="list_models")
def list_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    svc = ModelService(db)
    return svc.list_models(skip, limit)


@router.get("/{model_id}", response_model=ModelResponse, summary="Get model details", operation_id="get_model")
def get_model(model_id: int, db: Session = Depends(get_db)):
    svc = ModelService(db)
    return svc.get_model(model_id)


@router.patch(
    "/{model_id}",
    response_model=ModelResponse,
    summary="Update model metadata",
    operation_id="update_model",
)
def update_model(
    model_id: int,
    model_update: ModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = ModelService(db)
    return svc.update_model(model_id, model_update)


@router.post(
    "/{model_id}/versions",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new model version artifact",
    operation_id="upload_model_version",
)
def upload_model_version(
    model_id: int,
    file: UploadFile = File(...),
    feature_schema: str = Form(...),
    training_metrics: Optional[str] = Form(None),
    changelog: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    # Parse JSON strings from form data
    try:
        parsed_schema = json.loads(feature_schema)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="feature_schema must be valid JSON")

    parsed_metrics = None
    if training_metrics:
        try:
            parsed_metrics = json.loads(training_metrics)
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail="training_metrics must be valid JSON")

    svc = ModelService(db)
    return svc.upload_version(
        model_id=model_id,
        file_obj=file.file,
        filename=file.filename,
        feature_schema=parsed_schema,
        training_metrics=parsed_metrics,
        changelog=changelog,
        user_id=current_user.id,
    )


@router.get(
    "/{model_id}/versions",
    response_model=List[ModelVersionResponse],
    summary="List all versions for a model",
    operation_id="list_model_versions",
)
def list_model_versions(model_id: int, db: Session = Depends(get_db)):
    svc = ModelService(db)
    return svc.get_versions(model_id)
