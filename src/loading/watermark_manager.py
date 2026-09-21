from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import text
from src.config.database import get_sqlalchemy_engine
from src.utils.logger import get_logger

logger = get_logger("watermark_manager")

class WatermarkManager:
    def __init__(self):
        self.engine = get_sqlalchemy_engine()

    def get_watermark(self, table_name: str) -> Optional[datetime]:
        """Fetches the latest high watermark timestamp for a table."""
        with self.engine.connect() as conn:
            val = conn.execute(
                text("SELECT last_watermark_value FROM audit.watermarks WHERE table_name = :t"),
                {"t": table_name}
            ).scalar()
            return val

    def set_watermark(self, table_name: str, watermark_value: datetime, rows_read: int, run_id: str):
        """Updates or inserts the watermark timestamp for a table."""
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    MERGE audit.watermarks AS tgt
                    USING (SELECT :t AS table_name) AS src
                    ON tgt.table_name = src.table_name
                    WHEN MATCHED THEN
                        UPDATE SET
                            last_watermark_value = :val,
                            last_success_run_id = :run_id,
                            records_read_at_last_run = :rows,
                            updated_at = SYSUTCDATETIME()
                    WHEN NOT MATCHED THEN
                        INSERT (table_name, watermark_column, last_watermark_value, last_success_run_id, records_read_at_last_run)
                        VALUES (:t, 'order_datetime', :val, :run_id, :rows);
                """),
                {"t": table_name, "val": watermark_value, "run_id": run_id, "rows": rows_read}
            )
        logger.info(f"Watermark updated for [{table_name}]: {watermark_value}")
