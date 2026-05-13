"""
Predict Router - ML prediction endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.inference import predict_readmission

router = APIRouter(tags=["Prediction"])


class PredictRequest(BaseModel):
    subject_id: int
    hadm_id: int


@router.post("/predict")
async def predict(request: PredictRequest):
    """Predict 30-day readmission probability."""
    result = predict_readmission(request.subject_id, request.hadm_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
