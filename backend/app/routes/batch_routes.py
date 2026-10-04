"""
Batch prediction API routes.
"""
import io
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.authentication.rbac import require_roles
from backend.app.configuration.settings import settings
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.schemas.batch_schema import BatchJobResponse
from backend.app.services.batch_service import BatchService
from backend.app.services.storage_service import StorageService

router = APIRouter()
logger = logging.getLogger("modelforge.routes.batch")


from backend.app.services.audit_service import log_audit_event
from backend.app.services.notification_service import create_notification


@router.post(
    "/{deployment_id}/validate-csv",
    summary="Validate CSV dataset against deployment schema before submitting",
    operation_id="validate_batch_csv",
)
def validate_batch_csv(
    deployment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted for validation")
    svc = BatchService(db)
    return svc.validate_csv(deployment_id, file.file)


@router.post(
    "/{deployment_id}/predict-batch",
    response_model=BatchJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit batch CSV for prediction",
    operation_id="submit_batch",
)
def submit_batch_prediction(
    deployment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    svc = BatchService(db)
    job = svc.submit_batch_job(deployment_id, file.file, file.filename, current_user.id)

    log_audit_event(
        db=db,
        action="BATCH_SUBMIT",
        resource="batch",
        resource_id=str(job.id),
        user=current_user,
        metadata={"deployment_id": deployment_id, "filename": file.filename},
    )
    create_notification(
        db=db,
        title="Batch Job Completed" if job.status.value == "COMPLETED" else "Batch Job Submitted",
        message=f"Batch job #{job.id} for deployment #{deployment_id} ({job.total_records} records) finished with status {job.status.value}.",
        notification_type="SUCCESS" if job.status.value == "COMPLETED" else "INFO",
        link="/batch",
    )
    return job


@router.get(
    "/jobs",
    response_model=List[BatchJobResponse],
    summary="List batch prediction jobs",
    operation_id="list_batch_jobs",
)
def list_batch_jobs(
    deployment_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    svc = BatchService(db)
    return svc.list_jobs(deployment_id=deployment_id, skip=skip, limit=limit)


@router.get(
    "/{deployment_id}/jobs",
    response_model=List[BatchJobResponse],
    summary="List batch prediction jobs for a deployment",
    operation_id="list_deployment_batch_jobs",
)
def list_deployment_batch_jobs(
    deployment_id: int,
    db: Session = Depends(get_db),
):
    svc = BatchService(db)
    return svc.get_jobs_for_deployment(deployment_id)


@router.get(
    "/jobs/{job_id}",
    response_model=BatchJobResponse,
    summary="Get batch job status",
    operation_id="get_batch_status",
)
def get_batch_job_status(job_id: int, db: Session = Depends(get_db)):
    svc = BatchService(db)
    return svc.get_job_status(job_id)


@router.get(
    "/jobs/{job_id}/download",
    summary="Download batch results CSV",
    operation_id="download_batch_results",
)
def download_batch_results(job_id: int, db: Session = Depends(get_db)):
    svc = BatchService(db)
    job = svc.get_job_status(job_id)
    if not job.output_file_url:
        raise HTTPException(status_code=404, detail="Results not yet available")

    storage = StorageService()
    try:
        content = storage.read_artifact(settings.MINIO_BUCKET_BATCH, job.output_file_url)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Batch results artifact not found")
    except Exception as exc:
        logger.error("Failed to read batch results artifact: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve batch results")

    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=results_{job_id}.csv"},
    )
