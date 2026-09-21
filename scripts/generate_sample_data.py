"""
Sample Data Generator
Extracts a small, representative test sample into data/sample/ for rapid unit testing.
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "synthetic_cosmetics_data" / "raw"
SAMPLE_DIR = BASE_DIR / "data" / "sample"

def generate_samples():
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating sample data into {SAMPLE_DIR}...")

    # Customers sample (100 rows)
    df_c = pd.read_csv(RAW_DIR / "postgres_like" / "customers.csv", nrows=100)
    df_c.to_csv(SAMPLE_DIR / "sample_customers.csv", index=False)

    # Products sample (20 rows)
    df_p = pd.read_csv(RAW_DIR / "postgres_like" / "products.csv", nrows=20)
    df_p.to_csv(SAMPLE_DIR / "sample_products.csv", index=False)

    # Stores sample (35 rows)
    df_s = pd.read_csv(RAW_DIR / "postgres_like" / "stores.csv", nrows=35)
    df_s.to_csv(SAMPLE_DIR / "sample_stores.csv", index=False)

    # Orders sample (1,000 rows)
    df_o = pd.read_csv(RAW_DIR / "postgres_like" / "orders.csv", nrows=1000)
    df_o.to_csv(SAMPLE_DIR / "sample_orders.csv", index=False)

    # Inventory sample (200 rows)
    df_i = pd.read_csv(RAW_DIR / "csv" / "inventory_monthly.csv", nrows=200)
    df_i.to_csv(SAMPLE_DIR / "sample_inventory.csv", index=False)

    print("Sample datasets generated successfully!")

if __name__ == "__main__":
    generate_samples()
