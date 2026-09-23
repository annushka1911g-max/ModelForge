"""
SQLAlchemy User model and UserRole enum.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from backend.app.database.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    ML_ENGINEER = "ML_ENGINEER"
    VIEWER = "VIEWER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    models = relationship("Model", back_populates="creator")
    model_versions = relationship("ModelVersion", back_populates="creator")
    deployments = relationship("Deployment", back_populates="deployer")
    batch_jobs = relationship("BatchJob", back_populates="creator")
