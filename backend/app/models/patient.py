"""
Patient Model - MIMIC-IV patients table
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ..database import Base


class Patient(Base):
    __tablename__ = "patients"
    
    subject_id = Column(Integer, primary_key=True, index=True)
    gender = Column(String(1), nullable=False)
    anchor_age = Column(Integer)
    anchor_year = Column(Integer)
    anchor_year_group = Column(String(20))
    dod = Column(DateTime, nullable=True)
    
    # Relationships
    admissions = relationship("Admission", back_populates="patient", lazy="dynamic")
