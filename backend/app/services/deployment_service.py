"""
Service layer for Model Deployment lifecycle, status management, and rollback.
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.deployment import Deployment, DeploymentStatus
from backend.app.repositories.deployment_repository import DeploymentRepository
from backend.app.repositories.model_repository import ModelRepository, ModelVersionRepository

logger = logging.getLogger("modelforge.services.deployment")


class DeploymentService:
    def __init__(self, db: Session):
        self.db = db
        self.model_repo = ModelRepository(db)
        self.version_repo = ModelVersionRepository(db)
        self.deploy_repo = DeploymentRepository(db)

    def deploy_version(self, model_id: int, version_id: int, user_id: int) -> Deployment:
        """Deploy or re-deploy a model version."""
        model = self.model_repo.get(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        version = self.version_repo.get(version_id)
        if not version or version.model_id != model_id:
            raise HTTPException(status_code=404, detail="Model version not found for this model")

        # Check for existing deployment for this model
        existing = self.deploy_repo.get_by_model_id(model_id)
        if existing:
            # Invalidate cache for previous version
            try:
                from backend.app.services.inference_service import _model_runner
                _model_runner.invalidate_cache(existing.id, existing.current_version_id)
            except Exception:
                pass

            existing.previous_version_id = existing.current_version_id
            existing.current_version_id = version_id
            existing.status = DeploymentStatus.DEPLOYED
            existing.deployed_by = user_id
            existing.deployed_at = datetime.now(timezone.utc)
            deployment = self.deploy_repo.update(existing)
            logger.info("Re-deployed model %d to version %d", model_id, version_id)
        else:
            deployment = Deployment(
                model_id=model_id,
                current_version_id=version_id,
                status=DeploymentStatus.DEPLOYED,
                endpoint_path=f"/api/v1/deployments/0/predict",  # temp
                deployed_by=user_id,
                deployed_at=datetime.now(timezone.utc),
            )
            deployment = self.deploy_repo.create(deployment)
            deployment.endpoint_path = f"/api/v1/deployments/{deployment.id}/predict"
            deployment = self.deploy_repo.update(deployment)
            logger.info("Created deployment %d for model %d version %d", deployment.id, model_id, version_id)

        return deployment

    def stop_deployment(self, deployment_id: int, user_id: int) -> Deployment:
        deployment = self._get_deployment_or_404(deployment_id)
        if deployment.status == DeploymentStatus.STOPPED:
            raise HTTPException(status_code=400, detail="Deployment is already stopped")
        
        # Invalidate cache when stopping
        try:
            from backend.app.services.inference_service import _model_runner
            _model_runner.invalidate_cache(deployment.id, deployment.current_version_id)
        except Exception:
            pass

        deployment.status = DeploymentStatus.STOPPED
        return self.deploy_repo.update(deployment)

    def restart_deployment(self, deployment_id: int, user_id: int) -> Deployment:
        deployment = self._get_deployment_or_404(deployment_id)
        if deployment.status == DeploymentStatus.DEPLOYED:
            raise HTTPException(status_code=400, detail="Deployment is already running")
        deployment.status = DeploymentStatus.DEPLOYED
        deployment.deployed_at = datetime.now(timezone.utc)
        return self.deploy_repo.update(deployment)

    def rollback_version(self, deployment_id: int, target_version_id: Optional[int], user_id: int) -> Deployment:
        deployment = self._get_deployment_or_404(deployment_id)

        if target_version_id:
            target = self.version_repo.get(target_version_id)
            if not target or target.model_id != deployment.model_id:
                raise HTTPException(status_code=404, detail="Target version not found for this model")
        elif deployment.previous_version_id:
            target_version_id = deployment.previous_version_id
        else:
            raise HTTPException(status_code=400, detail="No previous version to roll back to")

        # Invalidate model cache for old version
        try:
            from backend.app.services.inference_service import _model_runner
            _model_runner.invalidate_cache(deployment_id, deployment.current_version_id)
        except Exception:
            pass

        deployment.previous_version_id = deployment.current_version_id
        deployment.current_version_id = target_version_id
        deployment.status = DeploymentStatus.DEPLOYED
        deployment.last_rollback_at = datetime.now(timezone.utc)
        deployment.deployed_at = datetime.now(timezone.utc)
        updated = self.deploy_repo.update(deployment)
        logger.info("Rolled back deployment %d to version %d", deployment_id, target_version_id)
        return updated

    def list_deployments(self) -> List[Deployment]:
        return self.deploy_repo.get_all()

    def get_deployment(self, deployment_id: int) -> Deployment:
        return self._get_deployment_or_404(deployment_id)

    def _get_deployment_or_404(self, deployment_id: int) -> Deployment:
        deployment = self.deploy_repo.get(deployment_id)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        return deployment
