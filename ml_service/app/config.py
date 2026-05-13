"""ML Service Configuration"""
import os

class MLSettings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mimic_prediction")
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    MODEL_NAME: str = "readmission_predictor"

ml_settings = MLSettings()
