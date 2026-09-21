import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from sqlalchemy import text
from src.config.database import get_sqlalchemy_engine
from src.config.settings import RAW_DATA_PATH
from src.ingestion.load_csv import read_csv_in_chunks, read_csv_full
from src.ingestion.load_excel import read_excel_sheets
from src.ingestion.load_json import read_exchange_rates_json
from src.utils.hashing import compute_row_hash
from src.utils.logger import get_logger

logger = get_logger("bronze_loader")

def add_lineage_metadata(df: pd.DataFrame, source_system: str, source_file: str, batch_id: str) -> pd.DataFrame:
    """Appends audit lineage columns and computes SHA-256 row hashes."""
    df = df.copy()
    df["source_system"] = source_system
    df["source_file"] = source_file
    df["ingestion_timestamp"] = datetime.now(timezone.utc).replace(tzinfo=None)
    df["batch_id"] = batch_id
    
    # Compute row hash using non-metadata columns
    base_cols = [c for c in df.columns if c not in ("source_system", "source_file", "ingestion_timestamp", "batch_id")]
    df["row_hash"] = df[base_cols].apply(lambda row: compute_row_hash(row.values), axis=1)
    return df

class BronzeLoader:
    def __init__(self, raw_path: Path = None, batch_id: str = None):
        self.raw_path = raw_path or RAW_DATA_PATH
        self.batch_id = batch_id or str(uuid.uuid4())
        self.engine = get_sqlalchemy_engine()

    def truncate_table(self, table_name: str):
        with self.engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {table_name}"))

    def load_customers(self) -> int:
        file_path = self.raw_path / "raw" / "postgres_like" / "customers.csv"
        df = read_csv_full(file_path)
        df_lineage = add_lineage_metadata(df, "Postgres_Operational", "customers.csv", self.batch_id)
        
        self.truncate_table("bronze.raw_customers")
        df_lineage.to_sql("raw_customers", self.engine, schema="bronze", if_exists="append", index=False, chunksize=5000)
        logger.info(f"Loaded {len(df_lineage)} records into bronze.raw_customers")
        return len(df_lineage)

    def load_products(self) -> int:
        file_path = self.raw_path / "raw" / "postgres_like" / "products.csv"
        df = read_csv_full(file_path)
        df_lineage = add_lineage_metadata(df, "Postgres_Operational", "products.csv", self.batch_id)
        
        self.truncate_table("bronze.raw_products")
        df_lineage.to_sql("raw_products", self.engine, schema="bronze", if_exists="append", index=False)
        logger.info(f"Loaded {len(df_lineage)} records into bronze.raw_products")
        return len(df_lineage)

    def load_stores(self) -> int:
        file_path = self.raw_path / "raw" / "postgres_like" / "stores.csv"
        df = read_csv_full(file_path)
        df_lineage = add_lineage_metadata(df, "Postgres_Operational", "stores.csv", self.batch_id)
        
        self.truncate_table("bronze.raw_stores")
        df_lineage.to_sql("raw_stores", self.engine, schema="bronze", if_exists="append", index=False)
        logger.info(f"Loaded {len(df_lineage)} records into bronze.raw_stores")
        return len(df_lineage)

    def load_inventory(self) -> int:
        file_path = self.raw_path / "raw" / "csv" / "inventory_monthly.csv"
        df = read_csv_full(file_path)
        df_lineage = add_lineage_metadata(df, "ERP_Inventory_Export", "inventory_monthly.csv", self.batch_id)
        
        self.truncate_table("bronze.raw_inventory")
        df_lineage.to_sql("raw_inventory", self.engine, schema="bronze", if_exists="append", index=False, chunksize=5000)
        logger.info(f"Loaded {len(df_lineage)} records into bronze.raw_inventory")
        return len(df_lineage)

    def load_excel_reference_data(self) -> Dict[str, int]:
        file_path = self.raw_path / "raw" / "excel" / "commercial_reference_data.xlsx"
        sheets = read_excel_sheets(file_path)
        counts = {}

        if "Targets" in sheets:
            df_tgt = add_lineage_metadata(sheets["Targets"], "Commercial_Planning", "commercial_reference_data.xlsx::Targets", self.batch_id)
            self.truncate_table("bronze.raw_targets")
            df_tgt.to_sql("raw_targets", self.engine, schema="bronze", if_exists="append", index=False)
            counts["targets"] = len(df_tgt)
            logger.info(f"Loaded {len(df_tgt)} records into bronze.raw_targets")

        if "Campaigns" in sheets:
            df_cmp = add_lineage_metadata(sheets["Campaigns"], "Marketing_Agency_Export", "commercial_reference_data.xlsx::Campaigns", self.batch_id)
            self.truncate_table("bronze.raw_campaigns")
            df_cmp.to_sql("raw_campaigns", self.engine, schema="bronze", if_exists="append", index=False)
            counts["campaigns"] = len(df_cmp)
            logger.info(f"Loaded {len(df_cmp)} records into bronze.raw_campaigns")

        return counts

    def load_exchange_rates(self) -> int:
        file_path = self.raw_path / "raw" / "api" / "exchange_rates.json"
        df = read_exchange_rates_json(file_path)
        df_lineage = add_lineage_metadata(df, "Forex_Central_Bank_API", "exchange_rates.json", self.batch_id)
        
        self.truncate_table("bronze.raw_exchange_rates")
        df_lineage.to_sql("raw_exchange_rates", self.engine, schema="bronze", if_exists="append", index=False)
        logger.info(f"Loaded {len(df_lineage)} records into bronze.raw_exchange_rates")
        return len(df_lineage)

    def load_orders(self, chunk_size: int = 50000) -> int:
        file_path = self.raw_path / "raw" / "postgres_like" / "orders.csv"
        self.truncate_table("bronze.raw_orders")
        total_rows = 0

        logger.info(f"Beginning chunked ingestion of orders.csv (chunks of {chunk_size})...")
        for chunk in read_csv_in_chunks(file_path, chunk_size=chunk_size):
            chunk_lineage = add_lineage_metadata(chunk, "Postgres_Operational", "orders.csv", self.batch_id)
            chunk_lineage.to_sql("raw_orders", self.engine, schema="bronze", if_exists="append", index=False, chunksize=10000)
            total_rows += len(chunk_lineage)
            logger.info(f"Ingested {total_rows:,} orders into bronze.raw_orders...")

        logger.info(f"Completed ingestion of {total_rows:,} total orders into bronze.raw_orders")
        return total_rows

    def load_all(self) -> Dict[str, Any]:
        """Loads all raw datasets into bronze layer."""
        logger.info(f"Starting Bronze Ingestion (Batch: {self.batch_id})")
        summary = {
            "customers": self.load_customers(),
            "products": self.load_products(),
            "stores": self.load_stores(),
            "inventory": self.load_inventory(),
            "exchange_rates": self.load_exchange_rates(),
            **self.load_excel_reference_data(),
            "orders": self.load_orders()
        }
        logger.info(f"Bronze Ingestion Summary: {summary}")
        return summary
