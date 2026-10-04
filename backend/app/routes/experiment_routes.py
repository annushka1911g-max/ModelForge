"""
Experiment tracking API routes.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.authentication.rbac import get_current_user, require_roles
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.schemas.experiment_schema import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentUpdate,
)
from backend.app.services.experiment_service import ExperimentService

router = APIRouter()


@router.post("/", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED, summary="Create experiment run")
def create_experiment(
    experiment_in: ExperimentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = ExperimentService(db)
    return svc.create_experiment(experiment_in, current_user.id)


@router.get("/", response_model=List[ExperimentResponse], summary="List experiments")
def list_experiments(
    skip: int = 0,
    limit: int = 100,
    model_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ExperimentService(db)
    return svc.list_experiments(skip=skip, limit=limit, model_id=model_id, status=status, search=search)


@router.get("/compare", summary="Compare multiple experiments")
def compare_experiments(
    ids: str = Query(..., description="Comma-separated experiment IDs, e.g. 1,2"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ExperimentService(db)
    try:
        experiment_ids = [int(i.strip()) for i in ids.split(",") if i.strip()]
    except ValueError:
        experiment_ids = []
    return svc.compare_experiments(experiment_ids)


@router.get("/{experiment_id}", response_model=ExperimentResponse, summary="Get experiment details")
def get_experiment(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ExperimentService(db)
    return svc.get_experiment(experiment_id)


@router.patch("/{experiment_id}", response_model=ExperimentResponse, summary="Update experiment")
def update_experiment(
    experiment_id: int,
    update_in: ExperimentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = ExperimentService(db)
    return svc.update_experiment(experiment_id, update_in)
