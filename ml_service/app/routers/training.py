"""
Training Router - Model retraining endpoints
"""
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Training"])

training_status = {"status": "idle", "progress": 0, "message": ""}


class RetrainResponse(BaseModel):
    status: str
    message: str


@router.post("/retrain", response_model=RetrainResponse)
async def retrain_model(background_tasks: BackgroundTasks):
    """Trigger model retraining in background."""
    if training_status["status"] == "running":
        return RetrainResponse(status="already_running", message="Training already in progress")
    
    background_tasks.add_task(run_training_pipeline)
    training_status["status"] = "running"
    training_status["progress"] = 0
    
    return RetrainResponse(status="started", message="Retraining pipeline started")


@router.get("/retrain/status")
async def get_training_status():
    """Get current training status."""
    return training_status


async def run_training_pipeline():
    """Execute the training pipeline."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        training_status["message"] = "Loading data..."
        training_status["progress"] = 10
        
        from ..services.feature_engineering import build_training_dataset
        df = build_training_dataset()
        
        if df.empty:
            training_status["status"] = "failed"
            training_status["message"] = "No training data available"
            return
        
        training_status["message"] = "Training models..."
        training_status["progress"] = 40
        
        from ..services.training_pipeline import train_models
        results = train_models(df)
        
        training_status["status"] = "completed"
        training_status["progress"] = 100
        training_status["message"] = f"Training completed. Best model: {results.get('best_model', 'N/A')}"
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        training_status["status"] = "failed"
        training_status["message"] = str(e)
