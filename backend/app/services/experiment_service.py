"""
Service layer for Experiment Tracking.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.app.models.experiment import Experiment, ExperimentStatus
from backend.app.schemas.experiment_schema import ExperimentCreate, ExperimentUpdate

logger = logging.getLogger("modelforge.services.experiments")


class ExperimentService:
    def __init__(self, db: Session):
        self.db = db

    def create_experiment(self, experiment_in: ExperimentCreate, user_id: int) -> Experiment:
        exp = Experiment(
            name=experiment_in.name.strip(),
            description=experiment_in.description.strip() if experiment_in.description else None,
            model_id=experiment_in.model_id,
            parameters=experiment_in.parameters or {},
            metrics=experiment_in.metrics or {},
            dataset_name=experiment_in.dataset_name,
            dataset_version=experiment_in.dataset_version,
            status=experiment_in.status,
            created_by=user_id,
            created_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc) if experiment_in.status in [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED] else None,
        )
        self.db.add(exp)
        self.db.commit()
        self.db.refresh(exp)
        logger.info("Created experiment %d: %s", exp.id, exp.name)
        return exp

    def list_experiments(
        self,
        skip: int = 0,
        limit: int = 100,
        model_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Experiment]:
        query = self.db.query(Experiment)
        if model_id is not None:
            query = query.filter(Experiment.model_id == model_id)
        if status:
            query = query.filter(Experiment.status == status.upper())
        if search:
            query = query.filter(Experiment.name.ilike(f"%{search}%"))

        return query.order_by(Experiment.created_at.desc()).offset(skip).limit(limit).all()

    def get_experiment(self, experiment_id: int) -> Experiment:
        exp = self.db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not exp:
            raise HTTPException(status_code=404, detail="Experiment not found")
        return exp

    def update_experiment(self, experiment_id: int, update_in: ExperimentUpdate) -> Experiment:
        exp = self.get_experiment(experiment_id)
        update_data = update_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(exp, field, value)

        if "status" in update_data and update_data["status"] in [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED, ExperimentStatus.CANCELLED]:
            if not exp.completed_at:
                exp.completed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(exp)
        logger.info("Updated experiment %d", exp.id)
        return exp

    def compare_experiments(self, experiment_ids: List[int]) -> Dict[str, Any]:
        if not experiment_ids:
            return {"experiments": [], "parameter_keys": [], "metric_keys": []}

        experiments = (
            self.db.query(Experiment)
            .filter(Experiment.id.in_(experiment_ids))
            .order_by(Experiment.id.asc())
            .all()
        )

        all_param_keys = set()
        all_metric_keys = set()
        for exp in experiments:
            if isinstance(exp.parameters, dict):
                all_param_keys.update(exp.parameters.keys())
            if isinstance(exp.metrics, dict):
                all_metric_keys.update(exp.metrics.keys())

        return {
            "experiments": experiments,
            "parameter_keys": sorted(list(all_param_keys)),
            "metric_keys": sorted(list(all_metric_keys)),
        }
