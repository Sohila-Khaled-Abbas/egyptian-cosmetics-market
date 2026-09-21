from sqlalchemy import text
from src.config.database import get_sqlalchemy_engine
from src.utils.logger import get_logger

logger = get_logger("warehouse_loader")

class WarehouseLoader:
    def __init__(self, batch_id: str = None):
        self.engine = get_sqlalchemy_engine()
        self.batch_id = batch_id or "BATCH_DEFAULT"

    def load_dimensions(self, batch_id: str = None) -> None:
        """Calls warehouse.usp_load_dimensions with SCD Type 2 logic."""
        target_batch = batch_id or self.batch_id
        logger.info(f"Triggering warehouse.usp_load_dimensions (Batch: {target_batch})...")
        
        with self.engine.begin() as conn:
            conn.execute(
                text("EXEC warehouse.usp_load_dimensions @BatchId = :batch_id"),
                {"batch_id": target_batch}
            )

        logger.info("Dimensions loaded successfully (including dim_date and SCD2 for dim_customer).")

    def load_facts(self, batch_id: str = None, is_incremental: bool = False) -> None:
        """Calls warehouse.usp_load_facts resolving surrogate keys and filtering quarantine."""
        target_batch = batch_id or self.batch_id
        logger.info(f"Triggering warehouse.usp_load_facts (Batch: {target_batch}, Incremental: {is_incremental})...")
        
        with self.engine.begin() as conn:
            conn.execute(
                text("EXEC warehouse.usp_load_facts @BatchId = :batch_id, @IsIncremental = :is_inc"),
                {"batch_id": target_batch, "is_inc": 1 if is_incremental else 0}
            )

        logger.info("Fact tables loaded successfully (fact_sales, fact_inventory, fact_store_targets).")
