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


from backend.app.services.audit_service import log_audit_event
from backend.app.services.notification_service import create_notification


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
    dep = svc.deploy_version(deployment_in.model_id, deployment_in.current_version_id, current_user.id)
    log_audit_event(
        db=db,
        action="DEPLOY",
        resource="deployment",
        resource_id=str(dep.id),
        user=current_user,
        metadata={"model_id": dep.model_id, "version_id": dep.current_version_id},
    )
    create_notification(
        db=db,
        title="Model Deployed",
        message=f"Deployment #{dep.id} is now running version #{dep.current_version_id}.",
        notification_type="SUCCESS",
        link="/deployments",
    )
    return dep


@router.get("/", response_model=List[DeploymentResponse], summary="List deployments", operation_id="list_deployments")
def list_deployments(db: Session = Depends(get_db)):
    svc = DeploymentService(db)
    return svc.list_deployments()


@router.get("/{deployment_id}", response_model=DeploymentResponse, summary="Get deployment", operation_id="get_deployment")
def get_deployment(deployment_id: int, db: Session = Depends(get_db)):
    svc = DeploymentService(db)
    return svc.get_deployment(deployment_id)


@router.get("/{deployment_id}/health-metrics", summary="Get deployment health metrics", operation_id="get_deployment_health_metrics")
def get_deployment_health_metrics(deployment_id: int, db: Session = Depends(get_db)):
    svc = DeploymentService(db)
    return svc.get_health_metrics(deployment_id)


@router.get("/{deployment_id}/history", summary="Get deployment rollback/state history", operation_id="get_deployment_history")
def get_deployment_history(deployment_id: int, db: Session = Depends(get_db)):
    svc = DeploymentService(db)
    return svc.get_deployment_history(deployment_id)


@router.post("/{deployment_id}/stop", response_model=DeploymentResponse, summary="Stop deployment", operation_id="stop_deployment")
def stop_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = DeploymentService(db)
    dep = svc.stop_deployment(deployment_id, current_user.id)
    log_audit_event(
        db=db,
        action="STOP",
        resource="deployment",
        resource_id=str(dep.id),
        user=current_user,
    )
    create_notification(
        db=db,
        title="Deployment Stopped",
        message=f"Deployment #{dep.id} was stopped.",
        notification_type="WARNING",
        link="/deployments",
    )
    return dep


@router.post("/{deployment_id}/restart", response_model=DeploymentResponse, summary="Restart deployment", operation_id="restart_deployment")
def restart_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = DeploymentService(db)
    dep = svc.restart_deployment(deployment_id, current_user.id)
    log_audit_event(
        db=db,
        action="RESTART",
        resource="deployment",
        resource_id=str(dep.id),
        user=current_user,
    )
    create_notification(
        db=db,
        title="Deployment Restarted",
        message=f"Deployment #{dep.id} was restarted.",
        notification_type="INFO",
        link="/deployments",
    )
    return dep


@router.post("/{deployment_id}/rollback", response_model=DeploymentResponse, summary="Rollback deployment", operation_id="rollback_deployment")
def rollback_deployment(
    deployment_id: int,
    rollback_in: RollbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = DeploymentService(db)
    dep = svc.rollback_version(deployment_id, rollback_in.target_version_id, current_user.id)
    log_audit_event(
        db=db,
        action="ROLLBACK",
        resource="deployment",
        resource_id=str(dep.id),
        user=current_user,
        metadata={"target_version_id": dep.current_version_id},
    )
    create_notification(
        db=db,
        title="Rollback Successful",
        message=f"Deployment #{dep.id} was rolled back to version #{dep.current_version_id}.",
        notification_type="SUCCESS",
        link="/deployments",
    )
    return dep
