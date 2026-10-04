"""
Service layer for Model and ModelVersion catalog management.
"""
import hashlib
import logging
from typing import Any, BinaryIO, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.configuration.settings import settings
from backend.app.models.model import Model
from backend.app.models.model_version import ModelVersion
from backend.app.repositories.model_repository import ModelRepository, ModelVersionRepository
from backend.app.schemas.model_schema import ModelCreate, ModelUpdate
from backend.app.services.storage_service import StorageService

logger = logging.getLogger("modelforge.services.model")


class ModelService:
    def __init__(self, db: Session):
        self.db = db
        self.model_repo = ModelRepository(db)
        self.version_repo = ModelVersionRepository(db)
        self.storage = StorageService()

    # ── Model CRUD ────────────────────────────────────────────────────────────

    def create_model(self, model_in: ModelCreate, user_id: int) -> Model:
        existing = self.model_repo.get_by_name(model_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A model with this name already exists",
            )
        model = Model(
            name=model_in.name,
            display_name=model_in.display_name,
            description=model_in.description,
            framework=model_in.framework,
            task_type=model_in.task_type,
            created_by=user_id,
        )
        return self.model_repo.create(model)

    def list_models(self, skip: int = 0, limit: int = 100) -> List[Model]:
        return self.model_repo.get_all(skip=skip, limit=limit)

    def get_model(self, model_id: int) -> Model:
        model = self.model_repo.get(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return model

    def update_model(self, model_id: int, model_update: ModelUpdate) -> Model:
        model = self.get_model(model_id)
        if model_update.display_name is not None:
            model.display_name = model_update.display_name
        if model_update.description is not None:
            model.description = model_update.description
        return self.model_repo.update(model)

    # ── Model Version Management ──────────────────────────────────────────────

    def upload_version(
        self,
        model_id: int,
        file_obj: BinaryIO,
        filename: str,
        feature_schema: Dict[str, Any],
        training_metrics: Optional[Dict[str, Any]],
        changelog: Optional[str],
        user_id: int,
    ) -> ModelVersion:
        model = self.get_model(model_id)

        # Read file bytes for hash and size
        file_bytes = file_obj.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        file_size = len(file_bytes)

        # Determine next version number
        latest = self.version_repo.get_latest_version(model_id)
        next_version = (latest.version_number + 1) if latest else 1

        # Upload to MinIO
        import io
        object_name = f"{model.name}/v{next_version}/{filename}"
        self.storage.upload_artifact(
            io.BytesIO(file_bytes),
            settings.MINIO_BUCKET_MODELS,
            object_name,
        )

        # Create version record
        version = ModelVersion(
            model_id=model_id,
            version_number=next_version,
            artifact_path=object_name,
            file_hash=file_hash,
            file_size_bytes=file_size,
            feature_schema=feature_schema,
            target_schema=None,
            training_metrics=training_metrics,
            changelog=changelog,
            created_by=user_id,
        )
        created = self.version_repo.create(version)
        logger.info(
            "Created version v%d for model %s (hash=%s, size=%d)",
            next_version, model.name, file_hash[:12], file_size,
        )
        return created

    def get_versions(self, model_id: int) -> List[ModelVersion]:
        self.get_model(model_id)  # Ensure model exists
        return self.version_repo.get_versions_for_model(model_id)

    def get_version(self, model_id: int, version_id: int) -> ModelVersion:
        version = self.version_repo.get(version_id)
        if not version or version.model_id != model_id:
            raise HTTPException(status_code=404, detail="Model version not found")
        return version
