"""
Patients Router - Patient & Admission data endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Patient, Admission, DiagnosisICD, ProcedureICD, Prescription, LabEvent, ICUStay
from ..schemas.patient import (
    PatientBase, PatientList, PatientDetail, 
    AdmissionBase, AdmissionDetail,
    DiagnosisResponse, ProcedureResponse, PrescriptionResponse,
    LabEventResponse, ICUStayResponse
)
from ..middleware.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.get("/", response_model=PatientList)
async def list_patients(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    gender: str = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """List all patients with pagination and filtering."""
    query = db.query(Patient)
    
    if search:
        query = query.filter(Patient.subject_id == int(search) if search.isdigit() else False)
    if gender:
        query = query.filter(Patient.gender == gender.upper())
    
    total = query.count()
    patients = query.order_by(Patient.subject_id).offset((page - 1) * per_page).limit(per_page).all()
    
    return PatientList(
        patients=[PatientBase.model_validate(p) for p in patients],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{subject_id}", response_model=PatientDetail)
async def get_patient(
    subject_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get patient detail with admissions summary."""
    patient = db.query(Patient).filter(Patient.subject_id == subject_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    admissions = db.query(Admission).filter(
        Admission.subject_id == subject_id
    ).order_by(Admission.admittime.desc()).all()
    
    return PatientDetail(
        **PatientBase.model_validate(patient).model_dump(),
        admissions=[AdmissionBase.model_validate(a) for a in admissions],
        total_admissions=len(admissions)
    )


@router.get("/{subject_id}/admissions")
async def get_patient_admissions(
    subject_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get all admissions for a patient."""
    admissions = db.query(Admission).filter(
        Admission.subject_id == subject_id
    ).order_by(Admission.admittime.desc()).all()
    
    return [AdmissionBase.model_validate(a) for a in admissions]


@router.get("/admissions/{hadm_id}", response_model=AdmissionDetail)
async def get_admission_detail(
    hadm_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get detailed admission including diagnoses, procedures, prescriptions, ICU stays."""
    admission = db.query(Admission).filter(Admission.hadm_id == hadm_id).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
    
    diagnoses = db.query(DiagnosisICD).filter(DiagnosisICD.hadm_id == hadm_id).all()
    procedures = db.query(ProcedureICD).filter(ProcedureICD.hadm_id == hadm_id).all()
    prescriptions = db.query(Prescription).filter(Prescription.hadm_id == hadm_id).limit(50).all()
    icu_stays = db.query(ICUStay).filter(ICUStay.hadm_id == hadm_id).all()
    lab_count = db.query(func.count(LabEvent.labevent_id)).filter(LabEvent.hadm_id == hadm_id).scalar()
    
    return AdmissionDetail(
        **AdmissionBase.model_validate(admission).model_dump(),
        diagnoses=[DiagnosisResponse.model_validate(d) for d in diagnoses],
        procedures=[ProcedureResponse.model_validate(p) for p in procedures],
        prescriptions=[PrescriptionResponse.model_validate(p) for p in prescriptions],
        icu_stays=[ICUStayResponse.model_validate(i) for i in icu_stays],
        lab_events_count=lab_count or 0
    )
