"""
Generates a comprehensive, visual Excalidraw file for Cleopatra Cosmetics platform.
"""

import json

def generate_excalidraw():
    elements = []
    
    # Helper to add rectangle
    def add_rect(id_, x, y, w, h, stroke, bg, fill="solid", radius=8):
        elements.append({
            "id": id_,
            "type": "rectangle",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": bg,
            "fillStyle": fill,
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 3},
            "seed": 1000 + len(elements),
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False
        })

    # Helper to add text
    def add_text(id_, x, y, text, size=14, color="#f8fafc", align="left"):
        elements.append({
            "id": id_,
            "type": "text",
            "x": x,
            "y": y,
            "width": len(text.splitlines()[0]) * (size * 0.6),
            "height": len(text.splitlines()) * (size * 1.4),
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": 2000 + len(elements),
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": size,
            "fontFamily": 1,
            "textAlign": align,
            "verticalAlign": "top",
            "baseline": size
        })

    # Helper to add arrow
    def add_arrow(id_, start_x, start_y, end_x, end_y, color="#38bdf8", stroke_width=2):
        elements.append({
            "id": id_,
            "type": "arrow",
            "x": start_x,
            "y": start_y,
            "width": end_x - start_x,
            "height": end_y - start_y,
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": stroke_width,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 2},
            "seed": 3000 + len(elements),
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "points": [[0, 0], [end_x - start_x, end_y - start_y]],
            "lastCommittedPoint": None,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow"
        })

    # Header Card
    add_rect("hdr-box", 60, 40, 2280, 110, "#f59e0b", "#0f172a")
    add_text("hdr-title", 90, 60, "CLEOPATRA MODERN COSMETICS | كليوباترا كوزماتكس الحديثة", 24, "#f8fafc")
    add_text("hdr-sub", 90, 95, "Enterprise Analytics Engineering Blueprint • Kimball Galaxy Fact Constellation, Isolated Quarantine & Power BI Tabular Lifecycle", 13, "#94a3b8")
    add_text("hdr-kpis", 1550, 75, "536,809 Rows Extracted  |  4,628 Quarantined (0.86%)  |  532,181 Clean DW (99.1%)  |  22 Governorates  |  7 Marts  |  55+ DAX", 12, "#38bdf8")

    # Column 1: Sources
    add_rect("c1-box", 60, 180, 320, 780, "#0284c7", "#141e33")
    add_text("c1-title", 80, 200, "1. OPERATIONAL DATA SOURCES", 15, "#38bdf8")
    add_text("c1-sub", 80, 222, "Heterogeneous Extraction (536k Rows)", 11, "#94a3b8")

    add_rect("c1-s1", 75, 250, 290, 180, "#1e3a8a", "#0f172a")
    add_text("c1-s1-t", 85, 260, "🐘 PostgreSQL Operational DB", 12, "#93c5fd")
    add_text("c1-s1-b", 85, 285, "• orders.csv (502,000 rows | 19 cols)\n  PK: order_id | FK: customer, product, store\n• customers.csv (25,200 rows | 11 cols)\n  PK: customer_id | phone (+20), gov\n• products.csv (20 SKUs | 11 cols)\n  PK: product_id | name_ar/en, price\n• stores.csv (35 stores across 22 Governorates)\n  PK: store_id | store_type, area", 10.5, "#e2e8f0")

    add_rect("c1-s2", 75, 445, 290, 120, "#0e7490", "#0f172a")
    add_text("c1-s2-t", 85, 455, "📦 Supply Chain WMS ERP", 12, "#67e8f9")
    add_text("c1-s2-b", 85, 480, "• inventory_monthly.csv (8,400 rows)\n  Monthly Store × SKU Balance Snapshot\n  Open + Recv - Sold - Damaged = Close\n  Tracks Stockout Risk Flags & Damage %", 10.5, "#e2e8f0")

    add_rect("c1-s3", 75, 580, 290, 120, "#047857", "#0f172a")
    add_text("c1-s3-t", 85, 590, "📊 Commercial Reference (Excel)", 12, "#6ee7b7")
    add_text("c1-s3-b", 85, 615, "• Sheet Targets: 417 monthly quotas\n  PK: target_month + store_id\n• Sheet Campaigns: 7 marketing events\n  Ramadan, White Friday, Eid, Summer", 10.5, "#e2e8f0")

    add_rect("c1-s4", 75, 715, 290, 100, "#d97706", "#0f172a")
    add_text("c1-s4-t", 85, 725, "🌐 Central Bank API (JSON)", 12, "#fcd34d")
    add_text("c1-s4-b", 85, 750, "• exchange_rates.json (730 FX rates)\n  Daily closing rates: USD, EUR, GBP to EGP\n  Base reporting currency standardization", 10.5, "#e2e8f0")

    add_rect("c1-eng", 75, 830, 290, 105, "#1e3a8a", "#0b132b")
    add_text("c1-eng-t", 85, 840, "⚡ Python ELT Orchestrator", 11.5, "#38bdf8")
    add_text("c1-eng-b", 85, 860, "• pyodbc fast_executemany streaming\n• SHA-256 deterministic fingerprinting\n• Chunked at 10,000 rows/batch\n• Ingests 536k rows in 4.8s (90k rows/s inc)", 10, "#94a3b8")

    # Arrow Col 1 to 2
    add_arrow("arr-1-2", 380, 570, 420, 570, "#38bdf8", 3)

    # Column 2: Bronze
    add_rect("c2-box", 420, 180, 280, 780, "#38bdf8", "#141e33")
    add_text("c2-title", 440, 200, "2. BRONZE LAYER", 15, "#22d3ee")
    add_text("c2-sub", 440, 222, "SQL Server 2022 bronze.*", 11, "#94a3b8")

    add_rect("c2-card", 435, 250, 250, 140, "#0369a1", "#082f49")
    add_text("c2-c-t", 445, 260, "🔒 Lossless Raw Persistence", 12, "#38bdf8")
    add_text("c2-c-b", 445, 285, "• All columns NVARCHAR(MAX)\n• Zero cast / numeric truncation\n• Collation: Arabic_100_CI_AS\n• Mandatory Audit Columns:\n  _source_file, _batch_id (UUID)\n  _ingested_at, _row_hash (SHA-256)", 10.5, "#bae6fd")

    add_rect("c2-tbls", 435, 410, 250, 360, "#1e293b", "#0f172a")
    add_text("c2-tbl-t", 445, 425, "Physical Tables (8 Tables):", 12, "#f8fafc")
    add_text("c2-tbl-b", 445, 455, "• bronze.raw_orders (502,000)\n• bronze.raw_customers (25,200)\n• bronze.raw_inventory (8,400)\n• bronze.raw_commercial_targets (417)\n• bronze.raw_exchange_rates (730)\n• bronze.raw_products (20)\n• bronze.raw_stores (35)\n• bronze.raw_campaigns (7)\n\nAudit Ledger:\naudit.pipeline_execution_log\nTracks execution runtime, SLA, rows", 10.5, "#94a3b8")

    # Arrow Col 2 to 3
    add_arrow("arr-2-3", 700, 570, 740, 570, "#22d3ee", 3)

    # Column 3: Staging
    add_rect("c3-box", 740, 180, 320, 780, "#818cf8", "#141e33")
    add_text("c3-title", 760, 200, "3. STAGING ENGINE", 15, "#818cf8")
    add_text("c3-sub", 760, 222, "staging.usp_load_staging", 11, "#94a3b8")

    add_rect("c3-t1", 755, 250, 290, 110, "#4338ca", "#1e1b4b")
    add_text("c3-t1-t", 765, 260, "📱 Mobile Phone Normalization", 11.5, "#a5b4fc")
    add_text("c3-t1-b", 765, 285, "Input: '+20 10 1234 5678'\n➔ Clean: '01012345678' (11 digits)\nDetects Egyptian Telecom Carrier:\nVodafone (010), Orange (012), Etisalat (011), WE (015)", 10, "#e0e7ff")

    add_rect("c3-t2", 755, 375, 290, 110, "#4338ca", "#1e1b4b")
    add_text("c3-t2-t", 765, 385, "🏛️ 22 Egyptian Governorates", 11.5, "#a5b4fc")
    add_text("c3-t2-b", 765, 410, "Input: 'cairo' / 'القاهره'\n➔ Clean: 'Cairo' | 'القاهرة'\nMaps to 5 Economic Regions:\nGreater Cairo, Delta, Canal, Upper Egypt, Frontier\nAssigns Courier SLA: 24h, 48h, 72h", 10, "#e0e7ff")

    add_rect("c3-t3", 755, 500, 290, 100, "#4338ca", "#1e1b4b")
    add_text("c3-t3-t", 765, 510, "💵 Currency & Math Integrity", 11.5, "#a5b4fc")
    add_text("c3-t3-b", 765, 535, "Input: 'جنيه' / 'ج.م' ➔ 'EGP' Canonical\nEnforces: Net = Gross - Discount\nStrong casting to DECIMAL(12,2)\nSurrogate DateKey: YYYYMMDD (INT)", 10, "#e0e7ff")

    add_rect("c3-tbls", 755, 620, 290, 310, "#1e293b", "#0f172a")
    add_text("c3-tbl-t", 765, 635, "Staging Output Tables:", 12, "#f8fafc")
    add_text("c3-tbl-b", 765, 660, "• staging.stg_orders (502,000)\n• staging.stg_customers (25,200)\n• staging.stg_inventory (8,400)\n• staging.stg_commercial_targets (417)\n• staging.stg_exchange_rates (730)\n• staging.stg_products (20)\n• staging.stg_stores (35)\n\nForwarded to Data Quality Sentinel\n16 automated assertions applied", 10.5, "#94a3b8")

    # Arrow Col 3 to 4
    add_arrow("arr-3-4", 1060, 570, 1100, 570, "#818cf8", 3)

    # Column 4: DQ Sentinel & Quarantine
    add_rect("c4-box", 1100, 180, 350, 780, "#f43f5e", "#141e33")
    add_text("c4-title", 1120, 200, "4. DQ SENTINEL & QUARANTINE", 15, "#fb7185")
    add_text("c4-sub", 1120, 222, "dq.usp_run_dq_checks (16 Rules)", 11, "#94a3b8")

    add_rect("c4-gate", 1115, 250, 320, 140, "#be123c", "#200b11")
    add_text("c4-gate-t", 1125, 260, "🛡️ Automated Sentinel Gate", 12.5, "#fda4af")
    add_text("c4-gate-b", 1125, 285, "• 16 Automated Assertions:\n  PK Unique, FK Referential, Math Equalities,\n  Positive Quantities, Phone Regex, Dates\n• Split Decisions:\n  Green: 99.14% Valid ➔ Warehouse\n  Red: 0.86% Defective ➔ Quarantine Vault", 10.5, "#fecdd3")

    add_rect("c4-pass", 1115, 410, 320, 85, "#059669", "#062419")
    add_text("c4-pass-t", 1125, 420, "✓ VALIDATED STREAM (99.14% PASS)", 12, "#34d399")
    add_text("c4-pass-b", 1125, 445, "532,181 Clean Rows loaded into DW:\nSales (497k) • Customers (24.8k) • Inventory (8.3k)", 10.5, "#d1fae5")

    add_rect("c4-fail", 1115, 515, 320, 420, "#be123c", "#1c0a11")
    add_text("c4-fail-t", 1125, 530, "⚠️ QUARANTINE VAULT (0.86% DEFECT)", 12, "#fb7185")
    add_text("c4-fail-b", 1125, 555, "4,628 Defective Rows Safely Isolated:\n\n• dq.rejected_orders (4,124 rows):\n  - Orphan Customer FK: 2,840 rows\n  - Negative Qty / Price: 812 rows\n  - Invalid Store ID: 310 rows\n  - Future Order Dates: 162 rows\n\n• dq.rejected_customers (400 rows):\n  - Malformed Phone (non-EG length): 260\n  - Unmapped Governorateernorate typo: 95\n  - Missing Customer Name: 45\n\n• dq.rejected_inventory (100 rows):\n  - Negative Closing Stock: 62\n  - Equation Gap Mismatch: 38\n\n• dq.rejected_targets (4 rows):\n  - Negative Sales Quota values\n\nLedger: dq.data_quality_results (100% Traceable)", 10, "#fecdd3")

    # Arrow Col 4 Pass to 5
    add_arrow("arr-4-5", 1450, 450, 1490, 450, "#34d399", 4)

    # Column 5: Kimball Galaxy DW
    add_rect("c5-box", 1490, 180, 450, 780, "#10b981", "#141e33")
    add_text("c5-title", 1510, 200, "5. KIMBALL GALAXY DATA WAREHOUSE", 15, "#34d399")
    add_text("c5-sub", 1510, 222, "warehouse.* | Fact Constellation + Snowflake", 11, "#94a3b8")

    # Fact Cards
    add_rect("c5-f1", 1505, 250, 420, 120, "#059669", "#031a12")
    add_text("c5-f1-t", 1515, 260, "⭐ fact_sales (497,876 Rows)", 12.5, "#34d399")
    add_text("c5-f1-b", 1515, 285, "Grain: 1 Order Line-Item Transaction\nKeys: sales_key (PK), order_id (Degenerate)\nFKs: date_key, customer_key, product_key, store_key, campaign_key\nMeasures: quantity, gross_sales, discount_egp, net_sales, cost, profit", 10, "#d1fae5")

    add_rect("c5-f2", 1505, 385, 420, 95, "#059669", "#031a12")
    add_text("c5-f2-t", 1515, 395, "⭐ fact_inventory (8,300 Rows)", 12.5, "#34d399")
    add_text("c5-f2-b", 1515, 420, "Grain: Monthly Snapshot per Store per SKU\nFKs: date_key, store_key, product_key\nMeasures: opening_stock, received, sold, damaged, closing_stock\nKPIs: Days of Inventory (DOI), Stockout Risk Flags", 10, "#d1fae5")

    add_rect("c5-f3", 1505, 495, 420, 85, "#059669", "#031a12")
    add_text("c5-f3-t", 1515, 505, "⭐ fact_store_targets (413 Rows)", 12.5, "#34d399")
    add_text("c5-f3-b", 1515, 530, "Grain: Monthly Performance Quota per Store\nFKs: target_date_key, store_key\nMeasures: sales_target_egp, order_target, target_achievement_pct", 10, "#d1fae5")

    # Conformed Dims & Snowflake
    add_rect("c5-dims", 1505, 595, 420, 200, "#0284c7", "#071927")
    add_text("c5-dim-t", 1515, 605, "Conformed Core Dimensions (warehouse.*):", 12, "#38bdf8")
    add_text("c5-dim-b", 1515, 630, "• dim_customer (24,800 active | SCD Type 2)\n  valid_from, valid_to, is_current, carrier_key, age_cohort\n• dim_product (20 SKUs | Egyptian Price Tiers & Domestic)\n• dim_store (35 Retail Boutiques across 22 Governorates)\n• dim_date (730 Days | Egyptian Fri/Sat Weekends)\n• dim_currency (Daily FX conversion to USD/EUR)", 10, "#bae6fd")

    add_rect("c5-snow", 1505, 810, 420, 130, "#0f766e", "#042f2c")
    add_text("c5-snow-t", 1515, 820, "❄️ Snowflake Hierarchy Outriggers:", 12, "#5eead4")
    add_text("c5-snow-b", 1515, 845, "1. dim_geography: 22 Governorates ➔ 5 Economic Regions ➔ 3 Courier SLAs\n2. dim_category: Product ➔ Subcategory ➔ Strategic Margin Class\n3. dim_telecom_carrier: Vodafone, Orange, Etisalat, WE Egypt\nStrictly 1:Many Single-Direction Relationships (Pure Star Topology)", 10, "#ccfbf1")

    # Arrow Col 5 to 6
    add_arrow("arr-5-6", 1940, 570, 1980, 570, "#c084fc", 3.5)

    # Column 6: Marts & Power BI
    add_rect("c6-box", 1980, 180, 360, 780, "#c084fc", "#141e33")
    add_text("c6-title", 2000, 200, "6. MARTS & POWER BI", 15, "#c084fc")
    add_text("c6-sub", 2000, 222, "mart.* & Cleopatra_Cosmetics_Report.pbip", 11, "#94a3b8")

    add_rect("c6-marts", 1995, 250, 330, 240, "#6d28d9", "#150e28")
    add_text("c6-m-t", 2005, 260, "7 Curated Business Marts (mart.*):", 12, "#e9d5ff")
    add_text("c6-m-b", 2005, 285, "• mart.mart_daily_sales (271.6k rows)\n  Date × Store × Channel operational trends\n• mart.mart_monthly_sales (425 rows)\n  C-Suite monthly revenue & quota tracking\n• mart.mart_product_performance (20 SKUs)\n  Margin %, velocity, return rates & rank\n• mart.mart_customer_retention_rfm (24.8k)\n  Champions, Loyal, At-Risk, Lost segments\n• mart.mart_inventory_health (8.3k rows)\n  Days of Inventory & stockout risk sentinel\n• mart.mart_marketing_roi (7 campaigns)\n• mart.v_pipeline_health (ETL SLA audit)", 10, "#ddd6fe")

    add_rect("c6-pbi", 1995, 505, 330, 220, "#581c87", "#130d24")
    add_text("c6-p-t", 2005, 515, "Power BI Tabular Suite (.pbip):", 12, "#faf5ff")
    add_text("c6-p-b", 2005, 540, "In-Engine M Data Lifecycle:\n00_Params ➔ 01_Src ➔ 02_Stg ➔ 04_Cln ➔ 07_Model\n\n55+ Production DAX Measures:\n📁 01 Financials: Gross, Net, Margin %, COGS\n📁 02 Targets: Quotas, % Attain, Gap\n📁 03 Customer RFM: CLV, Repeat, Churn\n📁 04 Inventory: Stockout Risk, DOI\n📁 05 FX Multi-Currency: USD/EUR Rates\n📁 06 Time Intel: YTD, MoM %, YoY %, Rolling", 10, "#ddd6fe")

    add_rect("c6-pages", 1995, 740, 330, 195, "#4c1d95", "#0a0614")
    add_text("c6-pg-t", 2005, 750, "5 Executive Report Pages:", 12, "#faf5ff")
    add_text("c6-pg-b", 2005, 775, "1. 🏛️ Executive Pulse Scorecard (C-Suite KPIs)\n2. 🗺️ Egypt Regional Penetration (22 Governorates, SLAs)\n3. 👥 Customer RFM & LTV (Carrier Affinities)\n4. 📦 Inventory Health & Stockouts (DOI Warnings)\n5. 🎯 Targets & Campaign ROAS (Store Quotas)\n\nZero cross-filter ambiguity | Pure 1:Many Model", 10, "#ddd6fe")

    excalidraw_data = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "viewBackgroundColor": "#070b14",
            "gridSize": 20
        },
        "files": {}
    }

    with open("docs/diagrams/project_lifecycle.excalidraw", "w", encoding="utf-8") as f:
        json.dump(excalidraw_data, f, indent=2, ensure_ascii=False)
    print(f"Updated docs/diagrams/project_lifecycle.excalidraw ({len(elements)} visual elements)")

if __name__ == "__main__":
    generate_excalidraw()
