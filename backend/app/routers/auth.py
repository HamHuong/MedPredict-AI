"""
Auth Router - Login / Logout / Current User
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.auth import LoginRequest, UserResponse
from ..utils.security import verify_password
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=UserResponse)
async def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and create session."""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Create session
    request.session["user_id"] = user.user_id
    request.session["role"] = user.role
    
    return user


@router.post("/logout")
async def logout(request: Request):
    """Destroy session."""
    request.session.clear()
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user
