"""
Backend Configuration
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/mimic_prediction"
    )
    
    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SESSION_MAX_AGE: int = int(os.getenv("SESSION_MAX_AGE", "3600"))
    
    # ML Service
    ML_SERVICE_URL: str = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
    
    # MLflow
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    class Config:
        env_file = ".env"


settings = Settings()
