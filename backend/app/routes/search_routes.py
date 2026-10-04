"""
Global Search API routes across models, deployments, experiments, and versions.
"""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.authentication.rbac import get_current_user
from backend.app.database.session import get_db
from backend.app.models.deployment import Deployment
from backend.app.models.experiment import Experiment
from backend.app.models.model import Model
from backend.app.models.model_version import ModelVersion
from backend.app.models.user import User

router = APIRouter()


@router.get("/", summary="Global platform search", operation_id="global_search")
def global_search(
    q: str = Query(..., min_length=1, description="Search term across entities"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, List[Dict[str, Any]]]:
    term = q.strip().lower()

    # Search Models
    models = (
        db.query(Model)
        .filter((Model.name.ilike(f"%{term}%")) | (Model.display_name.ilike(f"%{term}%")) | (Model.description.ilike(f"%{term}%")))
        .limit(10)
        .all()
    )
    model_results = [
        {
            "id": m.id,
            "title": m.display_name,
            "subtitle": f"{m.name} • {m.framework.value}",
            "type": "model",
            "url": f"/models/{m.id}",
        }
        for m in models
    ]

    # Search Deployments
    deployments = (
        db.query(Deployment)
        .join(Model, Deployment.model_id == Model.id)
        .filter((Model.name.ilike(f"%{term}%")) | (Model.display_name.ilike(f"%{term}%")) | (Deployment.endpoint_path.ilike(f"%{term}%")))
        .limit(10)
        .all()
    )
    deployment_results = [
        {
            "id": d.id,
            "title": f"Deployment #{d.id} ({d.model.display_name if d.model else 'Model'})",
            "subtitle": f"Status: {d.status.value} • Endpoint: {d.endpoint_path}",
            "type": "deployment",
            "url": "/deployments",
        }
        for d in deployments
    ]

    # Search Experiments
    experiments = (
        db.query(Experiment)
        .filter((Experiment.name.ilike(f"%{term}%")) | (Experiment.description.ilike(f"%{term}%")))
        .limit(10)
        .all()
    )
    experiment_results = [
        {
            "id": e.id,
            "title": e.name,
            "subtitle": f"Status: {e.status.value} • {e.dataset_name or 'No dataset'}",
            "type": "experiment",
            "url": "/experiments",
        }
        for e in experiments
    ]

    return {
        "models": model_results,
        "deployments": deployment_results,
        "experiments": experiment_results,
    }
