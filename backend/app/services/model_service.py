"""
Service layer for Model and ModelVersion catalog management.
"""
from typing import List, Optional, BinaryIO, Dict, Any
from sqlalchemy.orm import Session
from backend.app.schemas.model_schema import ModelCreate, ModelResponse, ModelVersionResponse
from backend.app.models.model import Model
from backend.app.models.model_version import ModelVersion


class ModelService:
    def __init__(self, db: Session):
        self.db = db

    def create_model(self, model_in: ModelCreate, user_id: int) -> Model:
        """
        Registers a new logical model group.
        """
        raise NotImplementedError("ModelService.create_model to be implemented")

    def list_models(self, skip: int = 0, limit: int = 100) -> List[Model]:
        """
        Retrieves all registered models.
        """
        raise NotImplementedError("ModelService.list_models to be implemented")

    def get_model(self, model_id: int) -> Optional[Model]:
        """
        Retrieves a single model by ID.
        """
        raise NotImplementedError("ModelService.get_model to be implemented")

    def upload_version(
        self,
        model_id: int,
        file_obj: BinaryIO,
        filename: str,
        feature_schema: List[Dict[str, Any]],
        training_metrics: Optional[Dict[str, Any]],
        changelog: Optional[str],
        user_id: int,
    ) -> ModelVersion:
        """
        Uploads artifact to MinIO, computes checksum, and creates new ModelVersion.
        """
        raise NotImplementedError("ModelService.upload_version to be implemented")
