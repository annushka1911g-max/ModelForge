"""
Model Catalog and Model Version API routes.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.model_schema import (
    ModelCreate,
    ModelResponse,
    ModelVersionResponse,
)
from backend.app.authentication.rbac import get_current_user, require_roles
from backend.app.models.user import User, UserRole

router = APIRouter()


@router.post(
    "/",
    response_model=ModelResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER]))],
)
def create_model(model_in: ModelCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Register a new model entity.
    """
    raise NotImplementedError("Create model endpoint to be implemented")


@router.get("/", response_model=List[ModelResponse])
def list_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all registered models.
    """
    raise NotImplementedError("List models endpoint to be implemented")


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    """
    Get model details by ID.
    """
    raise NotImplementedError("Get model endpoint to be implemented")


@router.post(
    "/{model_id}/versions",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER]))],
)
def upload_model_version(
    model_id: int,
    file: UploadFile = File(...),
    feature_schema: str = Form(...),
    training_metrics: Optional[str] = Form(None),
    changelog: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a new model artifact and register a new version.
    """
    raise NotImplementedError("Upload model version endpoint to be implemented")


@router.get("/{model_id}/versions", response_model=List[ModelVersionResponse])
def list_model_versions(model_id: int, db: Session = Depends(get_db)):
    """
    List all versions for a given model.
    """
    raise NotImplementedError("List model versions endpoint to be implemented")
