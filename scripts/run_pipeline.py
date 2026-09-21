"""
Cleopatra Modern Cosmetics — Master Analytics Engineering Pipeline
Orchestrates Bronze Ingestion -> Staging Standardization -> DQ & Quarantine ->
Kimball Warehouse (SCD2 Dimensions + Facts) -> Analytics Marts -> Audit Ledger
"""
import sys
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.ingestion.bronze_loader import BronzeLoader
from src.transformation.staging_cleaner import StagingCleaner
from src.validation.dq_checker import DataQualityChecker
from src.loading.warehouse_loader import WarehouseLoader
from src.loading.marts_loader import MartsLoader
from src.loading.audit_logger import AuditLogger
from src.utils.logger import get_logger

logger = get_logger("run_pipeline")

def run_pipeline(is_incremental: bool = False):
    run_id = f"RUN_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    audit = AuditLogger(run_id=run_id, pipeline_name="Cleopatra_Full_Pipeline")
    audit.start_pipeline()
    start_total = time.time()

    print("\n" + "=" * 75)
    print(f"  STARTING CLEOPATRA COSMETICS ANALYTICS PIPELINE")
    print(f"  Run ID: {run_id} | Mode: {'Incremental' if is_incremental else 'Full Load'}")
    print("=" * 75 + "\n")

    total_read = 0
    total_rejected = 0

    try:
        # ---------------------------------------------------------------------
        # 1. BRONZE EXTRACTION & INGESTION
        # ---------------------------------------------------------------------
        step_start = datetime.now(timezone.utc)
        logger.info(">>> [STAGE 1/6] Extracting raw multi-source files into bronze layer...")
        bronze = BronzeLoader(batch_id=run_id)
        bronze_summary = bronze.load_all()
        total_read = sum(bronze_summary.values())
        audit.log_step("Bronze_Ingestion", step_start, datetime.now(timezone.utc), "SUCCESS", total_read)

        # ---------------------------------------------------------------------
        # 2. STAGING STANDARDIZATION & CLEANING
        # ---------------------------------------------------------------------
        step_start = datetime.now(timezone.utc)
        logger.info(">>> [STAGE 2/6] Standardizing and transforming raw data into staging...")
        cleaner = StagingCleaner(batch_id=run_id)
        cleaner.execute_staging_load(batch_id=run_id)
        audit.log_step("Staging_Cleanse", step_start, datetime.now(timezone.utc), "SUCCESS", total_read)

        # ---------------------------------------------------------------------
        # 3. DATA QUALITY EVALUATION & QUARANTINE ROUTING
        # ---------------------------------------------------------------------
        step_start = datetime.now(timezone.utc)
        logger.info(">>> [STAGE 3/6] Executing data quality rules and isolating anomalies into quarantine...")
        dq = DataQualityChecker(run_id=run_id)
        dq_report = dq.generate_dq_report(run_id=run_id)
        quarantine = dq.get_quarantine_metrics()
        total_rejected = sum(quarantine.values())
        audit.log_step("DataQuality_Quarantine", step_start, datetime.now(timezone.utc), "SUCCESS", total_rejected)

        # ---------------------------------------------------------------------
        # 4. WAREHOUSE DIMENSIONS & SCD TYPE 2
        # ---------------------------------------------------------------------
        step_start = datetime.now(timezone.utc)
        logger.info(">>> [STAGE 4/6] Loading Kimball star schema dimensions and processing SCD Type 2...")
        wh = WarehouseLoader(batch_id=run_id)
        wh.load_dimensions(batch_id=run_id)
        audit.log_step("Dimensions_SCD2_Load", step_start, datetime.now(timezone.utc), "SUCCESS", 0)

        # ---------------------------------------------------------------------
        # 5. WAREHOUSE FACT TABLES
        # ---------------------------------------------------------------------
        step_start = datetime.now(timezone.utc)
        logger.info(">>> [STAGE 5/6] Loading fact tables (FactSales, FactInventory, FactStoreTargets)...")
        wh.load_facts(batch_id=run_id, is_incremental=is_incremental)
        audit.log_step("Facts_Load", step_start, datetime.now(timezone.utc), "SUCCESS", total_read - total_rejected)

        # ---------------------------------------------------------------------
        # 6. ANALYTICS MARTS VALIDATION
        # ---------------------------------------------------------------------
        step_start = datetime.now(timezone.utc)
        logger.info(">>> [STAGE 6/6] Verifying curated analytics marts and executive KPIs...")
        marts = MartsLoader()
        marts_counts = marts.validate_marts()
        kpis = marts.get_executive_kpis()
        audit.log_step("Marts_Validation", step_start, datetime.now(timezone.utc), "SUCCESS", sum(marts_counts.values()))

        # ---------------------------------------------------------------------
        # FINALIZE RUN
        # ---------------------------------------------------------------------
        elapsed = time.time() - start_total
        audit.finish_pipeline(
            status="SUCCESS",
            rows_read=total_read,
            rows_inserted=total_read - total_rejected,
            rows_rejected=total_rejected
        )

        print("\n" + "=" * 75)
        print("  PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        print("=" * 75)
        print(f"  Duration:            {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
        print(f"  Total Rows Ingested: {total_read:,}")
        print(f"  Valid Rows Loaded:   {total_read - total_rejected:,}")
        print(f"  Quarantined Rows:    {total_rejected:,}")
        print(f"  Total Net Revenue:   {kpis.get('total_revenue_egp', 0):,.2f} EGP")
        print(f"  Total Orders:        {kpis.get('total_orders', 0):,}")
        print(f"  Average Margin:      {kpis.get('avg_margin_pct', 0) * 100:.2f}%")
        print("=" * 75 + "\n")

    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        audit.finish_pipeline(status="FAILED", error_message=str(e))
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
