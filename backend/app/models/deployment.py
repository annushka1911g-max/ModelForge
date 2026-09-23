"""
SQLAlchemy Deployment definition.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.base import Base


class DeploymentStatus(str, enum.Enum):
    DEPLOYED = "DEPLOYED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    ROLLING_BACK = "ROLLING_BACK"


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True)
    current_version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="RESTRICT"), nullable=False)
    previous_version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.DEPLOYED, nullable=False, index=True)
    endpoint_path = Column(String(255), nullable=False)
    deployed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    deployed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_rollback_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    model = relationship("Model", back_populates="deployments")
    current_version = relationship("ModelVersion", foreign_keys=[current_version_id])
    previous_version = relationship("ModelVersion", foreign_keys=[previous_version_id])
    deployer = relationship("User", back_populates="deployments")
    prediction_logs = relationship("PredictionLog", back_populates="deployment", cascade="all, delete-orphan")
    batch_jobs = relationship("BatchJob", back_populates="deployment", cascade="all, delete-orphan")
