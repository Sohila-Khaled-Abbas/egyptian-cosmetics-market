# Cleopatra Modern Cosmetics — Complete Project Lifecycle Architecture & Technical Data Blueprint

This document is the authoritative architectural and operational specification for **Cleopatra Modern Cosmetics (كليوباترا كوزماتكس الحديثة)**. It outlines how heterogeneous operational source data flows through lossless bronze ingestion, deterministic staging standardization, automated data quality quarantining, Kimball Galaxy dimensional modeling, curated business marts, and executive Power BI reporting.

---

## 1. High-Resolution Visual Architecture Blueprint

The complete end-to-end data platform lifecycle is visualized in the production blueprint below, designed strictly to reflect the project's actual datasets, tables, row counts, stored procedures, and analytical marts:

![Cleopatra Cosmetics Modern Project Lifecycle Diagram](file:///d:/courses/Data%20Science/Data%20Engineering/Projects/egyptian_cosmetics_market/docs/diagrams/project_lifecycle.png)

> [!TIP]
> **Lossless Vector SVG & Editable Excalidraw Formats:**
> * 🎨 **Vector SVG (Lossless Zoom & High DPI)**: [project_lifecycle.svg](file:///d:/courses/Data%20Science/Data%20Engineering/Projects/egyptian_cosmetics_market/docs/diagrams/project_lifecycle.svg)
> * ✏️ **Editable Excalidraw Board**: [project_lifecycle.excalidraw](file:///d:/courses/Data%20Science/Data%20Engineering/Projects/egyptian_cosmetics_market/docs/diagrams/project_lifecycle.excalidraw)

---

## 2. Interactive Mermaid Architecture Flowchart

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#1E293B', 'primaryTextColor': '#F8FAFC', 'primaryBorderColor': '#38BDF8', 'lineColor': '#38BDF8', 'secondaryColor': '#0F172A', 'tertiaryColor': '#1E1B4B' }}}%%
flowchart TD

    %% Stage 1: Operational Sources
    subgraph STAGE1["<b>1. MULTI-SOURCE OPERATIONAL DATASETS</b>"]
        direction TB
        S1["<b>PostgreSQL Operational DB (CSV)</b><br/>• customers.csv (25,200 rows | 11 cols)<br/>• orders.csv (502,000 rows | 19 cols)<br/>• products.csv (20 SKUs | 11 cols)<br/>• stores.csv (35 stores | 7 cols)"]
        S2["<b>Supply Chain ERP (CSV)</b><br/>• inventory_monthly.csv (8,400 monthly snapshots)"]
        S3["<b>Commercial Reference (Excel)</b><br/>• commercial_reference_data.xlsx<br/>  - Sheet Targets: 417 monthly quotas<br/>  - Sheet Campaigns: 7 marketing events"]
        S4["<b>Central Bank of Egypt API (JSON)</b><br/>• exchange_rates.json (730 daily FX rates)"]
    end

    %% Stage 2: Bronze Lossless
    subgraph STAGE2["<b>2. BRONZE INGESTION LAYER (SQL SERVER 2022)</b>"]
        direction TB
        B1["<b>Schema: bronze.*</b><br/>• Lossless raw strings (NVARCHAR(MAX))<br/>• SHA-256 _row_hash fingerprinting<br/>• Lineage: _source_file, _batch_id, _ingested_at<br/>• Raw tables: raw_orders (502k), raw_customers (25.2k),<br/>  raw_inventory (8.4k), raw_targets (417), raw_fx (730)"]
    end

    %% Stage 3: Staging & Standardization
    subgraph STAGE3["<b>3. STAGING & CLEANSING ENGINE</b>"]
        direction TB
        STG1["<b>Stored Procedure: staging.usp_load_staging</b><br/>• Phone Standardizer: +20 10... ➔ 010... (Vodafone/Orange/Etisalat/WE)<br/>• 22 Egyptian Governorates Canonical Arabic/English Alignment<br/>• Currency Canonicalization: جنيه, ج.م, EGP ➔ EGP Canonical<br/>• Order Status Mapping: مكتمل ➔ Completed | مرتجع ➔ Returned<br/>• Integer Surrogate DateKey Generation: YYYYMMDD"]
    end

    %% Stage 4: Data Quality Sentinel & Quarantine
    subgraph STAGE4["<b>4. DATA QUALITY SENTINEL & ISOLATED QUARANTINE</b>"]
        direction TB
        DQ_ENGINE{"<b>dq.usp_run_dq_checks</b><br/>16 Automated Assertions"}
        QUARANTINE["<b>Quarantine Tables (dq.rejected_*)</b><br/>• rejected_orders: 4,124 rows (Orphan FKs, negative prices)<br/>• rejected_customers: 400 rows (Malformed phone, bad gov)<br/>• rejected_inventory: 100 rows (Negative stock, math error)<br/>• rejected_targets: 4 rows (Negative revenue target)<br/><i>4,628 Defective Rows Safely Isolated (0.86% Defect Rate)</i>"]
        AUDIT["<b>Audit & Observability Ledger</b><br/>• dq.data_quality_results (Pass %, fail counts, rule IDs)<br/>• audit.pipeline_execution_log (SLA, duration, run status)"]
    end

    %% Stage 5: Kimball Galaxy Warehouse
    subgraph STAGE5["<b>5. KIMBALL GALAXY DATA WAREHOUSE & SNOWFLAKE OUTRIGGERS</b>"]
        direction TB
        subgraph SNOWFLAKE["Snowflake Hierarchy Outriggers"]
            DIM_GEO["<b>dim_geography</b><br/>22 Governorates ➔ 5 Economic Regions<br/>3 Market Tiers ➔ Courier Delivery SLAs"]
            DIM_CAT["<b>dim_category & dim_subcategory</b><br/>Formulation Types ➔ Strategic Margin Classes"]
            DIM_CAR["<b>dim_telecom_carrier</b><br/>Vodafone (010), Orange (012), Etisalat (011), WE (015)"]
        end
        subgraph CONFORMED["Conformed Core Dimensions"]
            DIM_D["<b>dim_date</b> (730 Days, Egyptian Fri/Sat Weekends)"]
            DIM_C["<b>dim_customer</b> (24,800 Active Rows | SCD Type 2)"]
            DIM_P["<b>dim_product</b> (20 SKUs | Egyptian Price Tiers & Domestic Origin)"]
            DIM_S["<b>dim_store</b> (35 Stores | Retail Footprint & Regional Hubs)"]
            DIM_FX["<b>dim_currency</b> (EGP Base, FX Multipliers)"]
        end
        subgraph FACTS["Galaxy Multi-Process Facts (532,181 Total Clean Rows)"]
            FACT_S["<b>fact_sales</b> (497,876 Rows)<br/>Grain: 1 Order Line-Item"]
            FACT_I["<b>fact_inventory</b> (8,300 Rows)<br/>Grain: Monthly Snapshot per Store/SKU"]
            FACT_T["<b>fact_store_targets</b> (413 Rows)<br/>Grain: Store Monthly Revenue & Volume Quota"]
        end
    end

    %% Stage 6: Curated Marts
    subgraph STAGE6["<b>6. CURATED BUSINESS MARTS (Schema: mart.*)</b>"]
        direction TB
        M1["mart.mart_daily_sales (271.6k aggregated rows)"]
        M2["mart.mart_monthly_sales (425 executive monthly rows)"]
        M3["mart.mart_product_performance (20 SKUs margin & velocity)"]
        M4["mart.mart_customer_retention_rfm (24.8k scored customers)"]
        M5["mart.mart_inventory_health (8.3k rows: DOI & stockouts)"]
        M6["mart.mart_marketing_roi (7 marketing campaigns)"]
        M7["mart.v_pipeline_health (ETL SLA & observability)"]
    end

    %% Stage 7: Power BI Platform
    subgraph STAGE7["<b>7. POWER BI ENTERPRISE TABULAR PLATFORM (.PBIP)</b>"]
        direction TB
        PBI_IN_ENGINE["<b>Power Query M In-Engine Data Lifecycle</b><br/>00_Parameters ➔ 01_Source ➔ 02_Staging ➔ 03_Reference ➔<br/>04_Cleansed ➔ 05_Validated ➔ 06_Transformations ➔ 07_Model"]
        PBI_MODEL["<b>Tabular Star / Galaxy Model</b><br/>• Strictly 1:Many Single-Direction Relationships<br/>• _Measures Table: 55+ Production DAX Measures in 6 Display Folders"]
        PBI_REPORTS["<b>Executive Reporting Suite (5 Pages)</b><br/>1. Executive Pulse Scorecard | 2. Egypt Regional Penetration<br/>3. Customer LTV & RFM | 4. Inventory Health & Stockouts | 5. Targets & ROAS"]
    end

    %% Data Flow Lineage
    S1 & S2 & S3 & S4 ==> STAGE2
    STAGE2 ==> STAGE3
    STAGE3 ==> DQ_ENGINE
    DQ_ENGINE -->|Failed Checks (4,628 Rows)| QUARANTINE
    DQ_ENGINE -->|Execution Telemetry| AUDIT
    DQ_ENGINE ==>|Validated Clean (532,181 Rows)| STAGE5
    DIM_GEO --> DIM_S & DIM_C
    DIM_CAT --> DIM_P
    DIM_CAR --> DIM_C
    CONFORMED ==> FACTS
    FACTS ==> STAGE6
    STAGE6 ==> STAGE7
    STAGE5 -.->|Direct Import / Direct Lake| PBI_MODEL

    %% Styling
    classDef sourceStyle fill:#0F172A,stroke:#0284C7,stroke-width:2px,color:#F8FAFC;
    classDef bronzeStyle fill:#082F49,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC;
    classDef stagingStyle fill:#1E1B4B,stroke:#818CF8,stroke-width:2px,color:#F8FAFC;
    classDef dqStyle fill:#2A0B14,stroke:#F43F5E,stroke-width:2px,color:#FFE4E6;
    classDef whStyle fill:#062419,stroke:#10B981,stroke-width:2px,color:#ECFDF5;
    classDef martStyle fill:#14532D,stroke:#34D399,stroke-width:2px,color:#F0FDF4;
    classDef pbiStyle fill:#150E28,stroke:#C084FC,stroke-width:2px,color:#FAF5FF;

    class S1,S2,S3,S4 sourceStyle;
    class B1 bronzeStyle;
    class STG1 stagingStyle;
    class DQ_ENGINE,QUARANTINE,AUDIT dqStyle;
    class DIM_GEO,DIM_CAT,DIM_CAR,DIM_D,DIM_C,DIM_P,DIM_S,DIM_FX,FACT_S,FACT_I,FACT_T whStyle;
    class M1,M2,M3,M4,M5,M6,M7 martStyle;
    class PBI_IN_ENGINE,PBI_MODEL,PBI_REPORTS pbiStyle;
```

---

## 3. Master Operational Datasets Catalog

The platform ingests from four distinct operational subsystems comprising 7 physical datasets:

| System / Protocol | Physical File Path | File Format | Row Count | Attributes | Primary Business Grain | Key Identity Columns |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **PostgreSQL DB** | `data/raw/postgres_like/orders.csv` | CSV | $502,000$ | 19 | 1 Order Line-Item Transaction | `order_id` (PK), `customer_id`, `product_id`, `store_id` |
| **PostgreSQL DB** | `data/raw/postgres_like/customers.csv` | CSV | $25,200$ | 11 | Registered Customer Entity | `customer_id` (PK), `phone`, `email`, `governorate` |
| **PostgreSQL DB** | `data/raw/postgres_like/products.csv` | CSV | $20$ | 11 | Master Commercial SKU | `product_id` (PK), `brand_en`, `category`, `list_price_egp` |
| **PostgreSQL DB** | `data/raw/postgres_like/stores.csv` | CSV | $35$ | 7 | Retail Store / Hub Location | `store_id` (PK), `governorate`, `area`, `store_type` |
| **Supply Chain ERP**| `data/raw/csv/inventory_monthly.csv` | CSV | $8,400$ | 8 | Monthly Store-SKU Stock Balance | `month` + `store_id` + `product_id` (Composite PK) |
| **Commercial Excel** | `data/raw/excel/commercial_reference_data.xlsx` (`Targets`) | XLSX | $417$ | 4 | Store Monthly Target Quota | `target_month` + `store_id` (Composite PK) |
| **Commercial Excel** | `data/raw/excel/commercial_reference_data.xlsx` (`Campaigns`)| XLSX | $7$ | 6 | Marketing Event Parameters | `campaign_id` (PK), `start_date`, `end_date`, `budget` |
| **Central Bank API** | `data/raw/api/exchange_rates.json` | JSON | $730$ | 5 | Daily Forex Quote (2023–2024) | `date` + `currency` (Composite PK), `rate_to_egp` |

---

## 4. Stage-by-Stage Engineering Lifecycle

### Stage 1: Multi-Source Operational Extraction
- **Orchestration**: Automated Python ELT runner (`scripts/run_pipeline.py`).
- **Extraction Protocol**: Native `pyodbc` with `fast_executemany = True` chunked at 10,000 rows per batch.
- **Performance**: Ingests all 536,809 raw rows in ~4.8 seconds.

### Stage 2: Bronze Raw Persistence (`bronze.*`)
- **Lossless Ingestion**: All columns ingested as `NVARCHAR(MAX)` to guarantee that no source formatting anomaly or type overflow truncates data during initial capture.
- **Collation**: `Arabic_100_CI_AS` strictly preserved for Egyptian Arabic characters.
- **Audit Lineage**: Every row receives four immutable governance columns:
  - `_source_file`: Path of origin.
  - `_batch_id`: Ingestion execution UUID-v4.
  - `_ingested_at`: UTC timestamp.
  - `_row_hash`: SHA-256 hash of concatenated raw attributes for change detection.

### Stage 3: Staging & Cleansing Engine (`staging.*`)
- **Execution**: Stored procedure `staging.usp_load_staging`.
- **Egyptian Market Normalizations**:
  1. **Mobile Phone MSISDN Standardization**: Standardizes `+20 10...`, `+20 11...`, `+20 12...`, and `+20 15...` to unified local 11-digit numbers (`010...`, `011...`, `012...`, `015...`).
  2. **22 Egyptian Governorates Canonical Alignment**: Translates Arabic and English names into canonical keys mapped to 5 economic regions:
     - *Greater Cairo*: Cairo, Giza, Qalyubia.
     - *Alexandria & Delta*: Alexandria, Beheira, Gharbia, Dakahlia, Sharqia, Monufia, Kafr El Sheikh, Damietta.
     - *Canal Zone*: Port Said, Ismailia, Suez.
     - *Upper Egypt*: Fayoum, Beni Suef, Minya, Asyut, Sohag, Qena, Luxor, Aswan.
     - *Frontier & Red Sea*: Red Sea, South Sinai, North Sinai, Matrouh, New Valley.
  3. **Courier SLA Tiering**: Assigns shipping SLAs based on regional distribution hubs (Tier 1: 24h express, Tier 2: 48h standard, Tier 3: 72h regional).
  4. **Currency Canonicalization**: Unifies `جنيه`, `ج.م`, `EGP` into canonical `EGP`.
  5. **Order Status State Machine**: Maps operational Arabic statuses (`مكتمل` $\rightarrow$ `Completed`, `مرتجع` $\rightarrow$ `Returned`, `ملغي` $\rightarrow$ `Cancelled`).
  6. **Surrogate DateKey**: Casts datetimes to integer surrogate keys (`YYYYMMDD`) for high-performance join operations.

### Stage 4: Data Quality Sentinel & Isolated Quarantine (`dq.*`)
- **Execution**: Stored procedure `dq.usp_run_dq_checks` executing 16 automated assertions.
- **Isolated Quarantine Tables (`dq.rejected_*`)**: Defective rows are immediately routed out of the pipeline so they cannot corrupt the warehouse, but are never deleted:
  - `dq.rejected_orders` (**4,124 rows**): 2,840 orphaned customer IDs, 812 negative quantities/prices, 310 invalid store IDs, 162 future timestamps.
  - `dq.rejected_customers` (**400 rows**): 260 malformed phone numbers, 95 unrecognized governorates, 45 null names.
  - `dq.rejected_inventory` (**100 rows**): 62 negative closing stocks, 38 balance equation mismatches.
  - `dq.rejected_targets` (**4 rows**): Negative target revenue values entered into Excel.
- **Telemetry**: All checks are permanently logged in `dq.data_quality_results` tracking pass rates, failure counts, and rule IDs. Overall system pass rate is **99.14%** (532,181 clean rows passed).

### Stage 5: Kimball Galaxy Data Warehouse (`warehouse.*`)
- **Execution**: Stored procedures `warehouse.usp_load_dimensions` and `warehouse.usp_load_facts`.
- **Galaxy Fact Constellation**:
  - `warehouse.fact_sales` (**497,876 rows**): Grain is 1 order line-item.
  - `warehouse.fact_inventory` (**8,300 rows**): Grain is monthly store/product balance.
  - `warehouse.fact_store_targets` (**413 rows**): Grain is monthly retail store quota.
- **Conformed Dimensions**:
  - `dim_customer` (**24,800 active rows**): Slowly Changing Dimension (SCD Type 2) tracking historical changes with `valid_from`, `valid_to`, `is_current`, enriched with Egyptian Telecom carrier network and age cohort.
  - `dim_product` (**20 SKUs**): Enriched with price tiers (*Mass <150 EGP*, *Masstige 150–350 EGP*, *Prestige 350–600 EGP*, *Luxury >600 EGP*) and formulation origin (*Local Egyptian vs Imported*).
  - `dim_store` (**35 stores**): Omnichannel footprints (*Flagship, Mall Boutique, High Street*) across 22 governorates.
  - `dim_date` (**730 calendar days**): Role-playing dimension for Order Date, Target Month, and Inventory Month, configured with Egyptian weekend rules (Friday/Saturday) and major commercial seasons (*Ramadan, White Friday, Eid*).
  - `dim_currency` (**730 rows**): Daily FX multipliers to convert EGP to USD, EUR, and GBP.
- **Snowflake Outriggers**:
  - `dim_geography`: Normalizes Governorates $\rightarrow$ Economic Regions $\rightarrow$ Courier SLA Tiers.
  - `dim_category`: Normalizes Product $\rightarrow$ Subcategory $\rightarrow$ Category $\rightarrow$ Strategic Margin Class.
  - `dim_telecom_carrier`: Identifies carrier from mobile prefix (`010` Vodafone, `011` Etisalat, `012` Orange, `015` WE).

### Stage 6: Curated Analytics Marts (`mart.*`)
The warehouse exposes 7 curated, pre-aggregated business views and tables:
1. `mart.mart_daily_sales` ($271,600$ rows): Aggregated by Date, Store, Channel, and Payment Method.
2. `mart.mart_monthly_sales` ($425$ rows): Executive monthly revenue, target attainment, and MoM growth.
3. `mart.mart_product_performance` ($20$ rows): SKU sales velocity, gross margin %, return rates, and stockout frequency.
4. `mart.mart_customer_retention_rfm` ($24,800$ rows): Recency, Frequency, and Monetary scores categorizing customers into Champions, Loyal, At-Risk, and Hibernating.
5. `mart.mart_inventory_health` ($8,300$ rows): Days of Inventory (DOI), stockout risk warning flags, and damage rates.
6. `mart.mart_marketing_roi` ($7$ rows): Campaign ROAS, incremental sales uplift, and customer acquisition cost.
7. `mart.v_pipeline_health`: Live ETL telemetry, SLA compliance, and execution duration.

### Stage 7: Power BI Enterprise Tabular Platform (`.pbip`)
- **Semantic Model**: Built strictly on 1:Many single-direction relationships to avoid ambiguous paths and cross-filter degradation.
- **DAX Measures**: 55+ production DAX measures structured into 6 display folders:
  - 📁 `01 Financials & Revenue`
  - 📁 `02 Target & Variance`
  - 📁 `03 Customer RFM & LTV`
  - 📁 `04 Inventory Health & DOI`
  - 📁 `05 FX Multi-Currency`
  - 📁 `06 Time Intelligence`
- **Executive Reporting Pages**:
  - **Page 1: 🏛️ Executive Pulse Scorecard**: C-suite KPI cards, monthly revenue vs targets, margin gauge, top SKUs.
  - **Page 2: 🗺️ Egypt Regional Penetration**: 22 governorates drill-down, 5 economic regions, courier SLA delivery latency.
  - **Page 3: 👥 Customer Lifetime Value & RFM**: RFM quadrant scatter plot, carrier market share, customer cohort retention.
  - **Page 4: 📦 Inventory Health & Stockouts**: Stockout risk matrix by store/SKU, Days of Inventory (DOI), damaged stock cost.
  - **Page 5: 🎯 Targets & Campaign ROAS**: Monthly store quota achievement, marketing campaign ROI, promotional uplift.
