"""
Configuration module for ModelForge backend.
"""
from pathlib import Path
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for locating .env across different working directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "ModelForge"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Security & JWT
    SECRET_KEY: str = "temporary_dev_secret_key_please_override_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # PostgreSQL Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "modelforge_user"
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: str = "modelforge_db"
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str) and v.strip():
            return v
        values = info.data
        user = values.get("POSTGRES_USER", "postgres")
        password = values.get("POSTGRES_PASSWORD")
        server = values.get("POSTGRES_SERVER", "localhost")
        port = values.get("POSTGRES_PORT", 5432)
        db = values.get("POSTGRES_DB", "modelforge_db")

        auth = f"{user}:{password}" if password else user
        return f"postgresql://{auth}@{server}:{port}/{db}"

    # MinIO Object Storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ROOT_USER: str = "minio_admin"
    MINIO_ROOT_PASSWORD: str = "minio_secure_admin_password_placeholder"
    MINIO_BUCKET_MODELS: str = "models"
    MINIO_BUCKET_BATCH: str = "batch-jobs"
    MINIO_USE_SSL: bool = False

    # Inference & Cache
    MODEL_CACHE_MAX_SIZE: int = 5
    MODEL_STORAGE_DIR: str = "/tmp/modelforge/models_cache"

    # Monitoring & Telemetry
    PROMETHEUS_METRICS_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=(str(ENV_FILE), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
