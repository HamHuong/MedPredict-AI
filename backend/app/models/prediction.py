"""
Prediction Model
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Prediction(Base):
    __tablename__ = "predictions"
    
    prediction_id = Column(Integer, primary_key=True, index=True)
    hadm_id = Column(Integer, ForeignKey("admissions.hadm_id"))
    subject_id = Column(Integer, ForeignKey("patients.subject_id"))
    model_id = Column(Integer, ForeignKey("ml_models.model_id"))
    probability = Column(Float, nullable=False)
    risk_level = Column(String(10), nullable=False)  # LOW, MEDIUM, HIGH
    shap_values = Column(JSON)
    top_features = Column(JSON)
    predicted_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.user_id"))
    
    # Relationships
    patient = relationship("Patient")
    admission = relationship("Admission")
    model = relationship("MLModel")
    creator = relationship("User")
