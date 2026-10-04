"""
Service layer for orchestrating real-time prediction and async logging.
"""
import os
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.configuration.settings import settings
from backend.app.models.deployment import DeploymentStatus
from backend.app.models.prediction_log import PredictionLog
from backend.app.repositories.deployment_repository import (
    DeploymentRepository,
    PredictionLogRepository,
)
from backend.app.repositories.model_repository import ModelRepository, ModelVersionRepository
from backend.app.schemas.inference_schema import PredictionResponse
from backend.app.services.storage_service import StorageService
from inference.engine.cache import ModelCache
from inference.engine.runner import ModelRunner
from inference.validators.schema_validator import FeatureSchemaValidator

logger = logging.getLogger("modelforge.services.inference")

# Module-level singleton — shared across all requests
_model_cache = ModelCache(max_size=settings.MODEL_CACHE_MAX_SIZE)
_model_runner = ModelRunner(_model_cache)


class InferenceService:
    def __init__(self, db: Session):
        self.db = db
        self.deploy_repo = DeploymentRepository(db)
        self.log_repo = PredictionLogRepository(db)
        self.version_repo = ModelVersionRepository(db)
        self.model_repo = ModelRepository(db)
        self.storage = StorageService()

    def predict(self, deployment_id: int, features: Dict[str, Any], client_ip: str) -> PredictionResponse:
        # 1. Look up deployment
        deployment = self.deploy_repo.get(deployment_id)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        if deployment.status != DeploymentStatus.DEPLOYED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Deployment is {deployment.status.value}, not DEPLOYED",
            )

        # 2. Get model version and model metadata
        version = self.version_repo.get(deployment.current_version_id)
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model version not found",
            )
        model = self.model_repo.get(deployment.model_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found",
            )

        # 3. Ensure artifact is cached locally
        artifact_basename = os.path.basename(version.artifact_path)
        local_dir = os.path.join(settings.MODEL_STORAGE_DIR, model.name, f"v{version.version_number}")
        local_path = os.path.join(local_dir, artifact_basename)

        try:
            if not os.path.exists(local_path):
                os.makedirs(local_dir, exist_ok=True)
                self.storage.download_artifact(
                    settings.MINIO_BUCKET_MODELS, version.artifact_path, local_path
                )
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model artifact not found: {version.artifact_path}",
            )
        except Exception as exc:
            logger.error("Failed to retrieve model artifact: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve model artifact",
            )

        # 4. Validate features against schema
        is_valid, errors = FeatureSchemaValidator.validate(features, version.feature_schema)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Feature validation failed: {'; '.join(errors)}",
            )

        # 5. Run prediction
        try:
            prediction, probabilities, latency_ms = _model_runner.execute_prediction(
                deployment_id=deployment_id,
                version_id=version.id,
                artifact_path=local_path,
                framework=model.framework.value,
                features=features,
            )
        except NotImplementedError as exc:
            logger.warning("Framework not implemented: %s", exc)
            self._log_prediction_failure(deployment_id, version.id, features, 501, str(exc), client_ip)
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=str(exc),
            )
        except ValueError as exc:
            logger.warning("Invalid prediction input or configuration: %s", exc)
            self._log_prediction_failure(deployment_id, version.id, features, 400, str(exc), client_ip)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )
        except Exception as exc:
            logger.error("Inference execution failed: %s", exc, exc_info=True)
            self._log_prediction_failure(deployment_id, version.id, features, 500, str(exc), client_ip)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Model execution failed: {str(exc)}",
            )

        # 6. Log prediction
        try:
            log_entry = PredictionLog(
                deployment_id=deployment_id,
                model_version_id=version.id,
                input_features=features,
                prediction_output=prediction,
                latency_ms=latency_ms,
                status_code=200,
                client_ip=client_ip,
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as exc:
            logger.warning("Failed to log prediction: %s", exc)
            self.db.rollback()

        # 7. Return response
        return PredictionResponse(
            prediction=prediction,
            probabilities=probabilities[0] if probabilities and isinstance(probabilities[0], list) else probabilities,
            model_version=version.version_number,
            latency_ms=round(latency_ms, 2),
            timestamp=datetime.now(timezone.utc),
        )

    def _log_prediction_failure(
        self,
        deployment_id: int,
        version_id: int,
        features: Dict[str, Any],
        status_code: int,
        error_message: str,
        client_ip: str,
    ) -> None:
        try:
            log_entry = PredictionLog(
                deployment_id=deployment_id,
                model_version_id=version_id,
                input_features=features,
                prediction_output={"error": error_message},
                latency_ms=0.0,
                status_code=status_code,
                error_message=error_message[:500],
                client_ip=client_ip,
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as exc:
            logger.warning("Failed to log failed prediction: %s", exc)
            self.db.rollback()

    def get_prediction_logs(self, deployment_id: int, skip: int = 0, limit: int = 100) -> List[PredictionLog]:
        return self.log_repo.get_logs_for_deployment(deployment_id, limit=limit)

    def get_all_prediction_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        deployment_id: Optional[int] = None,
        model_version_id: Optional[int] = None,
        status_code: Optional[int] = None,
    ) -> List[PredictionLog]:
        return self.log_repo.get_all_logs(
            skip=skip,
            limit=limit,
            deployment_id=deployment_id,
            model_version_id=model_version_id,
            status_code=status_code,
        )

    def get_feature_importance(self, deployment_id: int) -> Dict[str, Any]:
        deployment = self.deploy_repo.get(deployment_id)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        version = self.version_repo.get(deployment.current_version_id)
        if not version:
            raise HTTPException(status_code=404, detail="Model version not found")

        model = self.model_repo.get(deployment.model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        artifact_basename = os.path.basename(version.artifact_path)
        local_dir = os.path.join(settings.MODEL_STORAGE_DIR, model.name, f"v{version.version_number}")
        local_path = os.path.join(local_dir, artifact_basename)

        try:
            if not os.path.exists(local_path):
                os.makedirs(local_dir, exist_ok=True)
                self.storage.download_artifact(settings.MINIO_BUCKET_MODELS, version.artifact_path, local_path)
        except Exception as exc:
            logger.warning("Could not download artifact for feature importance: %s", exc)

        cache_key = _model_runner._get_cache_key(deployment_id, version.id)
        adapter = _model_runner.cache.get(cache_key)
        if adapter is None and os.path.exists(local_path):
            try:
                adapter = _model_runner._load_adapter(local_path, model.framework.value)
                _model_runner.cache.put(cache_key, adapter)
            except Exception as exc:
                logger.warning("Could not load adapter for feature importance: %s", exc)

        feature_names = []
        if isinstance(version.feature_schema, dict):
            features_list = version.feature_schema.get("features", [])
            if isinstance(features_list, list):
                feature_names = [f.get("name") for f in features_list if isinstance(f, dict) and "name" in f]
        elif isinstance(version.feature_schema, list):
            feature_names = [f.get("name") for f in version.feature_schema if isinstance(f, dict) and "name" in f]

        importances = adapter.get_feature_importance(feature_names) if adapter else None
        if importances:
            return {
                "supported": True,
                "model_id": model.id,
                "model_name": model.display_name,
                "version": version.version_number,
                "framework": model.framework.value,
                "features": importances,
            }
        return {
            "supported": False,
            "model_id": model.id,
            "model_name": model.display_name,
            "version": version.version_number,
            "message": "Feature importance is not available for this model.",
            "features": [],
        }
