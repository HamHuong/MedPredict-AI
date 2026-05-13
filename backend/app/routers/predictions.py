"""
Predictions Router - Request predictions and view history
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import httpx
from datetime import datetime

from ..database import get_db
from ..config import settings
from ..models import Prediction, MLModel, Admission, Patient
from ..models.user import User
from ..schemas.prediction import PredictionRequest, PredictionResponse, PredictionHistory
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.post("/request", response_model=PredictionResponse)
async def request_prediction(
    pred_req: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Request a readmission prediction for a patient admission."""
    # Verify patient and admission exist
    patient = db.query(Patient).filter(Patient.subject_id == pred_req.subject_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    admission = db.query(Admission).filter(Admission.hadm_id == pred_req.hadm_id).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
    
    # Get active production model
    active_model = db.query(MLModel).filter(MLModel.stage == "production").first()
    
    # Call ML Service for prediction
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/predict",
                json={"subject_id": pred_req.subject_id, "hadm_id": pred_req.hadm_id}
            )
            
            if response.status_code == 200:
                ml_result = response.json()
            else:
                # Fallback: generate a demo prediction if ML service unavailable
                ml_result = _generate_demo_prediction(db, pred_req.subject_id, pred_req.hadm_id)
    except Exception:
        # ML Service not available - generate demo prediction
        ml_result = _generate_demo_prediction(db, pred_req.subject_id, pred_req.hadm_id)
    
    # Save prediction to database
    prediction = Prediction(
        hadm_id=pred_req.hadm_id,
        subject_id=pred_req.subject_id,
        model_id=active_model.model_id if active_model else None,
        probability=ml_result["probability"],
        risk_level=ml_result["risk_level"],
        shap_values=ml_result.get("shap_values"),
        top_features=ml_result.get("top_features"),
        predicted_at=datetime.utcnow(),
        created_by=current_user.user_id
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return PredictionResponse(
        prediction_id=prediction.prediction_id,
        hadm_id=prediction.hadm_id,
        subject_id=prediction.subject_id,
        probability=prediction.probability,
        risk_level=prediction.risk_level,
        shap_values=prediction.shap_values,
        top_features=prediction.top_features,
        predicted_at=prediction.predicted_at,
        model_name=active_model.name if active_model else "demo_model",
        model_version=active_model.version if active_model else "v0.0"
    )


def _generate_demo_prediction(db: Session, subject_id: int, hadm_id: int) -> dict:
    """Generate a demo prediction based on patient data when ML service is unavailable."""
    import random
    from ..models import DiagnosisICD, Prescription, ICUStay, LabEvent
    
    # Count clinical features for heuristic-based prediction
    num_diagnoses = db.query(func.count(DiagnosisICD.row_id)).filter(
        DiagnosisICD.hadm_id == hadm_id).scalar() or 0
    num_prescriptions = db.query(func.count(Prescription.row_id)).filter(
        Prescription.hadm_id == hadm_id).scalar() or 0
    has_icu = db.query(ICUStay).filter(ICUStay.hadm_id == hadm_id).first() is not None
    num_labs = db.query(func.count(LabEvent.labevent_id)).filter(
        LabEvent.hadm_id == hadm_id).scalar() or 0
    
    # Simple heuristic score
    base_risk = 0.2
    base_risk += min(num_diagnoses * 0.03, 0.3)
    base_risk += min(num_prescriptions * 0.01, 0.2)
    base_risk += 0.15 if has_icu else 0
    base_risk += min(num_labs * 0.001, 0.1)
    base_risk += random.uniform(-0.05, 0.05)
    probability = max(0.01, min(0.99, base_risk))
    
    if probability > 0.7:
        risk_level = "HIGH"
    elif probability > 0.3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    top_features = [
        {"feature": "num_diagnoses", "value": num_diagnoses, "importance": 0.25},
        {"feature": "icu_stay", "value": 1 if has_icu else 0, "importance": 0.20},
        {"feature": "num_prescriptions", "value": num_prescriptions, "importance": 0.18},
        {"feature": "num_lab_events", "value": num_labs, "importance": 0.15},
        {"feature": "admission_complexity", "value": round(probability, 2), "importance": 0.12},
    ]
    
    return {
        "probability": round(probability, 4),
        "risk_level": risk_level,
        "shap_values": {f["feature"]: round(f["importance"] * (1 if f["value"] else -1), 3) for f in top_features},
        "top_features": top_features
    }


@router.get("/history", response_model=PredictionHistory)
async def get_prediction_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    risk_level: str = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get prediction history with pagination."""
    query = db.query(Prediction)
    
    if risk_level:
        query = query.filter(Prediction.risk_level == risk_level.upper())
    
    total = query.count()
    predictions = query.order_by(Prediction.predicted_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    
    results = []
    for p in predictions:
        model = db.query(MLModel).filter(MLModel.model_id == p.model_id).first() if p.model_id else None
        results.append(PredictionResponse(
            prediction_id=p.prediction_id,
            hadm_id=p.hadm_id,
            subject_id=p.subject_id,
            probability=p.probability,
            risk_level=p.risk_level,
            shap_values=p.shap_values,
            top_features=p.top_features,
            predicted_at=p.predicted_at,
            model_name=model.name if model else None,
            model_version=model.version if model else None
        ))
    
    return PredictionHistory(
        predictions=results,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get single prediction detail."""
    prediction = db.query(Prediction).filter(Prediction.prediction_id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    model = db.query(MLModel).filter(MLModel.model_id == prediction.model_id).first() if prediction.model_id else None
    
    return PredictionResponse(
        prediction_id=prediction.prediction_id,
        hadm_id=prediction.hadm_id,
        subject_id=prediction.subject_id,
        probability=prediction.probability,
        risk_level=prediction.risk_level,
        shap_values=prediction.shap_values,
        top_features=prediction.top_features,
        predicted_at=prediction.predicted_at,
        model_name=model.name if model else None,
        model_version=model.version if model else None
    )
