"""
Deployment lifecycle API routes.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.authentication.rbac import get_current_user, require_roles
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.schemas.deployment_schema import (
    DeploymentCreate,
    DeploymentResponse,
    RollbackRequest,
)
from backend.app.services.deployment_service import DeploymentService

router = APIRouter()
logger = logging.getLogger("modelforge.routes.deployments")


@router.post(
    "/",
    response_model=DeploymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Deploy a model version",
    operation_id="deploy_model",
)
def deploy_model(
    deployment_in: DeploymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = DeploymentService(db)
    return svc.deploy_version(deployment_in.model_id, deployment_in.current_version_id, current_user.id)


@router.get("/", response_model=List[DeploymentResponse], summary="List deployments", operation_id="list_deployments")
def list_deployments(db: Session = Depends(get_db)):
    svc = DeploymentService(db)
    return svc.list_deployments()


@router.get("/{deployment_id}", response_model=DeploymentResponse, summary="Get deployment", operation_id="get_deployment")
def get_deployment(deployment_id: int, db: Session = Depends(get_db)):
    svc = DeploymentService(db)
    return svc.get_deployment(deployment_id)


@router.post("/{deployment_id}/stop", response_model=DeploymentResponse, summary="Stop deployment", operation_id="stop_deployment")
def stop_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = DeploymentService(db)
    return svc.stop_deployment(deployment_id, current_user.id)


@router.post("/{deployment_id}/restart", response_model=DeploymentResponse, summary="Restart deployment", operation_id="restart_deployment")
def restart_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = DeploymentService(db)
    return svc.restart_deployment(deployment_id, current_user.id)


@router.post("/{deployment_id}/rollback", response_model=DeploymentResponse, summary="Rollback deployment", operation_id="rollback_deployment")
def rollback_deployment(
    deployment_id: int,
    rollback_in: RollbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = DeploymentService(db)
    return svc.rollback_version(deployment_id, rollback_in.target_version_id, current_user.id)
