"""
Database Setup Runner
Executes all SQL DDL and Stored Procedure scripts against SQL Server
"""
import sys
import re
from pathlib import Path
import pyodbc

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.config.database import get_connection_string

SCRIPTS = [
    ("sql/ddl/01_create_database.sql", "master"),
    ("sql/ddl/02_create_schemas.sql", "egyptian_cosmetics_dw"),
    ("sql/bronze/03_create_bronze_tables.sql", "egyptian_cosmetics_dw"),
    ("sql/staging/04_create_staging_tables.sql", "egyptian_cosmetics_dw"),
    ("sql/dq/08_create_dq_tables.sql", "egyptian_cosmetics_dw"),
    ("sql/audit/09_create_audit_tables.sql", "egyptian_cosmetics_dw"),
    ("sql/warehouse/05_create_dimensions.sql", "egyptian_cosmetics_dw"),
    ("sql/warehouse/06_create_facts.sql", "egyptian_cosmetics_dw"),
    ("sql/marts/07_create_marts.sql", "egyptian_cosmetics_dw"),
    ("sql/staging/usp_load_staging.sql", "egyptian_cosmetics_dw"),
    ("sql/dq/usp_run_dq_checks.sql", "egyptian_cosmetics_dw"),
    ("sql/warehouse/usp_load_dimensions.sql", "egyptian_cosmetics_dw"),
    ("sql/warehouse/usp_load_facts.sql", "egyptian_cosmetics_dw"),
]

def execute_sql_file(file_path: Path, target_db: str):
    conn_str = get_connection_string(target_db)
    print(f"\n[RUNNING] {file_path.name} against [{target_db}]...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by GO commands (case-insensitive, on their own line)
    batches = re.split(r"^\s*GO\s*$", content, flags=re.MULTILINE | re.IGNORECASE)
    
    with pyodbc.connect(conn_str, autocommit=True) as conn:
        with conn.cursor() as cursor:
            for i, batch in enumerate(batches, 1):
                clean_batch = batch.strip()
                if clean_batch:
                    try:
                        cursor.execute(clean_batch)
                    except Exception as e:
                        print(f"Error in batch {i} of {file_path.name}: {e}")
                        raise

    print(f"[SUCCESS] {file_path.name} executed successfully.")

def main():
    print("=" * 70)
    print("  Cleopatra Modern Cosmetics Data Warehouse Setup")
    print("=" * 70)
    
    for rel_path, db in SCRIPTS:
        full_path = BASE_DIR / rel_path
        if not full_path.exists():
            print(f"[ERROR] Script not found: {full_path}")
            sys.exit(1)
        execute_sql_file(full_path, db)

    print("\n" + "=" * 70)
    print("  ALL DATABASE OBJECTS INITIALIZED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
