"""
Clinical Data Models - MIMIC-IV clinical tables
Includes: DiagnosisICD, ProcedureICD, Prescription, LabEvent, DLabItem, ICUStay
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class DLabItem(Base):
    __tablename__ = "d_labitems"
    
    itemid = Column(Integer, primary_key=True, index=True)
    label = Column(String(200))
    fluid = Column(String(100))
    category = Column(String(100))


class DiagnosisICD(Base):
    __tablename__ = "diagnoses_icd"
    
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("patients.subject_id"), nullable=False)
    hadm_id = Column(Integer, ForeignKey("admissions.hadm_id"), nullable=False, index=True)
    seq_num = Column(Integer)
    icd_code = Column(String(10))
    icd_version = Column(Integer)
    
    admission = relationship("Admission", back_populates="diagnoses")


class ProcedureICD(Base):
    __tablename__ = "procedures_icd"
    
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("patients.subject_id"), nullable=False)
    hadm_id = Column(Integer, ForeignKey("admissions.hadm_id"), nullable=False, index=True)
    seq_num = Column(Integer)
    icd_code = Column(String(10))
    icd_version = Column(Integer)
    chartdate = Column(DateTime)
    
    admission = relationship("Admission", back_populates="procedures")


class Prescription(Base):
    __tablename__ = "prescriptions"
    
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("patients.subject_id"), nullable=False)
    hadm_id = Column(Integer, ForeignKey("admissions.hadm_id"), nullable=False, index=True)
    pharmacy_id = Column(Integer)
    poe_id = Column(String(25))
    poe_seq = Column(Integer)
    starttime = Column(DateTime)
    stoptime = Column(DateTime)
    drug_type = Column(String(20))
    drug = Column(String(255))
    formulary_drug_cd = Column(String(120))
    gsn = Column(String(200))
    ndc = Column(String(25))
    prod_strength = Column(String(120))
    form_rx = Column(String(25))
    dose_val_rx = Column(String(120))
    dose_unit_rx = Column(String(120))
    form_val_disp = Column(String(120))
    form_unit_disp = Column(String(120))
    doses_per_24_hrs = Column(Float)
    route = Column(String(50))
    
    admission = relationship("Admission", back_populates="prescriptions")


class LabEvent(Base):
    __tablename__ = "labevents"
    
    labevent_id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("patients.subject_id"), nullable=False)
    hadm_id = Column(Integer, ForeignKey("admissions.hadm_id"), index=True)
    specimen_id = Column(Integer)
    itemid = Column(Integer, ForeignKey("d_labitems.itemid"))
    charttime = Column(DateTime)
    storetime = Column(DateTime)
    value = Column(String(200))
    valuenum = Column(Float)
    valueuom = Column(String(20))
    ref_range_lower = Column(Float)
    ref_range_upper = Column(Float)
    flag = Column(String(10))
    priority = Column(String(10))
    comments = Column(Text)
    
    admission = relationship("Admission", back_populates="lab_events")
    lab_item = relationship("DLabItem")


class ICUStay(Base):
    __tablename__ = "icustays"
    
    stay_id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("patients.subject_id"), nullable=False)
    hadm_id = Column(Integer, ForeignKey("admissions.hadm_id"), nullable=False, index=True)
    first_careunit = Column(String(50))
    last_careunit = Column(String(50))
    intime = Column(DateTime)
    outtime = Column(DateTime)
    los = Column(Float)
    
    admission = relationship("Admission", back_populates="icu_stays")
