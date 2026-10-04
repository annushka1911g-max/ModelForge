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
            tags=model_in.tags or [],
            is_starred=model_in.is_starred or False,
            created_by=user_id,
        )
        return self.model_repo.create(model)

    def list_models(
        self,
        skip: int = 0,
        limit: int = 100,
        framework: Optional[str] = None,
        task_type: Optional[str] = None,
        tag: Optional[str] = None,
        is_starred: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[Model]:
        query = self.db.query(Model)
        if framework:
            query = query.filter(Model.framework == framework.upper())
        if task_type:
            query = query.filter(Model.task_type == task_type.upper())
        if is_starred is not None:
            query = query.filter(Model.is_starred.is_(is_starred))
        if search:
            query = query.filter(
                (Model.name.ilike(f"%{search}%")) | (Model.display_name.ilike(f"%{search}%"))
            )
        models = query.order_by(Model.created_at.desc()).offset(skip).limit(limit).all()
        if tag:
            models = [m for m in models if isinstance(m.tags, list) and tag.lower() in [t.lower() for t in m.tags]]
        return models

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
        if model_update.tags is not None:
            model.tags = model_update.tags
        if model_update.is_starred is not None:
            model.is_starred = model_update.is_starred
        return self.model_repo.update(model)

    def toggle_favorite(self, model_id: int) -> Model:
        model = self.get_model(model_id)
        model.is_starred = not model.is_starred
        return self.model_repo.update(model)

    def add_tag(self, model_id: int, tag: str) -> Model:
        model = self.get_model(model_id)
        tag_clean = tag.strip().lower()
        tags = list(model.tags or [])
        if tag_clean not in tags:
            tags.append(tag_clean)
            model.tags = tags
            self.model_repo.update(model)
        return model

    def remove_tag(self, model_id: int, tag: str) -> Model:
        model = self.get_model(model_id)
        tag_clean = tag.strip().lower()
        tags = [t for t in (model.tags or []) if t != tag_clean]
        model.tags = tags
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

        # Upload to MinIO / Local storage
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

    def compare_versions(self, model_id: int, version_ids: List[int]) -> Dict[str, Any]:
        from backend.app.models.deployment import Deployment, DeploymentStatus

        model = self.get_model(model_id)
        versions = self.version_repo.get_versions_for_model(model_id)
        if version_ids:
            versions = [v for v in versions if v.id in version_ids or v.version_number in version_ids]

        # Check which version is deployed
        active_deployment = (
            self.db.query(Deployment)
            .filter(Deployment.model_id == model_id, Deployment.status == DeploymentStatus.DEPLOYED)
            .first()
        )
        deployed_version_id = active_deployment.current_version_id if active_deployment else None

        metric_names = set()
        version_summaries = []
        best_metrics: Dict[str, Any] = {}

        for v in versions:
            metrics = v.training_metrics or {}
            for k in metrics.keys():
                metric_names.add(k)

            v_info = {
                "id": v.id,
                "version_number": v.version_number,
                "status": v.status.value,
                "artifact_path": v.artifact_path,
                "file_size_bytes": v.file_size_bytes,
                "file_hash": v.file_hash,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "changelog": v.changelog,
                "metrics": metrics,
                "is_deployed": v.id == deployed_version_id,
            }
            version_summaries.append(v_info)

        # Compute best metric values (higher is better for accuracy, precision, recall, f1)
        for m in metric_names:
            best_val = -1.0
            best_ver = None
            for v in version_summaries:
                val = v["metrics"].get(m)
                if isinstance(val, (int, float)) and val > best_val:
                    best_val = float(val)
                    best_ver = v["version_number"]
            if best_ver is not None:
                best_metrics[m] = {"version": best_ver, "value": best_val}

        return {
            "model_id": model.id,
            "model_name": model.display_name,
            "metric_names": sorted(list(metric_names)),
            "versions": version_summaries,
            "best_metrics": best_metrics,
            "deployment_id": active_deployment.id if active_deployment else None,
        }
