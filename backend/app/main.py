"""
MIMIC-IV Clinical Prediction System - Backend API
Main FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .routers import auth, users, patients, predictions, admin
from .database import engine, SessionLocal
from .models.user import User
from .utils.security import hash_password

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


@app.on_event("startup")
def create_default_users():
    """Create default admin and doctor users on startup if they don't exist."""
    db = SessionLocal()
    try:
        # Check and create/update admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                password_hash=hash_password("admin123"),
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin_user)
        else:
            # Update password hash to ensure compatibility
            admin_user.password_hash = hash_password("admin123")
        
        # Check and create/update doctor user
        doctor_user = db.query(User).filter(User.username == "doctor").first()
        if not doctor_user:
            doctor_user = User(
                username="doctor",
                password_hash=hash_password("doctor123"),
                full_name="Dr. Nguyễn Văn A",
                role="doctor",
                is_active=True
            )
            db.add(doctor_user)
        else:
            doctor_user.password_hash = hash_password("doctor123")
        
        db.commit()
        print("✓ Default users created/updated successfully")
    except Exception as e:
        print(f"Warning: Could not create default users: {e}")
        db.rollback()
    finally:
        db.close()


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "backend-api", "version": "1.0.0"}
