"""
Inference Service
Load model and perform predictions with SHAP explanations
"""
import numpy as np
import logging
from .feature_engineering import build_feature_vector

logger = logging.getLogger(__name__)

# Feature names used by the model
FEATURE_NAMES = [
    "age", "gender_male", "los_hours", "prev_admissions",
    "num_diagnoses", "num_procedures", "num_prescriptions",
    "icu_flag", "icu_los", "num_lab_events", "lab_avg_value",
    "lab_min_value", "lab_max_value", "abnormal_labs", "hospital_expire_flag"
]


def predict_readmission(subject_id: int, hadm_id: int) -> dict:
    """Predict 30-day readmission probability."""
    # Build feature vector
    features = build_feature_vector(subject_id, hadm_id)
    if not features:
        return {"error": "Could not build feature vector"}
    
    # Try loading model from MLflow, fallback to heuristic
    try:
        import mlflow
        from ..config import ml_settings
        mlflow.set_tracking_uri(ml_settings.MLFLOW_TRACKING_URI)
        
        model = mlflow.sklearn.load_model(f"models:/{ml_settings.MODEL_NAME}/Production")
        feature_array = np.array([[features.get(f, 0) for f in FEATURE_NAMES]])
        probability = float(model.predict_proba(feature_array)[0][1])
        
        # SHAP values
        try:
            import shap
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(feature_array)
            if isinstance(shap_values, list):
                shap_vals = shap_values[1][0]
            else:
                shap_vals = shap_values[0]
            shap_dict = {FEATURE_NAMES[i]: round(float(shap_vals[i]), 4) for i in range(len(FEATURE_NAMES))}
        except Exception:
            shap_dict = _heuristic_shap(features)
        
    except Exception as e:
        logger.warning(f"MLflow model not available, using heuristic: {e}")
        probability = _heuristic_prediction(features)
        shap_dict = _heuristic_shap(features)
    
    # Risk level
    if probability > 0.7:
        risk_level = "HIGH"
    elif probability > 0.3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Top features by absolute SHAP importance
    sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
    top_features = [
        {"feature": f, "value": features.get(f, 0), "importance": round(abs(v), 4)}
        for f, v in sorted_features[:8]
    ]
    
    return {
        "probability": round(probability, 4),
        "risk_level": risk_level,
        "shap_values": shap_dict,
        "top_features": top_features
    }


def _heuristic_prediction(features: dict) -> float:
    """Simple heuristic-based prediction when no ML model is available."""
    score = 0.15
    score += min(features.get("num_diagnoses", 0) * 0.025, 0.25)
    score += min(features.get("prev_admissions", 0) * 0.08, 0.24)
    score += 0.12 if features.get("icu_flag", 0) == 1 else 0
    score += min(features.get("abnormal_labs", 0) * 0.005, 0.1)
    score += 0.05 if features.get("age", 0) > 70 else 0
    score += min(features.get("num_prescriptions", 0) * 0.008, 0.1)
    
    if features.get("los_hours", 0) > 168:  # > 7 days
        score += 0.08
    
    return max(0.01, min(0.99, score))


def _heuristic_shap(features: dict) -> dict:
    """Generate pseudo-SHAP values based on feature importance heuristics."""
    weights = {
        "age": 0.08, "gender_male": 0.03, "los_hours": 0.12,
        "prev_admissions": 0.18, "num_diagnoses": 0.15, "num_procedures": 0.06,
        "num_prescriptions": 0.08, "icu_flag": 0.10, "icu_los": 0.07,
        "num_lab_events": 0.04, "lab_avg_value": 0.02, "lab_min_value": 0.01,
        "lab_max_value": 0.01, "abnormal_labs": 0.06, "hospital_expire_flag": 0.01
    }
    return {f: round(weights.get(f, 0.01) * (1 if features.get(f, 0) > 0 else -0.5), 4) for f in FEATURE_NAMES}
