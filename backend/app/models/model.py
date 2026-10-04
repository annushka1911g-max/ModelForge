"""
SQLAlchemy Model group definition.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.app.database.base import Base


class MLFramework(str, enum.Enum):
    SCIKIT_LEARN = "SCIKIT_LEARN"
    XGBOOST = "XGBOOST"
    TENSORFLOW = "TENSORFLOW"
    PYTORCH = "PYTORCH"


class TaskType(str, enum.Enum):
    CLASSIFICATION = "CLASSIFICATION"
    REGRESSION = "REGRESSION"


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    framework = Column(Enum(MLFramework), nullable=False, index=True)
    task_type = Column(Enum(TaskType), nullable=False)
    tags = Column(JSON, default=list, nullable=True)
    is_starred = Column(Boolean, default=False, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", back_populates="models")
    versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="model", cascade="all, delete-orphan")
