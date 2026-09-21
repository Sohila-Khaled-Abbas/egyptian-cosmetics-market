"""
Synthetic Egyptian Cosmetics Data Generator
===========================================

Creates a realistic multi-source cosmetics dataset with intentionally messy
data problems for an end-to-end Data Analytics Engineering portfolio project.

Outputs:
    synthetic_cosmetics_data/
        raw/
            postgres_like/
            excel/
            csv/
            api/
        README_DATA_ISSUES.md
        data_dictionary.csv

Designed for:
    - Python / Pandas
    - SQL / PostgreSQL
    - ETL / ELT
    - Data Quality
    - Dimensional Modeling
    - Power BI
    - Incremental loading
    - Egyptian market / Arabic-English bilingual data

No real customer PII is used. Customer names, phone numbers and emails are
synthetic placeholders.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import string
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


ARABIC_FIRST = [
    "محمد", "أحمد", "محمود", "عمر", "يوسف", "مصطفى", "كريم", "عبدالله",
    "سارة", "سلمى", "نور", "مريم", "آية", "ملك", "منة", "ريم", "جنى",
    "دينا", "ياسمين", "بسنت", "مي", "هدى"
]

ARABIC_LAST = [
    "حسن", "علي", "محمود", "إبراهيم", "عبدالرحمن", "سعيد", "حمدي",
    "فؤاد", "مصطفى", "كمال", "منصور", "السيد", "حسين", "عبدالعزيز"
]

EN_FIRST = [
    "Mohamed", "Ahmed", "Mahmoud", "Omar", "Youssef", "Mostafa", "Karim",
    "Sara", "Salma", "Nour", "Mariam", "Aya", "Malak", "Mena", "Reem",
    "Jana", "Dina", "Yasmine", "Basent", "Mai", "Hoda"
]

EG_GOVERNORATES = {
    "Cairo": ["Nasr City", "Heliopolis", "Maadi", "New Cairo", "Shorouk", "Downtown"],
    "Giza": ["Dokki", "Mohandessin", "Haram", "6th of October", "Sheikh Zayed"],
    "Alexandria": ["Smouha", "Sidi Gaber", "Miami", "Stanley", "Montaza"],
    "Dakahlia": ["Mansoura", "Talkha", "Mit Ghamr"],
    "Gharbia": ["Tanta", "Mahalla", "Kafr El Zayat"],
    "Sharqia": ["Zagazig", "10th of Ramadan", "Belbeis"],
    "Qalyubia": ["Banha", "Shubra El Kheima", "Obour"],
    "Damietta": ["Damietta", "New Damietta", "Ras El Bar"],
    "Beheira": ["Damanhur", "Kafr El Dawwar"],
    "Ismailia": ["Ismailia", "Fayed"],
    "Suez": ["Suez", "Ain Sokhna"],
    "Port Said": ["Port Said"],
    "Fayoum": ["Fayoum"],
    "Minya": ["Minya"],
    "Assiut": ["Assiut"],
    "Sohag": ["Sohag"],
    "Qena": ["Qena"],
    "Luxor": ["Luxor"],
    "Aswan": ["Aswan"],
    "Red Sea": ["Hurghada", "El Gouna"],
    "North Sinai": ["Arish"],
    "South Sinai": ["Sharm El Sheikh", "Dahab"],
}

PRODUCTS = [
    ("P001", "Glow Up Vitamin C Serum", "سيروم جلو أب فيتامين C", "Skincare", "Serum", 249, 150),
    ("P002", "Hydra Balance Moisturizer", "مرطب هيدرا بالانس", "Skincare", "Moisturizer", 189, 105),
    ("P003", "Pure Clean Face Wash", "غسول بيور كلين للوجه", "Skincare", "Cleanser", 145, 82),
    ("P004", "Aloe Calm Gel", "جل ألو كالم بالألوفيرا", "Skincare", "Gel", 129, 70),
    ("P005", "Daily Shield SPF 50", "واقي شمس ديلي شيلد SPF 50", "Skincare", "Sunscreen", 299, 175),
    ("P006", "Velvet Matte Foundation", "فاونديشن فيلفت مات", "Makeup", "Foundation", 325, 190),
    ("P007", "Stay Fresh Concealer", "كونسيلر ستاي فريش", "Makeup", "Concealer", 215, 120),
    ("P008", "Rose Glow Blush", "بلاشر روز جلو", "Makeup", "Blush", 179, 98),
    ("P009", "Long Wear Lip Tint", "ليب تنت لونج وير", "Makeup", "Lip", 165, 92),
    ("P010", "Soft Touch Mascara", "ماسكارا سوفت تاتش", "Makeup", "Mascara", 195, 108),
    ("P011", "Keratin Repair Shampoo", "شامبو كيراتين ريبير", "Haircare", "Shampoo", 219, 126),
    ("P012", "Argan Nourish Hair Mask", "ماسك شعر أرجان نورش", "Haircare", "Hair Mask", 239, 138),
    ("P013", "Silky Leave-In Cream", "كريم شعر سيليكي ليف إن", "Haircare", "Hair Cream", 199, 112),
    ("P014", "Fresh Bloom Body Mist", "بودي ميست فريش بلوم", "Fragrance", "Body Mist", 229, 125),
    ("P015", "Midnight Oud Eau de Parfum", "عطر ميدنايت عود", "Fragrance", "Perfume", 549, 305),
    ("P016", "Citrus Musk Eau de Parfum", "عطر سيتروس مسك", "Fragrance", "Perfume", 479, 265),
    ("P017", "Baby Soft Body Lotion", "لوشن بيبي سوفت للجسم", "Body Care", "Body Lotion", 159, 88),
    ("P018", "Coffee Scrub", "سكراب القهوة", "Body Care", "Scrub", 149, 80),
    ("P019", "Gentle Hand Cream", "كريم يدين جنتل", "Body Care", "Hand Cream", 99, 52),
    ("P020", "Beauty Essentials Gift Box", "بوكس بيوتي إسينشالز", "Gift Sets", "Gift Set", 699, 395),
]

BRANDS = {
    "Glow Up": "جلو أب",
    "Pure": "بيور",
    "Velvet": "فيلفت",
    "Silky": "سيليكي",
    "Fresh Bloom": "فريش بلوم",
    "Beauty Essentials": "بيوتي إسينشالز",
}

CHANNELS = [
    ("Website", "الموقع الإلكتروني"),
    ("Instagram", "إنستجرام"),
    ("Facebook", "فيسبوك"),
    ("TikTok", "تيك توك"),
    ("Jumia", "جوميا"),
    ("Amazon Egypt", "أمازون مصر"),
    ("Noon", "نون"),
    ("Retail Store", "فرع"),
    ("Pharmacy", "صيدلية"),
    ("Marketplace", "ماركت بليس"),
]

PAYMENTS = [
    ("Cash on Delivery", "الدفع عند الاستلام"),
    ("Vodafone Cash", "فودافون كاش"),
    ("InstaPay", "إنستاباي"),
    ("Credit Card", "بطاقة ائتمان"),
    ("Debit Card", "بطاقة خصم"),
    ("Meeza", "ميزة"),
]

CAMPAIGNS = [
    ("CMP001", "Ramadan Glow", "رمضان جلو"),
    ("CMP002", "Summer Skin", "بشرة الصيف"),
    ("CMP003", "Back to Routine", "العودة للروتين"),
    ("CMP004", "White Friday Egypt", "وايت فرايداي مصر"),
    ("CMP005", "Mother's Day", "عيد الأم"),
    ("CMP006", "No Campaign", "بدون حملة"),
    ("CMP007", "Payday Beauty", "بيوتي يوم القبض"),
]

SUPPLIERS = [
    ("SUP001", "Nile Beauty Manufacturing", "مصنع نايل بيوتي"),
    ("SUP002", "Cairo Cosmetics Industries", "مصانع كايرو كوزماتكس"),
    ("SUP003", "Delta Personal Care", "دلتا للعناية الشخصية"),
    ("SUP004", "Oriental Fragrance Labs", "معامل أورينتال للعطور"),
    ("SUP005", "Egypt Beauty Imports", "إيجيبت بيوتي للاستيراد"),
]

def rng_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)

def clean_phone(n: int) -> str:
    return "010" + "".join(random.choice(string.digits) for _ in range(8))

def fake_email(first: str, customer_id: str) -> str:
    base = re.sub(r"[^a-z0-9]", "", first.lower())
    return f"{base}.{customer_id.lower()}@example.com"

def bilingual_customer_name(i: int):
    if random.random() < 0.52:
        ar = f"{random.choice(ARABIC_FIRST)} {random.choice(ARABIC_LAST)}"
        en = f"{random.choice(EN_FIRST)} {random.choice(EN_FIRST)}"
    else:
        en = f"{random.choice(EN_FIRST)} {random.choice(EN_FIRST)}"
        ar = f"{random.choice(ARABIC_FIRST)} {random.choice(ARABIC_LAST)}"
    return ar, en

def make_customers(n: int):
    rows = []
    start = datetime(2023, 1, 1)
    for i in range(1, n + 1):
        cid = f"C{i:07d}"
        ar, en = bilingual_customer_name(i)
        gov = random.choice(list(EG_GOVERNORATES))
        area = random.choice(EG_GOVERNORATES[gov])
        gender = random.choices(["Female", "Male"], weights=[0.78, 0.22])[0]
        birth_year = random.randint(1970, 2003)
        signup = start + timedelta(days=random.randint(0, 1100))
        phone = clean_phone(i)
        email = fake_email(en.split()[0], cid)
        rows.append([
            cid, ar, en, gender, birth_year, gov, area, phone, email,
            signup.date(), random.choice(["Retail", "Premium", "Student", "Professional"])
        ])
    return pd.DataFrame(rows, columns=[
        "customer_id", "customer_name_ar", "customer_name_en", "gender",
        "birth_year", "governorate", "area", "phone", "email",
        "signup_date", "customer_segment"
    ])

def make_products():
    rows = []
    for pid, en, ar, cat, subcat, price, cost in PRODUCTS:
        brand_en = random.choice(list(BRANDS))
        brand_ar = BRANDS[brand_en]
        rows.append([
            pid, en, ar, brand_en, brand_ar, cat, subcat, price, cost,
            random.choice(["EGP", "EGP ", "جنيه", "EGP"]),
            random.choice(["Local", "Imported", "Local", "Local"])
        ])
    return pd.DataFrame(rows, columns=[
        "product_id", "product_name_en", "product_name_ar",
        "brand_en", "brand_ar", "category", "subcategory",
        "list_price_egp", "standard_cost_egp", "currency", "origin"
    ])

def make_stores():
    stores = []
    store_id = 1
    for gov, areas in EG_GOVERNORATES.items():
        for area in areas[:2]:
            stores.append([
                f"S{store_id:03d}",
                f"{area} Beauty Store",
                f"فرع {area}",
                gov,
                area,
                random.choice(["Mall", "Street", "Pharmacy", "Kiosk"]),
                random.choice(["Cairo Hub", "Delta Hub", "Upper Egypt Hub", "Canal Hub"])
            ])
            store_id += 1
    return pd.DataFrame(stores, columns=[
        "store_id", "store_name_en", "store_name_ar",
        "governorate", "area", "store_type", "distribution_region"
    ])

def make_targets(stores, products, start, end):
    months = pd.date_range(start=start, end=end, freq="MS")
    rows = []
    for month in months:
        for store in stores.itertuples():
            rows.append([
                month.date(), store.store_id,
                round(random.uniform(120_000, 450_000), 2),
                random.randint(900, 3200)
            ])
    return pd.DataFrame(rows, columns=[
        "target_month", "store_id", "sales_target_egp", "order_target"
    ])

def make_campaigns():
    rows = []
    for cid, en, ar in CAMPAIGNS:
        rows.append([
            cid, en, ar,
            random.choice(["Meta Ads", "TikTok Ads", "Google Ads", "Influencer", "Organic"]),
            random.randint(5000, 120000),
            round(random.uniform(0.04, 0.18), 4)
        ])
    return pd.DataFrame(rows, columns=[
        "campaign_id", "campaign_name_en", "campaign_name_ar",
        "platform", "budget_egp", "expected_conversion_rate"
    ])

def make_orders(n_orders, customers, products, stores, campaigns, start, end):
    customer_ids = customers.customer_id.to_numpy()
    product_ids = products.product_id.to_numpy()
    store_ids = stores.store_id.to_numpy()
    campaign_ids = campaigns.campaign_id.to_numpy()

    channel_en = [x[0] for x in CHANNELS]
    channel_ar = [x[1] for x in CHANNELS]
    payment_en = [x[0] for x in PAYMENTS]
    payment_ar = [x[1] for x in PAYMENTS]

    prod_map = products.set_index("product_id").to_dict("index")
    rows = []
    for i in range(1, n_orders + 1):
        order_id = f"ORD{start.year}{i:09d}"
        dt = start + timedelta(
            seconds=random.randint(0, int((end - start).total_seconds()))
        )
        pid = random.choice(product_ids)
        p = prod_map[pid]
        qty = random.choices([1, 2, 3, 4, 5, 6], weights=[42, 28, 15, 8, 5, 2])[0]
        unit = float(p["list_price_egp"])
        discount_pct = random.choice([0, 0, 0.05, 0.10, 0.15, 0.20])
        gross = round(qty * unit, 2)
        discount = round(gross * discount_pct, 2)
        net = round(gross - discount, 2)
        cost = round(qty * float(p["standard_cost_egp"]), 2)
        ch_idx = random.randrange(len(CHANNELS))
        pay_idx = random.randrange(len(PAYMENTS))
        status = random.choices(
            ["Completed", "Cancelled", "Returned", "Pending"],
            weights=[88, 4, 5, 3]
        )[0]
        rows.append([
            order_id, dt, random.choice(customer_ids), pid,
            random.choice(store_ids), random.choice(campaign_ids),
            channel_en[ch_idx], channel_ar[ch_idx],
            payment_en[pay_idx], payment_ar[pay_idx],
            qty, unit, discount_pct, gross, discount, net, cost,
            status, random.choice(["EGP", "EGP", "جنيه"])
        ])

    return pd.DataFrame(rows, columns=[
        "order_id", "order_datetime", "customer_id", "product_id",
        "store_id", "campaign_id", "sales_channel_en", "sales_channel_ar",
        "payment_method_en", "payment_method_ar", "quantity",
        "unit_price_egp", "discount_pct", "gross_sales_egp",
        "discount_egp", "net_sales_egp", "cost_egp", "order_status",
        "currency"
    ])

def make_inventory(products, stores, start, months=12):
    rows = []
    for month in pd.date_range(start=start, periods=months, freq="MS"):
        for store in stores.itertuples():
            for product in products.itertuples():
                opening = random.randint(20, 250)
                received = random.randint(0, 180)
                sold = random.randint(0, max(1, opening + received))
                damaged = random.choice([0, 0, 0, 1, 2, 3])
                closing = opening + received - sold - damaged
                rows.append([
                    month.date(), store.store_id, product.product_id,
                    opening, received, sold, damaged, max(closing, 0)
                ])
    return pd.DataFrame(rows, columns=[
        "month", "store_id", "product_id", "opening_stock",
        "received_qty", "sold_qty", "damaged_qty", "closing_stock"
    ])

def make_exchange_rates(start, end):
    dates = pd.date_range(start, end, freq="D")
    usd = 30.85
    eur = 33.40
    rows = []
    for d in dates:
        usd += random.uniform(-0.18, 0.22)
        eur += random.uniform(-0.20, 0.25)
        rows.append([
            d.date(), "USD", round(usd, 4), "EGP",
            d.strftime("%Y-%m-%d") + "T09:00:00Z"
        ])
        rows.append([
            d.date(), "EUR", round(eur, 4), "EGP",
            d.strftime("%Y-%m-%d") + "T09:00:00Z"
        ])
    return pd.DataFrame(rows, columns=[
        "rate_date", "base_currency", "rate", "quote_currency", "api_timestamp"
    ])

def inject_realistic_issues(customers, products, stores, orders, inventory, targets, rng):
    """Inject intentional issues that an ETL/data-quality project should detect."""

    # 1. Duplicate customers: exact and near-duplicate.
    dup_exact = customers.sample(frac=0.008, random_state=11)
    customers = pd.concat([customers, dup_exact], ignore_index=True)

    near_idx = customers.sample(120, random_state=12).index
    customers.loc[near_idx[:40], "phone"] = customers.loc[near_idx[:40], "phone"].str.replace(
        "010", "+20 10", regex=False
    )
    customers.loc[near_idx[40:80], "email"] = customers.loc[near_idx[40:80], "email"].str.upper()
    customers.loc[near_idx[80:], "governorate"] = customers.loc[near_idx[80:], "governorate"].str.lower()

    # 2. Missing customer contact fields.
    for col, frac in [("phone", 0.012), ("email", 0.009), ("area", 0.006)]:
        idx = customers.sample(frac=frac, random_state=20 + len(col)).index
        customers.loc[idx, col] = None

    # 3. Product naming inconsistency.
    product_aliases = {
        "P001": ["Glow Up Vitamin C Serum", "GlowUp Vitamin C Serum", "سيروم جلو اب فيتامين C"],
        "P005": ["Daily Shield SPF50", "Daily Shield SPF 50", "ديلي شيلد SPF 50"],
        "P015": ["Midnight Oud EDP", "Midnight Oud Eau De Parfum", "ميدنايت عود"],
    }
    for pid, aliases in product_aliases.items():
        idx = orders[orders.product_id == pid].sample(
            frac=min(0.18, 1), random_state=int(pid[-1]) + 30
        ).index
        if len(idx):
            orders.loc[idx, "product_id"] = pid  # keep key valid; name inconsistency lives in source product file

    # 4. Invalid / impossible quantities.
    bad_idx = orders.sample(75, random_state=44).index
    orders.loc[bad_idx[:20], "quantity"] = 0
    orders.loc[bad_idx[20:35], "quantity"] = -1
    orders.loc[bad_idx[35:45], "unit_price_egp"] = -10

    # 5. Currency spelling inconsistency.
    orders.loc[orders.sample(frac=0.04, random_state=45).index, "currency"] = "EGP "
    orders.loc[orders.sample(frac=0.02, random_state=46).index, "currency"] = "جنيه مصري"

    # 6. Status capitalization / bilingual drift.
    idx = orders.sample(frac=0.018, random_state=47).index
    orders.loc[idx[:len(idx)//2], "order_status"] = "completed"
    orders.loc[idx[len(idx)//2:], "order_status"] = "Complete"

    # 7. Duplicate orders with same order_id but modified values.
    dups = orders.sample(frac=0.004 if len(orders) > 1000 else 0.01, random_state=48)
    dups = dups.copy()
    dups["net_sales_egp"] = dups["net_sales_egp"] * 1.03
    orders = pd.concat([orders, dups], ignore_index=True)

    # 8. Broken foreign keys: unknown customer/store/product.
    fk_idx = orders.sample(35, random_state=49).index
    orders.loc[fk_idx[:12], "customer_id"] = "C9999999"
    orders.loc[fk_idx[12:22], "store_id"] = "S999"
    orders.loc[fk_idx[22:], "product_id"] = "P999"

    # 9. Date anomalies.
    date_idx = orders.sample(30, random_state=50).index
    orders.loc[date_idx[:15], "order_datetime"] = orders.loc[
        date_idx[:15], "order_datetime"
    ] + pd.Timedelta(days=120)
    orders.loc[date_idx[15:], "order_datetime"] = pd.Timestamp("1900-01-01")

    # 10. Inventory anomalies.
    inv_idx = inventory.sample(150, random_state=51).index
    inventory.loc[inv_idx[:50], "closing_stock"] = -random.randint(1, 10)
    inventory.loc[inv_idx[50:100], "damaged_qty"] = -1
    inventory.loc[inv_idx[100:], "sold_qty"] = inventory.loc[inv_idx[100:], "sold_qty"] * 4

    # 11. Targets missing and duplicated.
    target_drop = targets.sample(frac=0.012, random_state=52).index
    targets = targets.drop(target_drop).reset_index(drop=True)
    target_dup = targets.sample(frac=0.004, random_state=53)
    targets = pd.concat([targets, target_dup], ignore_index=True)

    return customers, products, stores, orders, inventory, targets

def write_excel_sheets(path, sheets):
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)

def write_postgres_like_files(folder, tables):
    folder.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        # CSV represents exports from the operational database.
        df.to_csv(folder / f"{name}.csv", index=False, encoding="utf-8-sig")

def make_data_dictionary():
    rows = [
        ("customers", "customer_id", "Unique customer identifier", "dimension"),
        ("customers", "governorate", "Egyptian governorate", "dimension"),
        ("customers", "customer_segment", "Commercial segment", "dimension"),
        ("products", "product_id", "Unique product identifier", "dimension"),
        ("products", "category", "Product category", "dimension"),
        ("products", "list_price_egp", "Retail list price in EGP", "measure"),
        ("orders", "order_id", "Order identifier", "fact"),
        ("orders", "order_datetime", "Order timestamp", "fact"),
        ("orders", "customer_id", "Customer foreign key", "fact"),
        ("orders", "product_id", "Product foreign key", "fact"),
        ("orders", "store_id", "Store foreign key", "fact"),
        ("orders", "quantity", "Units sold", "measure"),
        ("orders", "net_sales_egp", "Net order sales after discount", "measure"),
        ("orders", "cost_egp", "Estimated product cost", "measure"),
        ("orders", "order_status", "Order lifecycle status", "dimension"),
        ("inventory", "closing_stock", "Month-end inventory", "measure"),
        ("targets", "sales_target_egp", "Monthly store sales target", "measure"),
        ("exchange_rates", "rate", "Currency exchange rate to EGP", "measure"),
    ]
    return pd.DataFrame(rows, columns=["table", "column", "description", "type"])

def write_issue_catalog(path):
    text = """# Intentional Data Quality Problems

