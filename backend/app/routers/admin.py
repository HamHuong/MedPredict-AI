"""
Admin Router - ML Model management, retraining, dashboard stats
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..database import get_db
from ..models import MLModel, RetrainingJob, Prediction, Patient, Admission
from ..models.user import User
from ..schemas.ml_model import (
    MLModelResponse, MLModelStageUpdate, 
    RetrainRequest, RetrainingJobResponse, DashboardStats
)
from ..middleware.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get dashboard overview statistics."""
    today = datetime.utcnow().date()
    
    total_patients = db.query(func.count(Patient.subject_id)).scalar() or 0
    total_admissions = db.query(func.count(Admission.hadm_id)).scalar() or 0
    total_predictions = db.query(func.count(Prediction.prediction_id)).scalar() or 0
    
    predictions_today = db.query(func.count(Prediction.prediction_id)).filter(
        func.date(Prediction.predicted_at) == today
    ).scalar() or 0
    
    high_risk = db.query(func.count(Prediction.prediction_id)).filter(
        Prediction.risk_level == "HIGH"
    ).scalar() or 0
    
    medium_risk = db.query(func.count(Prediction.prediction_id)).filter(
        Prediction.risk_level == "MEDIUM"
    ).scalar() or 0
    
    low_risk = db.query(func.count(Prediction.prediction_id)).filter(
        Prediction.risk_level == "LOW"
    ).scalar() or 0
    
    active_model = db.query(MLModel).filter(MLModel.stage == "production").first()
    
    # Recent predictions
    recent = db.query(Prediction).order_by(Prediction.predicted_at.desc()).limit(5).all()
    recent_list = [{
        "prediction_id": p.prediction_id,
        "subject_id": p.subject_id,
        "hadm_id": p.hadm_id,
        "probability": p.probability,
        "risk_level": p.risk_level,
        "predicted_at": p.predicted_at.isoformat() if p.predicted_at else None
    } for p in recent]
    
    return DashboardStats(
        total_patients=total_patients,
        total_admissions=total_admissions,
        total_predictions=total_predictions,
        predictions_today=predictions_today,
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        low_risk_count=low_risk,
        active_model=MLModelResponse.model_validate(active_model) if active_model else None,
        recent_predictions=recent_list
    )


@router.get("/models", response_model=list[MLModelResponse])
async def list_models(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """List all ML models."""
    models = db.query(MLModel).order_by(MLModel.created_at.desc()).all()
    return [MLModelResponse.model_validate(m) for m in models]


@router.put("/models/{model_id}/stage", response_model=MLModelResponse)
async def update_model_stage(
    model_id: int,
    stage_update: MLModelStageUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Update model stage (Admin only)."""
    model = db.query(MLModel).filter(MLModel.model_id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if stage_update.stage not in ("staging", "production", "archived"):
        raise HTTPException(status_code=400, detail="Invalid stage")
    
    # If promoting to production, demote current production model
    if stage_update.stage == "production":
        current_prod = db.query(MLModel).filter(MLModel.stage == "production").all()
        for m in current_prod:
            m.stage = "archived"
    
    model.stage = stage_update.stage
    db.commit()
    db.refresh(model)
    return MLModelResponse.model_validate(model)


@router.post("/retrain", response_model=RetrainingJobResponse)
async def trigger_retrain(
    retrain_req: RetrainRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Trigger model retraining (Admin only)."""
    job = RetrainingJob(
        triggered_by=current_user.user_id,
        trigger_reason=retrain_req.trigger_reason,
        status="pending",
        started_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # In production, this would trigger the ML pipeline asynchronously
    # For now, mark as completed with a simulated delay
    job.status = "running"
    db.commit()
    
    return RetrainingJobResponse.model_validate(job)


@router.get("/retrain/jobs", response_model=list[RetrainingJobResponse])
async def list_retrain_jobs(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """List retraining jobs."""
    jobs = db.query(RetrainingJob).order_by(RetrainingJob.started_at.desc()).all()
    return [RetrainingJobResponse.model_validate(j) for j in jobs]


@router.get("/metrics")
async def get_system_metrics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get system monitoring metrics."""
    # Prediction distribution by risk level
    risk_distribution = db.query(
        Prediction.risk_level,
        func.count(Prediction.prediction_id)
    ).group_by(Prediction.risk_level).all()
    
    # Predictions over last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    daily_predictions = db.query(
        func.date(Prediction.predicted_at),
        func.count(Prediction.prediction_id)
    ).filter(Prediction.predicted_at >= week_ago).group_by(
        func.date(Prediction.predicted_at)
    ).all()
    
    # Active model metrics
    active_model = db.query(MLModel).filter(MLModel.stage == "production").first()
    
    return {
        "risk_distribution": {r[0]: r[1] for r in risk_distribution},
        "daily_predictions": [{"date": str(d[0]), "count": d[1]} for d in daily_predictions],
        "active_model_metrics": active_model.metrics if active_model else {},
        "total_models": db.query(func.count(MLModel.model_id)).scalar() or 0,
    }
