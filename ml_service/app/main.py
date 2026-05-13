"""
ML Service - Main FastAPI Application
Handles prediction inference and model retraining
"""
from fastapi import FastAPI
from .routers import predict, training, monitoring

app = FastAPI(
    title="MIMIC-IV ML Service",
    description="Machine Learning inference and training service",
    version="1.0.0"
)

app.include_router(predict.router)
app.include_router(training.router)
app.include_router(monitoring.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ml-service", "version": "1.0.0"}
