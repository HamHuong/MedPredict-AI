"""
Prediction Schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    subject_id: int
    hadm_id: int


class PredictionResponse(BaseModel):
    prediction_id: int
    hadm_id: int
    subject_id: int
    probability: float
    risk_level: str
    shap_values: Optional[Dict[str, Any]] = None
    top_features: Optional[List[Dict[str, Any]]] = None
    predicted_at: Optional[datetime] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None

    class Config:
        from_attributes = True


class PredictionHistory(BaseModel):
    predictions: List[PredictionResponse]
    total: int
    page: int
    per_page: int
