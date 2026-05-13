"""
MIMIC-IV Clinical Prediction System - Backend API
Main FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .routers import auth, users, patients, predictions, admin

app = FastAPI(
    title="MIMIC-IV Clinical Prediction API",
    description="API for 30-day hospital readmission prediction system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Session middleware for cookie-based auth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, max_age=settings.SESSION_MAX_AGE)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(patients.router)
app.include_router(predictions.router)
app.include_router(admin.router)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "backend-api", "version": "1.0.0"}
