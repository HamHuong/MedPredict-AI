"""
Admission Model - MIMIC-IV admissions table
"""
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Admission(Base):
    __tablename__ = "admissions"
    
    hadm_id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("patients.subject_id"), nullable=False, index=True)
    admittime = Column(DateTime, nullable=False)
    dischtime = Column(DateTime)
    deathtime = Column(DateTime)
    admission_type = Column(String(50))
    admit_provider_id = Column(String(10))
    admission_location = Column(String(60))
    discharge_location = Column(String(60))
    insurance = Column(String(255))
    language = Column(String(10))
    marital_status = Column(String(30))
    race = Column(String(80))
    edregtime = Column(DateTime)
    edouttime = Column(DateTime)
    hospital_expire_flag = Column(SmallInteger, default=0)
    
    # Relationships
    patient = relationship("Patient", back_populates="admissions")
    diagnoses = relationship("DiagnosisICD", back_populates="admission", lazy="dynamic")
    procedures = relationship("ProcedureICD", back_populates="admission", lazy="dynamic")
    prescriptions = relationship("Prescription", back_populates="admission", lazy="dynamic")
    lab_events = relationship("LabEvent", back_populates="admission", lazy="dynamic")
    icu_stays = relationship("ICUStay", back_populates="admission", lazy="dynamic")
