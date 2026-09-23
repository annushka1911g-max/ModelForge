"""
SQLAlchemy ModelVersion definition.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, Text, DateTime, Enum, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database.base import Base


class VersionStatus(str, enum.Enum):
    READY = "READY"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    artifact_path = Column(String(512), nullable=False)
    file_hash = Column(String(64), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    feature_schema = Column(JSON, nullable=False)
    target_schema = Column(JSON, nullable=True)
    training_metrics = Column(JSON, nullable=True)
    status = Column(Enum(VersionStatus), default=VersionStatus.READY, nullable=False)
    changelog = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("model_id", "version_number", name="uq_model_version"),
    )

    # Relationships
    model = relationship("Model", back_populates="versions")
    creator = relationship("User", back_populates="model_versions")
    prediction_logs = relationship("PredictionLog", back_populates="model_version")
    batch_jobs = relationship("BatchJob", back_populates="model_version")
