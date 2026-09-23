"""
Deployment lifecycle API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.deployment_schema import (
    DeploymentCreate,
    DeploymentResponse,
    RollbackRequest,
)
from backend.app.authentication.rbac import get_current_user, require_roles
from backend.app.models.user import User, UserRole

router = APIRouter()


@router.post(
    "/",
    response_model=DeploymentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER]))],
)
def deploy_model(
    deployment_in: DeploymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deploy a specific model version with one click.
    """
    raise NotImplementedError("Deploy model endpoint to be implemented")


@router.get("/", response_model=List[DeploymentResponse])
def list_deployments(db: Session = Depends(get_db)):
    """
    List all active and inactive deployments.
    """
    raise NotImplementedError("List deployments endpoint to be implemented")


@router.get("/{deployment_id}", response_model=DeploymentResponse)
def get_deployment(deployment_id: int, db: Session = Depends(get_db)):
    """
    Get deployment details and status.
    """
    raise NotImplementedError("Get deployment endpoint to be implemented")


@router.post(
    "/{deployment_id}/rollback",
    response_model=DeploymentResponse,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER]))],
)
def rollback_deployment(
    deployment_id: int,
    rollback_in: RollbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Roll back deployment to its previous version.
    """
    raise NotImplementedError("Rollback deployment endpoint to be implemented")


@router.post(
    "/{deployment_id}/stop",
    response_model=DeploymentResponse,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER]))],
)
def stop_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Stop serving a deployed model.
    """
    raise NotImplementedError("Stop deployment endpoint to be implemented")
