"""
MIMIC-IV Demo CSV → PostgreSQL Import Script
=============================================
Reads CSV files from MIMIC-IV demo dataset and imports them into PostgreSQL.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mimic_prediction")

# MIMIC-IV Demo data directory
MIMIC_DIR = os.getenv("MIMIC_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                  "mimic-iv-clinical-database-demo-2.2"))

# Table import order (respecting foreign keys)
IMPORT_ORDER = [
    {"file": "hosp/patients.csv", "table": "patients"},
    {"file": "hosp/admissions.csv", "table": "admissions"},
    {"file": "hosp/d_labitems.csv", "table": "d_labitems"},
    {"file": "hosp/diagnoses_icd.csv", "table": "diagnoses_icd"},
    {"file": "hosp/procedures_icd.csv", "table": "procedures_icd"},
    {"file": "hosp/prescriptions.csv", "table": "prescriptions"},
    {"file": "hosp/labevents.csv", "table": "labevents"},
    {"file": "icu/icustays.csv", "table": "icustays"},
]

# Columns that need timestamp parsing
TIMESTAMP_COLS = {
    "patients": ["dod"],
    "admissions": ["admittime", "dischtime", "deathtime", "edregtime", "edouttime"],
    "prescriptions": ["starttime", "stoptime"],
    "labevents": ["charttime", "storetime"],
    "icustays": ["intime", "outtime"],
    "procedures_icd": ["chartdate"],
}

# Columns to keep for each table (matching our schema)
TABLE_COLUMNS = {
    "patients": ["subject_id", "gender", "anchor_age", "anchor_year", "anchor_year_group", "dod"],
    "admissions": ["hadm_id", "subject_id", "admittime", "dischtime", "deathtime", 
                   "admission_type", "admit_provider_id", "admission_location", "discharge_location",
                   "insurance", "language", "marital_status", "race", 
                   "edregtime", "edouttime", "hospital_expire_flag"],
    "d_labitems": ["itemid", "label", "fluid", "category"],
    "diagnoses_icd": ["subject_id", "hadm_id", "seq_num", "icd_code", "icd_version"],
    "procedures_icd": ["subject_id", "hadm_id", "seq_num", "icd_code", "icd_version", "chartdate"],
    "prescriptions": ["subject_id", "hadm_id", "pharmacy_id", "poe_id", "poe_seq",
                      "starttime", "stoptime", "drug_type", "drug", "formulary_drug_cd",
                      "gsn", "ndc", "prod_strength", "form_rx", "dose_val_rx", "dose_unit_rx",
                      "form_val_disp", "form_unit_disp", "doses_per_24_hrs", "route"],
    "labevents": ["labevent_id", "subject_id", "hadm_id", "specimen_id", "itemid",
                  "charttime", "storetime", "value", "valuenum", "valueuom",
                  "ref_range_lower", "ref_range_upper", "flag", "priority", "comments"],
    "icustays": ["stay_id", "subject_id", "hadm_id", "first_careunit", "last_careunit",
                 "intime", "outtime", "los"],
}


def import_table(engine, csv_path: str, table_name: str):
    """Import a single CSV file into PostgreSQL table."""
    if not os.path.exists(csv_path):
        logger.warning(f"File not found: {csv_path}, skipping...")
        return
    
    logger.info(f"Importing {csv_path} → {table_name}...")
    
    # Read CSV
    df = pd.read_csv(csv_path, low_memory=False)
    
    # Normalize column names to lowercase
    df.columns = df.columns.str.lower()
    
    # Filter columns to match our schema
    if table_name in TABLE_COLUMNS:
        available_cols = [c for c in TABLE_COLUMNS[table_name] if c in df.columns]
        df = df[available_cols]
    
    # Parse timestamps
    if table_name in TIMESTAMP_COLS:
        for col in TIMESTAMP_COLS[table_name]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Replace NaN with None for SQL compatibility
    df = df.where(pd.notnull(df), None)
    
    # Import using pandas to_sql with "append" mode
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False, method='multi', chunksize=500)
        logger.info(f"  ✓ Imported {len(df)} rows into {table_name}")
    except Exception as e:
        logger.error(f"  ✗ Error importing {table_name}: {e}")
        # Try row-by-row for debugging
        logger.info(f"  Retrying with individual inserts...")
        success = 0
        for idx, row in df.iterrows():
            try:
                row.to_frame().T.to_sql(table_name, engine, if_exists='append', index=False)
                success += 1
            except Exception:
                pass
        logger.info(f"  ✓ Imported {success}/{len(df)} rows into {table_name}")


def main():
    logger.info("=" * 60)
    logger.info("MIMIC-IV Demo → PostgreSQL Import")
    logger.info("=" * 60)
    logger.info(f"Database: {DATABASE_URL}")
    logger.info(f"MIMIC Dir: {MIMIC_DIR}")
    
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection successful")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return
    
    # Import tables in order
    for item in IMPORT_ORDER:
        csv_path = os.path.join(MIMIC_DIR, item["file"])
        import_table(engine, csv_path, item["table"])
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Import Summary:")
    with engine.connect() as conn:
        for item in IMPORT_ORDER:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {item['table']}"))
            count = result.scalar()
            logger.info(f"  {item['table']}: {count} rows")
    
    logger.info("=" * 60)
    logger.info("Import complete!")


if __name__ == "__main__":
    main()
