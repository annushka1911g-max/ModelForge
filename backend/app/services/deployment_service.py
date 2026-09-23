"""
Service layer for Model Deployment lifecycle and rollback.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.deployment import Deployment, DeploymentStatus


class DeploymentService:
    def __init__(self, db: Session):
        self.db = db

    def deploy_version(self, model_id: int, version_id: int, user_id: int) -> Deployment:
        """
        Deploys a specified model version and sets it active.
        """
        raise NotImplementedError("DeploymentService.deploy_version to be implemented")

    def rollback_version(self, deployment_id: int, user_id: int) -> Deployment:
        """
        Rolls back active deployment to its previous version.
        """
        raise NotImplementedError("DeploymentService.rollback_version to be implemented")

    def stop_deployment(self, deployment_id: int, user_id: int) -> Deployment:
        """
        Stops model serving for a deployment.
        """
        raise NotImplementedError("DeploymentService.stop_deployment to be implemented")

    def list_deployments(self) -> List[Deployment]:
        """
        Lists all deployments with their current status.
        """
        raise NotImplementedError("DeploymentService.list_deployments to be implemented")
