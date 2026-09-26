"""
Historical Orders Data Generator (Egyptian Cosmetics Market)
===========================================================

Generates realistic 2024 historical transaction data (`orders_historical.csv`)
to demonstrate Power Query Append Queries as New (`Table.Combine`).

Features realistic Egyptian cosmetics retail domain anomalies:
- Currency variations: EGP, EGP , جنيه, جنيه مصري, LE, null
- Status casing and bilingual drift: Completed, completed, Complete, Cancelled, ملغي, Returned, مرتجع, Pending
- Egyptian payment methods: Cash on Delivery, Fawry, InstaPay, Vodafone Cash, Credit Card
- Channels: In-Store, Website, Mobile App, WhatsApp Order
- Data quality issues:
  * Zero and negative quantities (unlinked returns)
  * Negative unit prices (manual credit overrides)
  * 1900-01-01 legacy date anomaly & future-dated transactions
  * Duplicate order IDs
  * Orphaned foreign keys (closed pop-up store S999, guest customer C9999999, discontinued product P999)
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


def generate_historical_orders(
    n_orders: int = 50000,
    output_path: str = "data/raw/postgres_like/orders_historical.csv",
    seed: int = 2024
):
    random.seed(seed)
    np.random.seed(seed)

    base_dir = Path(".")
    raw_dir = base_dir / "data" / "raw" / "postgres_like"

    # 1. Load actual reference master data
    customers_df = pd.read_csv(raw_dir / "customers.csv", usecols=["customer_id"])
    products_df = pd.read_csv(raw_dir / "products.csv")
    stores_df = pd.read_csv(raw_dir / "stores.csv", usecols=["store_id"])

    customer_ids = customers_df["customer_id"].dropna().to_numpy()
    store_ids = stores_df["store_id"].dropna().to_numpy()
    product_map = products_df.set_index("product_id").to_dict("index")
    product_ids = list(product_map.keys())

    # 2. Egyptian retail channels & payment methods (2024 context)
    channels = [
        ("In-Store", "متجر"),
        ("Website", "الموقع الإلكتروني"),
        ("Mobile App", "تطبيق الهاتف"),
        ("WhatsApp Order", "طلبات واتساب"),
    ]
    channel_weights = [0.45, 0.25, 0.20, 0.10]

    payments = [
        ("Cash on Delivery", "الدفع عند الاستلام"),
        ("Fawry", "فوري"),
        ("InstaPay", "انستاباي"),
        ("Vodafone Cash", "فودافون كاش"),
        ("Credit Card", "بطاقة ائتمان"),
    ]
    payment_weights = [0.50, 0.18, 0.14, 0.12, 0.06]

    # Campaigns active during 2024 (e.g., Mother's Day, Ramadan, White Friday)
    campaign_pool = ["CAMP01", "CAMP02", "CAMP03", "CAMP04", "CAMP05", "CAMP06", "CAMP07", None]
    campaign_weights = [0.15, 0.18, 0.12, 0.10, 0.15, 0.10, 0.05, 0.15]

    # Date range: Full year 2024
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    end_date = datetime(2024, 12, 31, 23, 59, 59)
    total_seconds = int((end_date - start_date).total_seconds())

    rows = []
    print(f"Generating {n_orders:,} historical order transactions for 2024...")

    for i in range(1, n_orders + 1):
        order_id = f"ORD2024{i:09d}"
        order_dt = start_date + timedelta(seconds=random.randint(0, total_seconds))

        pid = random.choice(product_ids)
        p = product_map[pid]

        qty = random.choices([1, 2, 3, 4, 5, 6], weights=[45, 27, 14, 8, 4, 2])[0]
        unit_price = float(p["list_price_egp"])
        discount_pct = random.choice([0.0, 0.0, 0.0, 0.05, 0.10, 0.15, 0.20, 0.25])

        gross = round(qty * unit_price, 2)
        discount_amt = round(gross * discount_pct, 2)
        net = round(gross - discount_amt, 2)
        cost = round(qty * float(p["standard_cost_egp"]), 2)

        ch = random.choices(channels, weights=channel_weights)[0]
        pay = random.choices(payments, weights=payment_weights)[0]
        camp = random.choices(campaign_pool, weights=campaign_weights)[0]
        cust = random.choice(customer_ids)
        store = random.choice(store_ids)

        status = random.choices(
            ["Completed", "Cancelled", "Returned", "Pending"],
            weights=[86, 5, 6, 3]
        )[0]

        currency = "EGP"

        rows.append([
            order_id,
            order_dt.strftime("%Y-%m-%d %H:%M:%S"),
            cust,
            pid,
            store,
            camp if camp else "",
            ch[0],
            ch[1],
            pay[0],
            pay[1],
            qty,
            unit_price,
            discount_pct,
            gross,
            discount_amt,
            net,
            cost,
            status,
            currency
        ])

    columns = [
        "order_id", "order_datetime", "customer_id", "product_id",
        "store_id", "campaign_id", "sales_channel_en", "sales_channel_ar",
        "payment_method_en", "payment_method_ar", "quantity",
        "unit_price_egp", "discount_pct", "gross_sales_egp",
        "discount_egp", "net_sales_egp", "cost_egp", "order_status",
        "currency"
    ]

    df = pd.DataFrame(rows, columns=columns)

    # 3. Inject realistic Egyptian retail data issues matching README_DATA_ISSUES.md
    print("Injecting intentional business domain data quality issues...")

    # Issue A: Status casing and bilingual drift
    status_sample = df.sample(frac=0.035, random_state=101).index
    s_half = len(status_sample) // 3
    df.loc[status_sample[:s_half], "order_status"] = "completed"
    df.loc[status_sample[s_half:2*s_half], "order_status"] = "Complete"
    df.loc[status_sample[2*s_half:], "order_status"] = "ملغي"

    # Issue B: Currency inconsistencies
    curr_egp_space = df.sample(frac=0.025, random_state=102).index
    df.loc[curr_egp_space, "currency"] = "EGP "
    curr_ar = df.sample(frac=0.015, random_state=103).index
    df.loc[curr_ar, "currency"] = "جنيه مصري"
    curr_le = df.sample(frac=0.010, random_state=104).index
    df.loc[curr_le, "currency"] = "LE"

    # Issue C: Negative / Zero quantities (unlinked returns and cart tests)
    bad_qty_idx = df.sample(n=60, random_state=105).index
    df.loc[bad_qty_idx[:35], "quantity"] = 0
    df.loc[bad_qty_idx[35:], "quantity"] = -1

    # Issue D: Negative unit prices (manual manager price overrides)
    bad_price_idx = df.sample(n=15, random_state=106).index
    df.loc[bad_price_idx, "unit_price_egp"] = -50.0

    # Issue E: Date anomalies (legacy 1900-01-01 and future-dated records)
    date_anomaly_idx = df.sample(n=25, random_state=107).index
    df.loc[date_anomaly_idx[:15], "order_datetime"] = "1900-01-01 00:00:00"
    df.loc[date_anomaly_idx[15:], "order_datetime"] = "2026-11-20 14:15:00"

    # Issue F: Broken foreign keys
    # - S999: Closed Heliopolis pop-up kiosk in early 2024
    # - C9999999: Guest walk-ins without loyalty profile
    # - P999: Discontinued imported line
    fk_sample = df.sample(n=45, random_state=108).index
    df.loc[fk_sample[:15], "store_id"] = "S999"
    df.loc[fk_sample[15:30], "customer_id"] = "C9999999"
    df.loc[fk_sample[30:], "product_id"] = "P999"

    # Issue G: Duplicate order transactions (~200 exact and modified duplicates)
    dup_sample = df.sample(n=200, random_state=109).copy()
    # slightly modify timestamp or net to simulate retry payments
    dup_sample.loc[dup_sample.index[:100], "net_sales_egp"] = dup_sample.loc[dup_sample.index[:100], "net_sales_egp"] * 1.02
    df = pd.concat([df, dup_sample], ignore_index=True)

    # 4. Save output
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False, encoding="utf-8-sig")

    print(f"Successfully generated {len(df):,} records saved to '{out_file}'.")
    print(f"Date span: {df['order_datetime'].min()} to {df['order_datetime'].max()}")
    print(f"File size: {out_file.stat().st_size / (1024*1024):.2f} MB")
    return df


if __name__ == "__main__":
    generate_historical_orders(n_orders=50000)
