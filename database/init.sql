-- ============================================
-- MIMIC-IV Clinical Prediction System
-- Database Schema Initialization
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- MIMIC-IV Core Tables
-- ============================================

CREATE TABLE IF NOT EXISTS patients (
    subject_id INTEGER PRIMARY KEY,
    gender VARCHAR(1) NOT NULL,
    anchor_age INTEGER,
    anchor_year INTEGER,
    anchor_year_group VARCHAR(20),
    dod TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS admissions (
    hadm_id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES patients(subject_id),
    admittime TIMESTAMP NOT NULL,
    dischtime TIMESTAMP,
    deathtime TIMESTAMP,
    admission_type VARCHAR(50),
    admit_provider_id VARCHAR(10),
    admission_location VARCHAR(60),
    discharge_location VARCHAR(60),
    insurance VARCHAR(255),
    language VARCHAR(10),
    marital_status VARCHAR(30),
    race VARCHAR(80),
    edregtime TIMESTAMP,
    edouttime TIMESTAMP,
    hospital_expire_flag SMALLINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS d_labitems (
    itemid INTEGER PRIMARY KEY,
    label VARCHAR(200),
    fluid VARCHAR(100),
    category VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS diagnoses_icd (
    row_id SERIAL PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES patients(subject_id),
    hadm_id INTEGER NOT NULL REFERENCES admissions(hadm_id),
    seq_num INTEGER,
    icd_code VARCHAR(10),
    icd_version INTEGER
);

CREATE TABLE IF NOT EXISTS procedures_icd (
    row_id SERIAL PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES patients(subject_id),
    hadm_id INTEGER NOT NULL REFERENCES admissions(hadm_id),
    seq_num INTEGER,
    icd_code VARCHAR(10),
    icd_version INTEGER,
    chartdate TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prescriptions (
    row_id SERIAL PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES patients(subject_id),
    hadm_id INTEGER NOT NULL REFERENCES admissions(hadm_id),
    pharmacy_id INTEGER,
    poe_id VARCHAR(25),
    poe_seq INTEGER,
    starttime TIMESTAMP,
    stoptime TIMESTAMP,
    drug_type VARCHAR(20),
    drug VARCHAR(255),
    formulary_drug_cd VARCHAR(120),
    gsn VARCHAR(200),
    ndc VARCHAR(25),
    prod_strength VARCHAR(120),
    form_rx VARCHAR(25),
    dose_val_rx VARCHAR(120),
    dose_unit_rx VARCHAR(120),
    form_val_disp VARCHAR(120),
    form_unit_disp VARCHAR(120),
    doses_per_24_hrs REAL,
    route VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS labevents (
    labevent_id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES patients(subject_id),
    hadm_id INTEGER REFERENCES admissions(hadm_id),
    specimen_id INTEGER,
    itemid INTEGER REFERENCES d_labitems(itemid),
    charttime TIMESTAMP,
    storetime TIMESTAMP,
    value VARCHAR(200),
    valuenum DOUBLE PRECISION,
    valueuom VARCHAR(20),
    ref_range_lower DOUBLE PRECISION,
    ref_range_upper DOUBLE PRECISION,
    flag VARCHAR(10),
    priority VARCHAR(10),
    comments TEXT
);

CREATE TABLE IF NOT EXISTS icustays (
    stay_id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES patients(subject_id),
    hadm_id INTEGER NOT NULL REFERENCES admissions(hadm_id),
    first_careunit VARCHAR(50),
    last_careunit VARCHAR(50),
    intime TIMESTAMP,
    outtime TIMESTAMP,
    los DOUBLE PRECISION
);

-- ============================================
-- Application Tables
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(10) NOT NULL DEFAULT 'doctor' CHECK (role IN ('admin', 'doctor')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ml_models (
    model_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20),
    algorithm VARCHAR(50),
    mlflow_run_id VARCHAR(50),
    stage VARCHAR(20) DEFAULT 'staging' CHECK (stage IN ('staging', 'production', 'archived')),
    metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions (
    prediction_id SERIAL PRIMARY KEY,
    hadm_id INTEGER REFERENCES admissions(hadm_id),
    subject_id INTEGER REFERENCES patients(subject_id),
    model_id INTEGER REFERENCES ml_models(model_id),
    probability DOUBLE PRECISION NOT NULL,
    risk_level VARCHAR(10) NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    shap_values JSONB,
    top_features JSONB,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS retraining_jobs (
    job_id SERIAL PRIMARY KEY,
    triggered_by INTEGER REFERENCES users(user_id),
    trigger_reason VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    new_model_version VARCHAR(20),
    logs TEXT
);

-- ============================================
-- Indexes for Performance
-- ============================================

CREATE INDEX IF NOT EXISTS idx_admissions_subject ON admissions(subject_id);
CREATE INDEX IF NOT EXISTS idx_diagnoses_hadm ON diagnoses_icd(hadm_id);
CREATE INDEX IF NOT EXISTS idx_diagnoses_subject ON diagnoses_icd(subject_id);
CREATE INDEX IF NOT EXISTS idx_procedures_hadm ON procedures_icd(hadm_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_hadm ON prescriptions(hadm_id);
CREATE INDEX IF NOT EXISTS idx_labevents_hadm ON labevents(hadm_id);
CREATE INDEX IF NOT EXISTS idx_labevents_subject ON labevents(subject_id);
CREATE INDEX IF NOT EXISTS idx_labevents_itemid ON labevents(itemid);
CREATE INDEX IF NOT EXISTS idx_icustays_hadm ON icustays(hadm_id);
CREATE INDEX IF NOT EXISTS idx_predictions_subject ON predictions(subject_id);
CREATE INDEX IF NOT EXISTS idx_predictions_hadm ON predictions(hadm_id);
