"""
Storage service for ModelForge.

The local filesystem backend is used for development/MVP deployments.
Artifacts are stored under STORAGE_DIR and organized by bucket/object name.

The service keeps the same public interface previously used by the MinIO
implementation so the rest of ModelForge does not need to change.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import BinaryIO

from backend.app.configuration.settings import settings

logger = logging.getLogger("modelforge.services.storage")


class StorageService:
    def __init__(self):
        self.base_dir = Path(settings.STORAGE_DIR).expanduser().resolve()

        self.models_bucket = settings.MINIO_BUCKET_MODELS
        self.batch_bucket = settings.MINIO_BUCKET_BATCH

        self.models_dir = self.base_dir / self.models_bucket
        self.batch_dir = self.base_dir / self.batch_bucket

        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.batch_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Storage initialized using local filesystem: %s",
            self.base_dir,
        )

    def _bucket_dir(self, bucket: str) -> Path:
        """
        Return the filesystem directory corresponding to a logical bucket.
        """
        if bucket == self.models_bucket:
            directory = self.models_dir
        elif bucket == self.batch_bucket:
            directory = self.batch_dir
        else:
            directory = self.base_dir / bucket

        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def _safe_object_path(self, bucket: str, object_name: str) -> Path:
        """
        Convert bucket + object name into a safe filesystem path.

        Prevents object names containing '..' from escaping STORAGE_DIR.
        """
        bucket_dir = self._bucket_dir(bucket)

        # Normalize separators so S3-style paths work on macOS.
        object_name = object_name.replace("\\", "/").lstrip("/")

        target = (bucket_dir / object_name).resolve()

        if bucket_dir.resolve() not in target.parents and target != bucket_dir.resolve():
            raise ValueError("Invalid storage object path")

        return target

    def ensure_buckets(self) -> None:
        """
        Create storage directories.

        Kept for compatibility with the previous MinIO implementation.
        """
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.batch_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Local storage buckets ready: %s, %s",
            self.models_dir,
            self.batch_dir,
        )

    def upload_artifact(
        self,
        file_obj: BinaryIO,
        bucket: str,
        object_name: str,
    ) -> str:
        """
        Store an artifact on the local filesystem.

        Returns the logical object name, preserving the previous API.
        """
        target = self._safe_object_path(bucket, object_name)

        target.parent.mkdir(parents=True, exist_ok=True)

        file_obj.seek(0)

        with target.open("wb") as destination:
            shutil.copyfileobj(file_obj, destination)

        logger.info(
            "Uploaded artifact to %s/%s",
            bucket,
            object_name,
        )

        return object_name

    def download_artifact(
        self,
        bucket: str,
        object_name: str,
        target_path: str,
    ) -> str:
        """
        Copy an artifact from local artifact storage to the model cache.
        """
        source = self._safe_object_path(bucket, object_name)
        target = Path(target_path).expanduser().resolve()

        if not source.exists():
            raise FileNotFoundError(
                f"Artifact not found: {bucket}/{object_name}"
            )

        target.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source, target)

        logger.info(
            "Downloaded artifact %s/%s -> %s",
            bucket,
            object_name,
            target,
        )

        return str(target)

    def delete_artifact(
        self,
        bucket: str,
        object_name: str,
    ) -> bool:
        """
        Delete an artifact from local storage.
        """
        target = self._safe_object_path(bucket, object_name)

        try:
            if target.exists():
                target.unlink()

                logger.info(
                    "Deleted artifact %s/%s",
                    bucket,
                    object_name,
                )

            return True

        except OSError as exc:
            logger.error(
                "Failed to delete artifact %s/%s: %s",
                bucket,
                object_name,
                exc,
            )
            return False

    def artifact_exists(self, bucket: str, object_name: str) -> bool:
        """
        Check if an artifact exists in storage.
        """
        try:
            target = self._safe_object_path(bucket, object_name)
            return target.is_file()
        except Exception:
            return False

    def read_artifact(self, bucket: str, object_name: str) -> bytes:
        """
        Read the binary content of an artifact from local storage.
        """
        target = self._safe_object_path(bucket, object_name)
        if not target.exists():
            raise FileNotFoundError(
                f"Artifact not found: {bucket}/{object_name}"
            )
        return target.read_bytes()
