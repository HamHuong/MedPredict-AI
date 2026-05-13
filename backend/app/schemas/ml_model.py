"""
ML Model Schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class MLModelResponse(BaseModel):
    model_id: int
    name: str
    version: Optional[str] = None
    algorithm: Optional[str] = None
    mlflow_run_id: Optional[str] = None
    stage: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MLModelStageUpdate(BaseModel):
    stage: str  # staging, production, archived


class RetrainRequest(BaseModel):
    trigger_reason: Optional[str] = "Manual retrain request"


class RetrainingJobResponse(BaseModel):
    job_id: int
    triggered_by: Optional[int] = None
    trigger_reason: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    new_model_version: Optional[str] = None

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_patients: int = 0
    total_admissions: int = 0
    total_predictions: int = 0
    predictions_today: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    active_model: Optional[MLModelResponse] = None
    recent_predictions: List[Dict[str, Any]] = []
