import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import text
from src.config.database import get_sqlalchemy_engine
from src.utils.logger import get_logger

logger = get_logger("audit_logger")

class AuditLogger:
    def __init__(self, run_id: Optional[str] = None, pipeline_name: str = "Cleopatra_ETL_Pipeline"):
        self.engine = get_sqlalchemy_engine()
        self.run_id = run_id or f"RUN_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self.pipeline_name = pipeline_name

    def start_pipeline(self):
        """Records initial pipeline run state as RUNNING."""
        logger.info(f"Starting pipeline run: {self.run_id} ({self.pipeline_name})")
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO audit.pipeline_runs (
                        run_id, pipeline_name, start_time, status
                    )
                    VALUES (:run_id, :pipeline_name, SYSUTCDATETIME(), 'RUNNING')
                """),
                {"run_id": self.run_id, "pipeline_name": self.pipeline_name}
            )

    def log_step(
        self,
        step_name: str,
        start_time: datetime,
        end_time: datetime,
        status: str,
        rows_processed: int = 0,
        error_message: Optional[str] = None
    ):
        """Logs a completed granular step within the pipeline run."""
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Step completed: [{step_name}] in {duration:.2f}s | Rows: {rows_processed:,} | Status: {status}")

        st_naive = start_time.replace(tzinfo=None) if start_time and start_time.tzinfo else start_time
        et_naive = end_time.replace(tzinfo=None) if end_time and end_time.tzinfo else end_time

        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO audit.pipeline_steps (
                        run_id, step_name, start_time, end_time, duration_seconds,
                        status, rows_processed, error_message
                    )
                    VALUES (
                        :run_id, :step_name, :start_time, :end_time, :duration,
                        :status, :rows, :err
                    )
                """),
                {
                    "run_id": self.run_id,
                    "step_name": step_name,
                    "start_time": st_naive,
                    "end_time": et_naive,
                    "duration": duration,
                    "status": status,
                    "rows": rows_processed,
                    "err": error_message
                }
            )

    def finish_pipeline(
        self,
        status: str,
        rows_read: int = 0,
        rows_inserted: int = 0,
        rows_rejected: int = 0,
        error_message: Optional[str] = None
    ):
        """Finalizes the pipeline run with summary counts and status."""
        logger.info(f"Finishing pipeline run: {self.run_id} | Status: {status}")
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE audit.pipeline_runs
                    SET 
                        end_time = SYSUTCDATETIME(),
                        duration_seconds = DATEDIFF(SECOND, start_time, SYSUTCDATETIME()),
                        status = :status,
                        rows_read = :read,
                        rows_inserted = :inserted,
                        rows_rejected = :rejected,
                        error_message = :err
                    WHERE run_id = :run_id
                """),
                {
                    "run_id": self.run_id,
                    "status": status,
                    "read": rows_read,
                    "inserted": rows_inserted,
                    "rejected": rows_rejected,
                    "err": error_message
                }
            )
