"""
Model Catalog and Model Version API routes.
"""
import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
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
from backend.app.services.audit_service import log_audit_event
from backend.app.services.model_service import ModelService
from backend.app.services.notification_service import create_notification

router = APIRouter()
logger = logging.getLogger("modelforge.routes.models")


class TagRequest(BaseModel):
    tag: str


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
    model = svc.create_model(model_in, current_user.id)
    log_audit_event(
        db=db,
        action="MODEL_CREATE",
        resource="model",
        resource_id=str(model.id),
        user=current_user,
        metadata={"name": model.name, "framework": model.framework.value},
    )
    create_notification(
        db=db,
        title="Model Registered",
        message=f"Model '{model.display_name}' ({model.name}) registered successfully.",
        notification_type="SUCCESS",
        link=f"/models/{model.id}",
    )
    return model


@router.get("/", response_model=List[ModelResponse], summary="List all models", operation_id="list_models")
def list_models(
    skip: int = 0,
    limit: int = 100,
    framework: Optional[str] = None,
    task_type: Optional[str] = None,
    tag: Optional[str] = None,
    is_starred: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    svc = ModelService(db)
    return svc.list_models(
        skip=skip,
        limit=limit,
        framework=framework,
        task_type=task_type,
        tag=tag,
        is_starred=is_starred,
        search=search,
    )


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
    updated = svc.update_model(model_id, model_update)
    log_audit_event(
        db=db,
        action="MODEL_UPDATE",
        resource="model",
        resource_id=str(model_id),
        user=current_user,
    )
    return updated


@router.post("/{model_id}/favorite", response_model=ModelResponse, summary="Toggle model favorite")
def toggle_favorite(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ModelService(db)
    return svc.toggle_favorite(model_id)


@router.post("/{model_id}/tags", response_model=ModelResponse, summary="Add tag to model")
def add_tag(
    model_id: int,
    tag_in: TagRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = ModelService(db)
    return svc.add_tag(model_id, tag_in.tag)


@router.delete("/{model_id}/tags/{tag}", response_model=ModelResponse, summary="Remove tag from model")
def remove_tag(
    model_id: int,
    tag: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = ModelService(db)
    return svc.remove_tag(model_id, tag)


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
    version = svc.upload_version(
        model_id=model_id,
        file_obj=file.file,
        filename=file.filename,
        feature_schema=parsed_schema,
        training_metrics=parsed_metrics,
        changelog=changelog,
        user_id=current_user.id,
    )
    log_audit_event(
        db=db,
        action="VERSION_UPLOAD",
        resource="version",
        resource_id=str(version.id),
        user=current_user,
        metadata={"model_id": model_id, "version_number": version.version_number},
    )
    create_notification(
        db=db,
        title="Version Uploaded",
        message=f"Uploaded version v{version.version_number} for model #{model_id}.",
        notification_type="SUCCESS",
        link=f"/models/{model_id}",
    )
    return version


@router.get(
    "/{model_id}/versions",
    response_model=List[ModelVersionResponse],
    summary="List all versions for a model",
    operation_id="list_model_versions",
)
def list_model_versions(model_id: int, db: Session = Depends(get_db)):
    svc = ModelService(db)
    return svc.get_versions(model_id)


@router.get(
    "/{model_id}/versions/compare",
    summary="Compare model versions",
    operation_id="compare_model_versions",
)
def compare_model_versions(
    model_id: int,
    version_ids: Optional[str] = Query(None, description="Comma-separated version IDs, e.g. 1,2"),
    db: Session = Depends(get_db),
):
    svc = ModelService(db)
    v_ids = []
    if version_ids:
        try:
            v_ids = [int(v.strip()) for v in version_ids.split(",") if v.strip()]
        except ValueError:
            v_ids = []
    return svc.compare_versions(model_id, v_ids)
