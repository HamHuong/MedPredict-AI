"""
Feature Engineering Service
Builds feature vectors from MIMIC-IV database tables for ML prediction
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from ..config import ml_settings

engine = create_engine(ml_settings.DATABASE_URL, pool_pre_ping=True)


def build_feature_vector(subject_id: int, hadm_id: int) -> dict:
    """Build a feature vector for a single admission."""
    with engine.connect() as conn:
        # Patient demographics
        patient = conn.execute(text(
            "SELECT gender, anchor_age FROM patients WHERE subject_id = :sid"
        ), {"sid": subject_id}).fetchone()
        
        if not patient:
            return None
        
        # Admission info
        admission = conn.execute(text(
            "SELECT admittime, dischtime, admission_type, insurance, marital_status, race, hospital_expire_flag "
            "FROM admissions WHERE hadm_id = :hid"
        ), {"hid": hadm_id}).fetchone()
        
        if not admission:
            return None
        
        # Length of stay in hours
        los_hours = 0
        if admission[0] and admission[1]:
            los_hours = (admission[1] - admission[0]).total_seconds() / 3600
        
        # Previous admissions count
        prev_admissions = conn.execute(text(
            "SELECT COUNT(*) FROM admissions WHERE subject_id = :sid AND admittime < :atime"
        ), {"sid": subject_id, "atime": admission[0]}).scalar() or 0
        
        # Diagnoses count
        num_diagnoses = conn.execute(text(
            "SELECT COUNT(*) FROM diagnoses_icd WHERE hadm_id = :hid"
        ), {"hid": hadm_id}).scalar() or 0
        
        # Procedures count
        num_procedures = conn.execute(text(
            "SELECT COUNT(*) FROM procedures_icd WHERE hadm_id = :hid"
        ), {"hid": hadm_id}).scalar() or 0
        
        # Prescriptions count
        num_prescriptions = conn.execute(text(
            "SELECT COUNT(*) FROM prescriptions WHERE hadm_id = :hid"
        ), {"hid": hadm_id}).scalar() or 0
        
        # ICU stay info
        icu_info = conn.execute(text(
            "SELECT COUNT(*), COALESCE(SUM(los), 0) FROM icustays WHERE hadm_id = :hid"
        ), {"hid": hadm_id}).fetchone()
        icu_flag = 1 if icu_info[0] > 0 else 0
        icu_los = float(icu_info[1]) if icu_info[1] else 0.0
        
        # Lab events summary
        lab_stats = conn.execute(text(
            "SELECT COUNT(*), AVG(valuenum), MIN(valuenum), MAX(valuenum) "
            "FROM labevents WHERE hadm_id = :hid AND valuenum IS NOT NULL"
        ), {"hid": hadm_id}).fetchone()
        num_labs = lab_stats[0] or 0
        lab_avg = float(lab_stats[1]) if lab_stats[1] else 0.0
        lab_min = float(lab_stats[2]) if lab_stats[2] else 0.0
        lab_max = float(lab_stats[3]) if lab_stats[3] else 0.0
        
        # Abnormal lab flag count
        abnormal_labs = conn.execute(text(
            "SELECT COUNT(*) FROM labevents WHERE hadm_id = :hid AND flag = 'abnormal'"
        ), {"hid": hadm_id}).scalar() or 0
        
        features = {
            "age": patient[1] if patient[1] else 65,
            "gender_male": 1 if patient[0] == 'M' else 0,
            "los_hours": round(los_hours, 2),
            "prev_admissions": prev_admissions,
            "num_diagnoses": num_diagnoses,
            "num_procedures": num_procedures,
            "num_prescriptions": num_prescriptions,
            "icu_flag": icu_flag,
            "icu_los": round(icu_los, 2),
            "num_lab_events": num_labs,
            "lab_avg_value": round(lab_avg, 2),
            "lab_min_value": round(lab_min, 2),
            "lab_max_value": round(lab_max, 2),
            "abnormal_labs": abnormal_labs,
            "hospital_expire_flag": admission[6] if admission[6] else 0,
        }
        
        return features


def build_training_dataset() -> pd.DataFrame:
    """Build full training dataset with readmission labels."""
    with engine.connect() as conn:
        # Get all admissions with patient info
        query = text("""
            SELECT a.hadm_id, a.subject_id, p.gender, p.anchor_age,
                   a.admittime, a.dischtime, a.admission_type, a.insurance,
                   a.hospital_expire_flag
            FROM admissions a
            JOIN patients p ON a.subject_id = p.subject_id
            WHERE a.dischtime IS NOT NULL
            ORDER BY a.subject_id, a.admittime
        """)
        admissions_df = pd.read_sql(query, conn)
    
    if admissions_df.empty:
        return pd.DataFrame()
    
    # Generate readmission labels
    admissions_df['admittime'] = pd.to_datetime(admissions_df['admittime'])
    admissions_df['dischtime'] = pd.to_datetime(admissions_df['dischtime'])
    
    records = []
    for _, group in admissions_df.groupby('subject_id'):
        group = group.sort_values('admittime')
        for i in range(len(group)):
            row = group.iloc[i]
            readmit_30d = 0
            if i + 1 < len(group):
                next_admit = group.iloc[i + 1]['admittime']
                days_diff = (next_admit - row['dischtime']).days
                if 0 <= days_diff <= 30:
                    readmit_30d = 1
            
            features = build_feature_vector(int(row['subject_id']), int(row['hadm_id']))
            if features:
                features['readmit_30d'] = readmit_30d
                features['hadm_id'] = int(row['hadm_id'])
                features['subject_id'] = int(row['subject_id'])
                records.append(features)
    
    return pd.DataFrame(records)
