from typing import Dict, Any, List
import pandas as pd
from sqlalchemy import text
from src.config.database import get_sqlalchemy_engine
from src.utils.logger import get_logger

logger = get_logger("dq_checker")

class DataQualityChecker:
    def __init__(self, run_id: str = None):
        self.engine = get_sqlalchemy_engine()
        self.run_id = run_id

    def execute_sql_dq_checks(self, run_id: str = None) -> pd.DataFrame:
        """Executes dq.usp_run_dq_checks stored procedure and fetches summary ledger."""
        target_run_id = run_id or self.run_id or "RUN_DEFAULT"
        logger.info(f"Triggering SQL Server Data Quality validations (Run ID: {target_run_id})...")

        with self.engine.begin() as conn:
            conn.execute(
                text("EXEC dq.usp_run_dq_checks @RunId = :run_id, @BatchId = :batch_id"),
                {"run_id": target_run_id, "batch_id": target_run_id}
            )

        # Retrieve DQ results
        query = text("""
            SELECT rule_id, total_rows, failed_rows, failure_rate, status, error_sample_reference
            FROM dq.data_quality_results
            WHERE run_id = :run_id
        """)
        with self.engine.connect() as conn:
            results_df = pd.read_sql(query, conn, params={"run_id": target_run_id})

        logger.info(f"DQ checks completed across {len(results_df)} rule sets")
        return results_df

    def get_quarantine_metrics(self) -> Dict[str, int]:
        """Returns row counts from all 4 quarantine tables."""
        counts = {}
        tables = [
            ("orders", "dq.rejected_orders"),
            ("customers", "dq.rejected_customers"),
            ("inventory", "dq.rejected_inventory"),
            ("targets", "dq.rejected_targets")
        ]
        with self.engine.connect() as conn:
            for key, tbl in tables:
                cnt = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
                counts[key] = cnt
        return counts

    def generate_dq_report(self, run_id: str = None) -> str:
        """Generates a formatted ASCII / Markdown summary report of DQ results."""
        results_df = self.execute_sql_dq_checks(run_id)
        quarantine = self.get_quarantine_metrics()

        lines = [
            "=" * 70,
            "  CLEOPATRA MODERN COSMETICS — DATA QUALITY & OBSERVABILITY AUDIT",
            "=" * 70,
            f"Run ID: {run_id or self.run_id}",
            "-" * 70,
            f"{'Rule ID':<15} {'Total Rows':<12} {'Failed':<10} {'Fail Rate %':<12} {'Status':<10}",
            "-" * 70,
        ]

        for _, row in results_df.iterrows():
            fail_pct = f"{row['failure_rate'] * 100:.2f}%"
            lines.append(f"{row['rule_id']:<15} {row['total_rows']:<12,d} {row['failed_rows']:<10,d} {fail_pct:<12} {row['status']:<10}")

        lines.extend([
            "-" * 70,
            "QUARANTINE SUMMARY (REJECTED RECORDS ISOLATED):",
            f"  - Defective Orders Quarantined:    {quarantine.get('orders', 0):,}",
            f"  - Defective Customers Quarantined: {quarantine.get('customers', 0):,}",
            f"  - Defective Inventory Quarantined: {quarantine.get('inventory', 0):,}",
            f"  - Defective Targets Quarantined:   {quarantine.get('targets', 0):,}",
            "=" * 70
        ])

        report_text = "\n".join(lines)
        logger.info("\n" + report_text)
        return report_text
