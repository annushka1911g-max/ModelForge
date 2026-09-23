"""
SQLAlchemy BatchJob definition.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.base import Base


class BatchStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(Integer, ForeignKey("deployments.id", ondelete="CASCADE"), nullable=False, index=True)
    model_version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False)
    input_file_url = Column(String(512), nullable=False)
    output_file_url = Column(String(512), nullable=True)
    total_records = Column(Integer, default=0, nullable=False)
    processed_records = Column(Integer, default=0, nullable=False)
    status = Column(Enum(BatchStatus), default=BatchStatus.PENDING, nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    deployment = relationship("Deployment", back_populates="batch_jobs")
    model_version = relationship("ModelVersion", back_populates="batch_jobs")
    creator = relationship("User", back_populates="batch_jobs")
