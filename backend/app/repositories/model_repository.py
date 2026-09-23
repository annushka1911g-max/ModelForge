"""
Repository for Model and ModelVersion entities.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.model import Model
from backend.app.models.model_version import ModelVersion
from backend.app.repositories.base_repository import BaseRepository


class ModelRepository(BaseRepository[Model]):
    def __init__(self, db: Session):
        super().__init__(Model, db)

    def get_by_name(self, name: str) -> Optional[Model]:
        return self.db.query(Model).filter(Model.name == name).first()


class ModelVersionRepository(BaseRepository[ModelVersion]):
    def __init__(self, db: Session):
        super().__init__(ModelVersion, db)

    def get_by_model_and_version(self, model_id: int, version_number: int) -> Optional[ModelVersion]:
        return (
            self.db.query(ModelVersion)
            .filter(ModelVersion.model_id == model_id, ModelVersion.version_number == version_number)
            .first()
        )

    def get_latest_version(self, model_id: int) -> Optional[ModelVersion]:
        return (
            self.db.query(ModelVersion)
            .filter(ModelVersion.model_id == model_id)
            .order_by(ModelVersion.version_number.desc())
            .first()
        )

    def get_versions_for_model(self, model_id: int) -> List[ModelVersion]:
        return (
            self.db.query(ModelVersion)
            .filter(ModelVersion.model_id == model_id)
            .order_by(ModelVersion.version_number.desc())
            .all()
        )