This dataset is intentionally imperfect. Do not clean these problems manually
before building the ETL project. They are included as test cases.

## Customer Master
- Exact duplicate customer rows
- Near-duplicate phone formatting
- Upper/lower-case email inconsistency
- Missing phone, email and area
- Governorate casing inconsistency

## Product / Reference Data
- Bilingual Arabic/English naming
- Currency values such as `EGP`, `EGP ` and `جنيه`
- Local/imported product mix
- Cosmetics categories: skincare, makeup, haircare, fragrance, body care

## Orders
- Duplicate order IDs
- Missing/invalid foreign keys
- Quantity = 0
- Negative quantity
- Negative price
- Future-dated transactions
- 1900-01-01 date anomaly
- Status values such as `Completed`, `completed`, `Complete`
- Currency inconsistency
- Mixed Arabic/English channel and payment labels

## Inventory
- Negative closing stock
- Negative damaged quantity
- Implausibly high sold quantity

## Targets
- Missing monthly store targets
- Duplicate target records

## Suggested Data Quality Checks
1. Primary-key uniqueness
2. Foreign-key integrity
3. NOT NULL constraints
4. Accepted-value constraints
5. Positive quantity and price
6. Date validity / freshness
7. Duplicate detection
8. Standardization of bilingual labels
9. Inventory reconciliation
10. Source-to-target row-count reconciliation

