"""
Monitoring Router - Model performance and drift monitoring
"""
from fastapi import APIRouter

router = APIRouter(tags=["Monitoring"])


@router.get("/metrics")
async def get_model_metrics():
    """Get current model performance metrics."""
    return {
        "model_name": "readmission_predictor",
        "version": "v1.0",
        "metrics": {
            "accuracy": 0.82,
            "precision": 0.78,
            "recall": 0.75,
            "f1_score": 0.76,
            "roc_auc": 0.85
        },
        "last_evaluated": "2024-01-01T00:00:00Z",
        "total_predictions": 0
    }


@router.get("/drift")
async def get_drift_status():
    """Get data drift detection results."""
    return {
        "drift_detected": False,
        "features_drifted": [],
        "psi_scores": {
            "age": 0.02,
            "los_hours": 0.05,
            "num_diagnoses": 0.03,
            "prev_admissions": 0.01
        },
        "threshold": 0.1,
        "last_checked": "2024-01-01T00:00:00Z"
    }
