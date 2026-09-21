"""
Automated Data Quality & Pipeline Reconciliation Assertion Tests
Verifies the empirical synthetic cosmetics dataset matches documented figures.
"""

import json
from pathlib import Path
import pandas as pd
import pytest

DATA_DIR = Path(__file__).parent.parent / "data"

@pytest.fixture(scope="session")
def manifest():
    manifest_path = DATA_DIR / "manifest.json"
    assert manifest_path.exists(), f"manifest.json missing at {manifest_path}"
    return json.loads(manifest_path.read_text(encoding="utf-8"))

def test_manifest_metrics(manifest):
    """Verify manifest row counts conform to project architecture."""
    assert manifest["customers_rows"] == 25200
    assert manifest["orders_rows"] == 502000
    assert manifest["products_rows"] == 20
    assert manifest["stores_rows"] == 35
    assert manifest["inventory_rows"] == 8400
    assert manifest["targets_rows"] == 417
    assert manifest["market"] == "Egypt"
    assert manifest["currency"] == "EGP"

def test_raw_files_exist():
    """Verify all 7 raw source files exist in their designated directories."""
    expected_files = [
        DATA_DIR / "raw/postgres_like/customers.csv",
        DATA_DIR / "raw/postgres_like/products.csv",
        DATA_DIR / "raw/postgres_like/stores.csv",
        DATA_DIR / "raw/postgres_like/orders.csv",
        DATA_DIR / "raw/csv/inventory_monthly.csv",
        DATA_DIR / "raw/excel/commercial_reference_data.xlsx",
        DATA_DIR / "raw/api/exchange_rates.json",
    ]
    for file_path in expected_files:
        assert file_path.exists(), f"Raw file missing: {file_path}"
        assert file_path.stat().st_size > 0, f"Raw file is empty: {file_path}"

def test_customer_deduplication_math():
    """Verify customers deduplication from 25,200 raw to 25,000 distinct."""
    customers_path = DATA_DIR / "raw/postgres_like/customers.csv"
    df = pd.read_csv(customers_path)
    assert len(df) == 25200
    distinct_ids = df["customer_id"].nunique()
    assert distinct_ids == 25000, f"Expected 25,000 distinct customers, got {distinct_ids}"
    assert len(df) - distinct_ids == 200, "Expected exactly 200 duplicate customer records"

def test_inventory_defect_counts():
    """Verify inventory raw data has 50 negative closing stocks and 50 negative damages."""
    inv_path = DATA_DIR / "raw/csv/inventory_monthly.csv"
    df = pd.read_csv(inv_path)
    assert len(df) == 8400
    negative_stock = (df["closing_stock"] < 0).sum()
    negative_damaged = (df["damaged_qty"] < 0).sum()
    assert negative_stock == 50
    assert negative_damaged == 50
    # Clean rows after quarantine
    clean_inv = len(df[(df["closing_stock"] >= 0) & (df["damaged_qty"] >= 0)])
    assert clean_inv == 8300, f"Expected 8,300 clean inventory rows, got {clean_inv}"
