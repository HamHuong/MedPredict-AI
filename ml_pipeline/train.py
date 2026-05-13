"""
ML Pipeline - Main Training Entrypoint
Standalone script to train readmission prediction models
Usage: python train.py
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mimic_prediction")
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

FEATURE_COLS = [
    "age", "gender_male", "los_hours", "prev_admissions",
    "num_diagnoses", "num_procedures", "num_prescriptions",
    "icu_flag", "icu_los", "num_lab_events", "abnormal_labs"
]


def extract_features(engine):
    """Extract features and labels from database."""
    logger.info("Extracting features from database...")
    
    with engine.connect() as conn:
        # Get all admissions
        admissions = pd.read_sql(text("""
            SELECT a.hadm_id, a.subject_id, p.gender, p.anchor_age,
                   a.admittime, a.dischtime, a.hospital_expire_flag
            FROM admissions a
            JOIN patients p ON a.subject_id = p.subject_id
            WHERE a.dischtime IS NOT NULL
            ORDER BY a.subject_id, a.admittime
        """), conn)
    
    if admissions.empty:
        logger.error("No admissions found!")
        return pd.DataFrame()
    
    logger.info(f"Found {len(admissions)} admissions")
    admissions['admittime'] = pd.to_datetime(admissions['admittime'])
    admissions['dischtime'] = pd.to_datetime(admissions['dischtime'])
    
    records = []
    with engine.connect() as conn:
        for _, row in admissions.iterrows():
            hid = int(row['hadm_id'])
            sid = int(row['subject_id'])
            
            los_hours = (row['dischtime'] - row['admittime']).total_seconds() / 3600
            prev = conn.execute(text(
                "SELECT COUNT(*) FROM admissions WHERE subject_id = :s AND admittime < :t"
            ), {"s": sid, "t": row['admittime']}).scalar() or 0
            
            n_diag = conn.execute(text("SELECT COUNT(*) FROM diagnoses_icd WHERE hadm_id = :h"), {"h": hid}).scalar() or 0
            n_proc = conn.execute(text("SELECT COUNT(*) FROM procedures_icd WHERE hadm_id = :h"), {"h": hid}).scalar() or 0
            n_presc = conn.execute(text("SELECT COUNT(*) FROM prescriptions WHERE hadm_id = :h"), {"h": hid}).scalar() or 0
            
            icu = conn.execute(text("SELECT COUNT(*), COALESCE(SUM(los),0) FROM icustays WHERE hadm_id = :h"), {"h": hid}).fetchone()
            n_labs = conn.execute(text("SELECT COUNT(*) FROM labevents WHERE hadm_id = :h"), {"h": hid}).scalar() or 0
            n_abn = conn.execute(text("SELECT COUNT(*) FROM labevents WHERE hadm_id = :h AND flag = 'abnormal'"), {"h": hid}).scalar() or 0
            
            records.append({
                "hadm_id": hid, "subject_id": sid,
                "age": row['anchor_age'], "gender_male": 1 if row['gender'] == 'M' else 0,
                "los_hours": round(los_hours, 2), "prev_admissions": prev,
                "num_diagnoses": n_diag, "num_procedures": n_proc, "num_prescriptions": n_presc,
                "icu_flag": 1 if icu[0] > 0 else 0, "icu_los": float(icu[1]),
                "num_lab_events": n_labs, "abnormal_labs": n_abn,
                "admittime": row['admittime'], "dischtime": row['dischtime']
            })
    
    df = pd.DataFrame(records)
    
    # Generate readmission labels
    df['readmit_30d'] = 0
    for sid, group in df.groupby('subject_id'):
        group = group.sort_values('admittime')
        indices = group.index.tolist()
        for i in range(len(indices) - 1):
            days_diff = (df.loc[indices[i+1], 'admittime'] - df.loc[indices[i], 'dischtime']).days
            if 0 <= days_diff <= 30:
                df.loc[indices[i], 'readmit_30d'] = 1
    
    logger.info(f"Dataset: {len(df)} samples, {df['readmit_30d'].sum()} readmissions ({df['readmit_30d'].mean()*100:.1f}%)")
    return df


def train_and_evaluate(df):
    """Train models and evaluate."""
    X = df[FEATURE_COLS].fillna(0).values
    y = df['readmit_30d'].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42,
        stratify=y if len(np.unique(y)) > 1 else None
    )
    
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    models = {
        "LogisticRegression": (LogisticRegression(max_iter=1000, random_state=42), True),
        "RandomForest": (RandomForestClassifier(n_estimators=100, random_state=42), False),
    }
    
    try:
        from xgboost import XGBClassifier
        models["XGBoost"] = (XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss'), False)
    except ImportError:
        logger.warning("XGBoost not installed, skipping")
    
    best_name, best_auc = None, 0
    
    # Try MLflow
    use_mlflow = False
    try:
        # pyrefly: ignore [missing-import]
        import mlflow
        mlflow.set_tracking_uri(MLFLOW_URI)
        mlflow.set_experiment("readmission_prediction")
        use_mlflow = True
        logger.info(f"MLflow tracking at {MLFLOW_URI}")
    except Exception:
        logger.warning("MLflow not available, logging locally only")
    
    for name, (model, use_scaled) in models.items():
        logger.info(f"\nTraining {name}...")
        
        Xt = X_train_s if use_scaled else X_train
        Xe = X_test_s if use_scaled else X_test
        
        model.fit(Xt, y_train)
        y_pred = model.predict(Xe)
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
        }
        
        try:
            y_prob = model.predict_proba(Xe)[:, 1]
            metrics["roc_auc"] = roc_auc_score(y_test, y_prob)
        except:
            metrics["roc_auc"] = 0.5
        
        logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall: {metrics['recall']:.4f}")
        logger.info(f"  F1: {metrics['f1']:.4f}")
        logger.info(f"  ROC-AUC: {metrics['roc_auc']:.4f}")
        
        if use_mlflow:
            try:
                with mlflow.start_run(run_name=name):
                    mlflow.log_params({"model": name, "n_samples": len(df), "n_features": len(FEATURE_COLS)})
                    mlflow.log_metrics({k: round(v, 4) for k, v in metrics.items()})
                    mlflow.sklearn.log_model(model, "model")
            except Exception as e:
                logger.warning(f"MLflow logging failed: {e}")
        
        if metrics["roc_auc"] > best_auc:
            best_auc = metrics["roc_auc"]
            best_name = name
    
    logger.info(f"\n{'='*50}")
    logger.info(f"Best Model: {best_name} (AUC={best_auc:.4f})")
    logger.info(f"{'='*50}")


def main():
    logger.info("=" * 60)
    logger.info("ML Training Pipeline — Readmission Prediction")
    logger.info("=" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection OK")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return
    
    df = extract_features(engine)
    if df.empty:
        logger.error("No data extracted. Please import MIMIC-IV data first.")
        return
    
    train_and_evaluate(df)
    logger.info("\nTraining pipeline complete!")


if __name__ == "__main__":
    main()
