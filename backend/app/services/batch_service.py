"""
Service layer for managing batch prediction jobs via CSV.
"""
import io
import logging
import os
from datetime import datetime, timezone
from typing import BinaryIO, List, Optional

import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.configuration.settings import settings
from backend.app.models.batch_job import BatchJob, BatchStatus
from backend.app.models.deployment import DeploymentStatus
from backend.app.repositories.deployment_repository import (
    BatchJobRepository,
    DeploymentRepository,
)
from backend.app.repositories.model_repository import ModelVersionRepository
from backend.app.services.storage_service import StorageService

logger = logging.getLogger("modelforge.services.batch")
CHUNK_SIZE = 500


class BatchService:
    def __init__(self, db: Session):
        self.db = db
        self.deploy_repo = DeploymentRepository(db)
        self.batch_repo = BatchJobRepository(db)
        self.version_repo = ModelVersionRepository(db)
        self.storage = StorageService()

    def submit_batch_job(
        self, deployment_id: int, file_obj: BinaryIO, filename: str, user_id: int
    ) -> BatchJob:
        deployment = self.deploy_repo.get(deployment_id)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        if deployment.status != DeploymentStatus.DEPLOYED:
            raise HTTPException(
                status_code=400,
                detail=f"Deployment is {deployment.status.value}, not DEPLOYED",
            )

        # Read and upload CSV
        csv_bytes = file_obj.read()
        file_obj.seek(0)

        object_name = f"batch/{deployment_id}/{filename}"
        self.storage.upload_artifact(io.BytesIO(csv_bytes), settings.MINIO_BUCKET_BATCH, object_name)

        # Count rows
        row_count = csv_bytes.decode("utf-8").strip().count("\n")  # header + data - 1
        if row_count < 1:
            raise HTTPException(status_code=400, detail="CSV must have at least one data row")

        job = BatchJob(
            deployment_id=deployment_id,
            model_version_id=deployment.current_version_id,
            input_file_url=object_name,
            total_records=row_count,
            processed_records=0,
            status=BatchStatus.PENDING,
            created_by=user_id,
        )
        job = self.batch_repo.create(job)

        # Process synchronously for MVP
        self._process(job.id, csv_bytes)
        return self.batch_repo.get(job.id)

    def _process(self, job_id: int, csv_content: bytes) -> None:
        job = self.batch_repo.get(job_id)
        if not job:
            return

        job.status = BatchStatus.PROCESSING
        self.batch_repo.update(job)

        try:
            from backend.app.services.inference_service import _model_runner
            from inference.validators.schema_validator import FeatureSchemaValidator

            deployment = self.deploy_repo.get(job.deployment_id)
            if not deployment:
                raise ValueError("Associated deployment not found")

            version = self.version_repo.get(job.model_version_id)
            if not version:
                raise ValueError("Associated model version not found")

            model = deployment.model
            if not model:
                raise ValueError("Associated model not found")

            # Ensure artifact is local
            artifact_basename = os.path.basename(version.artifact_path)
            local_dir = os.path.join(
                settings.MODEL_STORAGE_DIR, model.name, f"v{version.version_number}"
            )
            local_path = os.path.join(local_dir, artifact_basename)

            if not os.path.exists(local_path):
                os.makedirs(local_dir, exist_ok=True)
                self.storage.download_artifact(
                    settings.MINIO_BUCKET_MODELS, version.artifact_path, local_path
                )

            df = pd.read_csv(io.BytesIO(csv_content))
            if df.empty:
                raise ValueError("CSV contains no data rows")

            # Validate schema using the first record
            first_record = df.iloc[0].to_dict()
            is_valid, validation_errors = FeatureSchemaValidator.validate(first_record, version.feature_schema)
            if not is_valid:
                raise ValueError(f"Feature schema validation failed: {'; '.join(validation_errors)}")

            all_predictions = []
            processed = 0

            for start in range(0, len(df), CHUNK_SIZE):
                chunk = df.iloc[start : start + CHUNK_SIZE]
                features_list = chunk.to_dict(orient="records")

                prediction, _, _ = _model_runner.execute_prediction(
                    deployment_id=job.deployment_id,
                    version_id=job.model_version_id,
                    artifact_path=local_path,
                    framework=model.framework.value,
                    features=features_list,
                )
                all_predictions.extend(
                    prediction if isinstance(prediction, list) else [prediction]
                )
                processed += len(chunk)
                job.processed_records = processed
                self.batch_repo.update(job)

            df["prediction"] = all_predictions
            output_buf = io.BytesIO()
            df.to_csv(output_buf, index=False)
            output_buf.seek(0)

            output_name = f"batch/{job.deployment_id}/results_{job_id}.csv"
            self.storage.upload_artifact(output_buf, settings.MINIO_BUCKET_BATCH, output_name)

            job.output_file_url = output_name
            job.status = BatchStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            self.batch_repo.update(job)
            logger.info("Batch job %d completed: %d records", job_id, processed)

        except Exception as exc:
            logger.error("Batch job %d failed: %s", job_id, exc, exc_info=True)
            job.status = BatchStatus.FAILED
            job.error_message = str(exc)[:500]
            self.batch_repo.update(job)

    def get_job_status(self, job_id: int) -> BatchJob:
        job = self.batch_repo.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Batch job not found")
        return job

    def get_jobs_for_deployment(self, deployment_id: int) -> List[BatchJob]:
        return self.batch_repo.get_jobs_for_deployment(deployment_id)

    def list_jobs(self, deployment_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[BatchJob]:
        if deployment_id is not None:
            return self.batch_repo.get_jobs_for_deployment(deployment_id)
        return self.batch_repo.get_all_jobs(skip=skip, limit=limit)

    def validate_csv(self, deployment_id: int, file_obj: BinaryIO) -> dict:
        deployment = self.deploy_repo.get(deployment_id)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        version = self.version_repo.get(deployment.current_version_id)
        if not version:
            raise HTTPException(status_code=404, detail="Model version not found")

        schema_features = []
        if isinstance(version.feature_schema, dict):
            schema_features = version.feature_schema.get("features", [])
        elif isinstance(version.feature_schema, list):
            schema_features = version.feature_schema

        required_cols = [f.get("name") for f in schema_features if isinstance(f, dict) and f.get("required", True)]
        type_specs = {f.get("name"): f.get("type", "float") for f in schema_features if isinstance(f, dict)}

        csv_bytes = file_obj.read()
        file_obj.seek(0)

        try:
            df = pd.read_csv(io.BytesIO(csv_bytes))
        except Exception as exc:
            return {
                "is_valid": False,
                "total_rows": 0,
                "summary": f"Could not parse CSV: {str(exc)}",
                "missing_columns": required_cols,
                "extra_columns": [],
                "null_counts": {},
                "type_errors": [f"CSV parsing error: {str(exc)}"],
                "preview_rows": [],
            }

        total_rows = len(df)
        missing_columns = [col for col in required_cols if col not in df.columns]
        extra_columns = [col for col in df.columns if col not in type_specs]
        null_counts = {col: int(df[col].isnull().sum()) for col in df.columns if df[col].isnull().sum() > 0}

        type_errors = []
        for col, expected_type in type_specs.items():
            if col in df.columns:
                if expected_type in ["float", "int"]:
                    non_numeric = pd.to_numeric(df[col], errors="coerce").isnull() & df[col].notnull()
                    invalid_count = int(non_numeric.sum())
                    if invalid_count > 0:
                        first_bad = df.loc[non_numeric, col].iloc[0]
                        type_errors.append(f"Invalid: {col} has {invalid_count} non-numeric value(s) (e.g. \"{first_bad}\")")

        is_valid = len(missing_columns) == 0 and len(type_errors) == 0 and total_rows > 0

        summary = "Dataset is valid and ready for batch inference." if is_valid else (
            f"Validation issues: {len(missing_columns)} missing columns, {len(type_errors)} type mismatch(es)."
        )

        preview_rows = df.head(5).to_dict(orient="records")

        return {
            "is_valid": is_valid,
            "total_rows": total_rows,
            "summary": summary,
            "missing_columns": missing_columns,
            "extra_columns": extra_columns,
            "null_counts": null_counts,
            "type_errors": type_errors,
            "preview_rows": preview_rows,
        }
