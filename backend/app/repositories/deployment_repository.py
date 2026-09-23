"""
Repository for Deployment, PredictionLog, and BatchJob entities.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.deployment import Deployment, DeploymentStatus
from backend.app.models.prediction_log import PredictionLog
from backend.app.models.batch_job import BatchJob
from backend.app.repositories.base_repository import BaseRepository


class DeploymentRepository(BaseRepository[Deployment]):
    def __init__(self, db: Session):
        super().__init__(Deployment, db)

    def get_by_model_id(self, model_id: int) -> Optional[Deployment]:
        return self.db.query(Deployment).filter(Deployment.model_id == model_id).first()

    def get_active_deployments(self) -> List[Deployment]:
        return self.db.query(Deployment).filter(Deployment.status == DeploymentStatus.DEPLOYED).all()


class PredictionLogRepository(BaseRepository[PredictionLog]):
    def __init__(self, db: Session):
        super().__init__(PredictionLog, db)

    def get_logs_for_deployment(self, deployment_id: int, limit: int = 100) -> List[PredictionLog]:
        return (
            self.db.query(PredictionLog)
            .filter(PredictionLog.deployment_id == deployment_id)
            .order_by(PredictionLog.created_at.desc())
            .limit(limit)
            .all()
        )


class BatchJobRepository(BaseRepository[BatchJob]):
    def __init__(self, db: Session):
        super().__init__(BatchJob, db)

    def get_jobs_for_deployment(self, deployment_id: int) -> List[BatchJob]:
        return (
            self.db.query(BatchJob)
            .filter(BatchJob.deployment_id == deployment_id)
            .order_by(BatchJob.created_at.desc())
            .all()
        )
