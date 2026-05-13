"""
Training Pipeline - Full ML training with MLflow tracking
Trains Logistic Regression, Random Forest, and XGBoost models
"""
import logging
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

logger = logging.getLogger(__name__)

FEATURE_COLS = [
    "age", "gender_male", "los_hours", "prev_admissions",
    "num_diagnoses", "num_procedures", "num_prescriptions",
    "icu_flag", "icu_los", "num_lab_events", "lab_avg_value",
    "lab_min_value", "lab_max_value", "abnormal_labs", "hospital_expire_flag"
]


def train_models(df: pd.DataFrame) -> dict:
    """Train multiple models and select the best one."""
    logger.info(f"Training with {len(df)} samples")
    
    # Prepare data
    X = df[FEATURE_COLS].fillna(0).values
    y = df["readmit_30d"].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
    }
    
    try:
        from xgboost import XGBClassifier
        models["XGBoost"] = XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss')
    except ImportError:
        logger.warning("XGBoost not available, skipping")
    
    results = {}
    best_model_name = None
    best_auc = 0
    
    for name, model in models.items():
        logger.info(f"Training {name}...")
        
        if name == "LogisticRegression":
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_prob = model.predict_proba(X_test_scaled)[:, 1] if len(np.unique(y_test)) > 1 else np.zeros(len(y_test))
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1] if len(np.unique(y_test)) > 1 else np.zeros(len(y_test))
        
        metrics = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
            "f1": round(f1_score(y_test, y_pred, zero_division=0), 4),
        }
        
        try:
            metrics["roc_auc"] = round(roc_auc_score(y_test, y_prob), 4)
        except ValueError:
            metrics["roc_auc"] = 0.5
        
        results[name] = metrics
        logger.info(f"  {name}: AUC={metrics['roc_auc']}, F1={metrics['f1']}")
        
        # Track with MLflow
        try:
            import mlflow
            from ..config import ml_settings
            mlflow.set_tracking_uri(ml_settings.MLFLOW_TRACKING_URI)
            mlflow.set_experiment("readmission_prediction")
            
            with mlflow.start_run(run_name=name):
                mlflow.log_params({"model": name, "n_features": len(FEATURE_COLS)})
                mlflow.log_metrics(metrics)
                mlflow.sklearn.log_model(model, "model")
        except Exception as e:
            logger.warning(f"MLflow logging failed: {e}")
        
        if metrics["roc_auc"] > best_auc:
            best_auc = metrics["roc_auc"]
            best_model_name = name
    
    return {
        "best_model": best_model_name,
        "best_auc": best_auc,
        "all_results": results
    }
