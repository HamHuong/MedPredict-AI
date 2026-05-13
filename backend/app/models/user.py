"""
User Model - Authentication & Authorization
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(10), nullable=False, default="doctor")  # admin, doctor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
