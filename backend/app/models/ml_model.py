"""
ML Model & Retraining Job Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from ..database import Base


class MLModel(Base):
    __tablename__ = "ml_models"
    
    model_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    version = Column(String(20))
    algorithm = Column(String(50))
    mlflow_run_id = Column(String(50))
    stage = Column(String(20), default="staging")  # staging, production, archived
    metrics = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())


class RetrainingJob(Base):
    __tablename__ = "retraining_jobs"
    
    job_id = Column(Integer, primary_key=True, index=True)
    triggered_by = Column(Integer, ForeignKey("users.user_id"))
    trigger_reason = Column(String(255))
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    new_model_version = Column(String(20))
    logs = Column(Text)
