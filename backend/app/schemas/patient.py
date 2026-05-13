"""
Patient & Admission Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PatientBase(BaseModel):
    subject_id: int
    gender: str
    anchor_age: Optional[int] = None
    anchor_year: Optional[int] = None
    anchor_year_group: Optional[str] = None
    dod: Optional[datetime] = None

    class Config:
        from_attributes = True


class PatientList(BaseModel):
    patients: List[PatientBase]
    total: int
    page: int
    per_page: int


class AdmissionBase(BaseModel):
    hadm_id: int
    subject_id: int
    admittime: Optional[datetime] = None
    dischtime: Optional[datetime] = None
    deathtime: Optional[datetime] = None
    admission_type: Optional[str] = None
    admission_location: Optional[str] = None
    discharge_location: Optional[str] = None
    insurance: Optional[str] = None
    language: Optional[str] = None
    marital_status: Optional[str] = None
    race: Optional[str] = None
    hospital_expire_flag: Optional[int] = 0

    class Config:
        from_attributes = True


class DiagnosisResponse(BaseModel):
    icd_code: Optional[str] = None
    icd_version: Optional[int] = None
    seq_num: Optional[int] = None

    class Config:
        from_attributes = True


class ProcedureResponse(BaseModel):
    icd_code: Optional[str] = None
    icd_version: Optional[int] = None
    seq_num: Optional[int] = None
    chartdate: Optional[datetime] = None

    class Config:
        from_attributes = True


class PrescriptionResponse(BaseModel):
    drug: Optional[str] = None
    drug_type: Optional[str] = None
    route: Optional[str] = None
    dose_val_rx: Optional[str] = None
    dose_unit_rx: Optional[str] = None
    starttime: Optional[datetime] = None
    stoptime: Optional[datetime] = None

    class Config:
        from_attributes = True


class LabEventResponse(BaseModel):
    itemid: Optional[int] = None
    charttime: Optional[datetime] = None
    value: Optional[str] = None
    valuenum: Optional[float] = None
    valueuom: Optional[str] = None
    flag: Optional[str] = None

    class Config:
        from_attributes = True


class ICUStayResponse(BaseModel):
    stay_id: int
    first_careunit: Optional[str] = None
    last_careunit: Optional[str] = None
    intime: Optional[datetime] = None
    outtime: Optional[datetime] = None
    los: Optional[float] = None

    class Config:
        from_attributes = True


class AdmissionDetail(AdmissionBase):
    diagnoses: List[DiagnosisResponse] = []
    procedures: List[ProcedureResponse] = []
    prescriptions: List[PrescriptionResponse] = []
    icu_stays: List[ICUStayResponse] = []
    lab_events_count: int = 0


class PatientDetail(PatientBase):
    admissions: List[AdmissionBase] = []
    total_admissions: int = 0
