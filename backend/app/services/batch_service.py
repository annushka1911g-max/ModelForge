"""
Service layer for managing batch prediction jobs via CSV.
"""
from typing import BinaryIO
from sqlalchemy.orm import Session
from backend.app.models.batch_job import BatchJob


class BatchService:
    def __init__(self, db: Session):
        self.db = db

    def submit_batch_job(self, deployment_id: int, file_obj: BinaryIO, filename: str, user_id: int) -> BatchJob:
        """
        Stores uploaded CSV, creates a BatchJob record, and triggers background processing.
        """
        raise NotImplementedError("BatchService.submit_batch_job to be implemented")

    def process_batch_job(self, job_id: int) -> None:
        """
        Processes batch rows in chunks, executes model inference, and writes output CSV.
        """
        raise NotImplementedError("BatchService.process_batch_job to be implemented")

    def get_job_status(self, job_id: int) -> BatchJob:
        """
        Returns status and progress of a batch job.
        """
        raise NotImplementedError("BatchService.get_job_status to be implemented")
