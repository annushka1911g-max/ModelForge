"""
Storage service interface for MinIO / S3 object interactions.
"""
from typing import BinaryIO
from backend.app.configuration.settings import settings


class StorageService:
    def __init__(self):
        self.endpoint = settings.MINIO_ENDPOINT
        self.models_bucket = settings.MINIO_BUCKET_MODELS
        self.batch_bucket = settings.MINIO_BUCKET_BATCH

    def upload_artifact(self, file_obj: BinaryIO, bucket: str, object_name: str) -> str:
        """
        Uploads a binary artifact to object storage and returns the object path.
        """
        raise NotImplementedError("StorageService.upload_artifact to be implemented")

    def download_artifact(self, bucket: str, object_name: str, target_path: str) -> str:
        """
        Downloads an artifact to local cache path.
        """
        raise NotImplementedError("StorageService.download_artifact to be implemented")

    def delete_artifact(self, bucket: str, object_name: str) -> bool:
        """
        Deletes an artifact from object storage.
        """
        raise NotImplementedError("StorageService.delete_artifact to be implemented")
