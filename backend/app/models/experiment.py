"""
SQLAlchemy Experiment model for lightweight experiment tracking.
"""
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database.base import Base


class ExperimentStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"), nullable=True, index=True)
    parameters = Column(JSON, default=dict, nullable=False)
    metrics = Column(JSON, default=dict, nullable=False)
    dataset_name = Column(String(255), nullable=True)
    dataset_version = Column(String(100), nullable=True)
    status = Column(Enum(ExperimentStatus), default=ExperimentStatus.RUNNING, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    model = relationship("Model", backref="experiments")
    creator = relationship("User", backref="experiments")
