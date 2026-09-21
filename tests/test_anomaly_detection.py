import pytest
import pandas as pd
from pathlib import Path
from src.validation.rules_engine import RulesEngine

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

def test_detect_orders_anomalies():
    orders_csv = RAW_DIR / "postgres_like" / "orders.csv"
    assert orders_csv.exists()

    # Scan orders in chunks to detect intentional anomalies
    qty_anomaly_found = False
    date_anomaly_found = False

    for chunk in pd.read_csv(orders_csv, chunksize=100000, dtype=str):
        if RulesEngine.check_positive_numeric(chunk, "quantity").sum() > 0:
            qty_anomaly_found = True
        if RulesEngine.check_date_range(chunk, "order_datetime", min_date="2020-01-01", max_date="2025-12-31").sum() > 0:
            date_anomaly_found = True
        if qty_anomaly_found and date_anomaly_found:
            break

    assert qty_anomaly_found, "Expected intentional non-positive quantity anomalies in orders.csv"
    assert date_anomaly_found, "Expected intentional legacy/future date anomalies in orders.csv"

def test_detect_inventory_negative_stock():
    inv_csv = RAW_DIR / "csv" / "inventory_monthly.csv"
    assert inv_csv.exists()

    df_inv = pd.read_csv(inv_csv, dtype=str)
    closing_anomalies = RulesEngine.check_non_negative(df_inv, "closing_stock")
    damaged_anomalies = RulesEngine.check_non_negative(df_inv, "damaged_qty")

    assert closing_anomalies.sum() > 0, "Expected intentional negative closing stock anomalies"
    assert damaged_anomalies.sum() > 0, "Expected intentional negative damaged quantity anomalies"
