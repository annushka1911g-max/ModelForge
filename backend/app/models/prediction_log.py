"""
SQLAlchemy PredictionLog definition.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database.base import Base


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    deployment_id = Column(Integer, ForeignKey("deployments.id", ondelete="CASCADE"), nullable=False, index=True)
    model_version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False)
    input_features = Column(JSON, nullable=False)
    prediction_output = Column(JSON, nullable=False)
    latency_ms = Column(Float, nullable=False)
    status_code = Column(Integer, default=200, nullable=False)
    error_message = Column(Text, nullable=True)
    client_ip = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    deployment = relationship("Deployment", back_populates="prediction_logs")
    model_version = relationship("ModelVersion", back_populates="prediction_logs")