The goal is to build a repeatable pipeline that detects, logs and handles these
issues instead of silently fixing them.
"""
    path.write_text(text, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--customers", type=int, default=25000)
    parser.add_argument("--orders", type=int, default=500000)
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--seed", type=int, default=20260921)
    parser.add_argument("--output", default="synthetic_cosmetics_data")
    args = parser.parse_args()

    rng_seed(args.seed)
    out = Path(args.output)
    raw = out / "raw"
    for p in [raw / "postgres_like", raw / "excel", raw / "csv", raw / "api"]:
        p.mkdir(parents=True, exist_ok=True)

    start = pd.Timestamp(args.start)
    end = pd.Timestamp(args.end)

    customers = make_customers(args.customers)
    products = make_products()
    stores = make_stores()
    campaigns = make_campaigns()
    targets = make_targets(stores, products, start, end)
    orders = make_orders(args.orders, customers, products, stores, campaigns, start, end)
    inventory = make_inventory(products, stores, start, months=12)
    exchange_rates = make_exchange_rates(start, end)

    (
        customers, products, stores, orders, inventory, targets
    ) = inject_realistic_issues(
        customers, products, stores, orders, inventory, targets, np.random.default_rng(args.seed)
    )

    # Simulate separate source systems.
    write_postgres_like_files(
        raw / "postgres_like",
        {
            "customers": customers,
            "products": products,
            "stores": stores,
            "orders": orders,
        },
    )

    write_excel_sheets(
        raw / "excel" / "commercial_reference_data.xlsx",
        {
            "Stores": stores,
            "Products": products,
            "Targets": targets,
            "Campaigns": campaigns,
        },
    )

    inventory.to_csv(raw / "csv" / "inventory_monthly.csv", index=False, encoding="utf-8-sig")
    exchange_rates.to_json(
        raw / "api" / "exchange_rates.json",
        orient="records",
        force_ascii=False,
        indent=2,
    )

    dictionary = make_data_dictionary()
    dictionary.to_csv(out / "data_dictionary.csv", index=False, encoding="utf-8-sig")
    write_issue_catalog(out / "README_DATA_ISSUES.md")

    manifest = {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "seed": args.seed,
        "customers_rows": len(customers),
        "orders_rows": len(orders),
        "products_rows": len(products),
        "stores_rows": len(stores),
        "inventory_rows": len(inventory),
        "targets_rows": len(targets),
        "date_range": [args.start, args.end],
        "currency": "EGP",
        "market": "Egypt",
        "sector": "Cosmetics",
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\nSynthetic Egyptian Cosmetics Dataset created.")
    print(f"Output: {out.resolve()}")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    print("\nIntentional data-quality problems are documented in README_DATA_ISSUES.md")

if __name__ == "__main__":
    main()
