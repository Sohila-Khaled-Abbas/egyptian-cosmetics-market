from sqlalchemy import text
from src.config.database import get_sqlalchemy_engine
from src.utils.logger import get_logger

logger = get_logger("staging_cleaner")

class StagingCleaner:
    def __init__(self, batch_id: str = None):
        self.engine = get_sqlalchemy_engine()
        self.batch_id = batch_id or "BATCH_DEFAULT"

    def execute_staging_load(self, batch_id: str = None) -> None:
        """
        Executes staging.usp_load_staging to clean and standardize bronze data:
        - Normalizes Egyptian phone numbers (+20 10... -> 010...)
        - Normalizes Governorates casing (cairo -> Cairo)
        - Normalizes Currencies (جنيه, EGP  -> EGP)
        - Normalizes Order statuses (Complete, completed -> Completed)
        - Generates order_date_key and inventory month_date_key
        """
        target_batch = batch_id or self.batch_id
        logger.info(f"Triggering staging.usp_load_staging (Batch: {target_batch})...")
        
        with self.engine.begin() as conn:
            conn.execute(
                text("EXEC staging.usp_load_staging @BatchID = :batch_id"),
                {"batch_id": target_batch}
            )

        logger.info("Staging layer transformation and standardization completed successfully.")
