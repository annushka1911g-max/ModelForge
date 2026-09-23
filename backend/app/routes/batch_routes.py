"""
Batch prediction API routes.
"""
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.batch_schema import BatchJobResponse
from backend.app.authentication.rbac import get_current_user, require_roles
from backend.app.models.user import User, UserRole

router = APIRouter()


@router.post(
    "/{deployment_id}/predict-batch",
    response_model=BatchJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER]))],
)
def submit_batch_prediction(
    deployment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a CSV file for asynchronous batch prediction.
    """
    raise NotImplementedError("Batch prediction submission to be implemented")


@router.get("/jobs/{job_id}", response_model=BatchJobResponse)
def get_batch_job_status(job_id: int, db: Session = Depends(get_db)):
    """
    Check the status and progress of a batch prediction job.
    """
    raise NotImplementedError("Batch job status endpoint to be implemented")


@router.get("/jobs/{job_id}/download")
def download_batch_results(job_id: int, db: Session = Depends(get_db)):
    """
    Download the processed CSV containing predictions.
    """
    raise NotImplementedError("Batch download endpoint to be implemented")
