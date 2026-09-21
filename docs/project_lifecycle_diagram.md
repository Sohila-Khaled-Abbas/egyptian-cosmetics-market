# Cleopatra Modern Cosmetics — Complete Project Lifecycle Architecture

This document presents the full, end-to-end analytics engineering and Power BI data lifecycle for **Cleopatra Modern Cosmetics (كليوباترا كوزماتكس الحديثة)**. It illustrates how raw, heterogeneous operational data flows through ingestion, automated data quality quarantining, Kimball Galaxy dimensional modeling, curated business marts, and executive Power BI reporting.

---

## 1. High-Resolution Visual Architecture Diagram

![Cleopatra Cosmetics Modern Project Lifecycle Diagram](file:///d:/courses/Data%20Science/Data%20Engineering/Projects/egyptian_cosmetics_market/docs/diagrams/project_lifecycle.png)

> [!TIP]
> **Vector SVG & Excalidraw Formats:**
> * 🎨 **Vector SVG (Lossless Zoom)**: [project_lifecycle.svg](file:///d:/courses/Data%20Science/Data%20Engineering/Projects/egyptian_cosmetics_market/docs/diagrams/project_lifecycle.svg)
> * ✏️ **Editable Excalidraw Board**: [project_lifecycle.excalidraw](file:///d:/courses/Data%20Science/Data%20Engineering/Projects/egyptian_cosmetics_market/docs/diagrams/project_lifecycle.excalidraw)

---

## 2. Interactive Mermaid Architecture Flowchart

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#1E293B', 'primaryTextColor': '#F8FAFC', 'primaryBorderColor': '#38BDF8', 'lineColor': '#38BDF8', 'secondaryColor': '#0F172A', 'tertiaryColor': '#1E1B4B' }}}%%
flowchart TD

    %% Stage 1: Operational Sources
    subgraph STAGE1["<b>1. MULTI-SOURCE OPERATIONAL INGESTION</b>"]
        direction TB
        S1["<b>PostgreSQL Operational DB</b><br/>• customers.csv (25.2k)<br/>• orders.csv (502k)<br/>• products.csv (20)<br/>• stores.csv (35)"]
        S2["<b>Supply Chain ERP (CSV)</b><br/>• inventory_monthly.csv (8.4k)"]
        S3["<b>Commercial Excel</b><br/>• commercial_reference_data.xlsx<br/>(Targets & Campaigns)"]
        S4["<b>Central Bank API (JSON)</b><br/>• exchange_rates.json (730 FX)"]
    end

    %% Stage 2: Bronze Lossless
    subgraph STAGE2["<b>2. BRONZE LAYER (SQL SERVER 2022)</b>"]
        direction TB
        B1["<b>Lossless Raw Staging</b><br/>• All source types preserved as raw strings<br/>• Lineage: source_file, batch_id, ingestion_timestamp<br/>• Deterministic SHA-256 row_hash fingerprinting"]
    end

    %% Stage 3: Staging & Standardization
    subgraph STAGE3["<b>3. STAGING & STANDARDIZATION ENGINE</b>"]
        direction TB
        STG1["<b>staging.usp_load_staging</b><br/>• Phone Standardization (+20 10... ➔ 010...)<br/>• Governorate Capitalization & Arabic Normalization<br/>• Currency Canonicalization (جنيه, EGP ➔ EGP)<br/>• Status Normalization (مكتمل ➔ Completed)<br/>• Surrogate DateKey Generation (YYYYMMDD)"]
    end

    %% Stage 4: Data Quality & Quarantine
    subgraph STAGE4["<b>4. DATA QUALITY SENTINEL & QUARANTINE</b>"]
        direction TB
        DQ_ENGINE{"<b>dq.usp_run_dq_checks</b><br/>16+ Automated Rules"}
        QUARANTINE["<b>Quarantine Tables (dq.rejected_*)</b><br/>• rejected_orders (4,124)<br/>• rejected_customers (400)<br/>• rejected_inventory (100)<br/>• rejected_targets (4)<br/><i>Zero dirty rows pass into warehouse!</i>"]
        AUDIT["<b>Audit & Observability</b><br/>• dq.data_quality_results<br/>• Pass rate %, failure logs, alerts"]
    end

    %% Stage 5: Kimball Galaxy Warehouse
    subgraph STAGE5["<b>5. KIMBALL GALAXY DATA WAREHOUSE & SNOWFLAKE HIERARCHIES</b>"]
        direction TB
        subgraph SNOWFLAKE["Snowflake Hierarchies"]
            DIM_GEO["<b>dim_geography</b><br/>Governorates ➔ 5 Economic Regions<br/>3 Market Tiers ➔ Courier SLAs"]
            DIM_CAT["<b>dim_category & dim_subcategory</b><br/>Strategic Margin Classes ➔ Form Types"]
        end
        subgraph CONFORMED["Conformed Core Dimensions"]
            DIM_D["<b>dim_date</b> (Calendar, Fri/Sat Weekends)"]
            DIM_C["<b>dim_customer</b> (SCD Type 2 + Carrier & Age Cohort)"]
            DIM_P["<b>dim_product</b> (Egyptian Price Tiers & Domestic Origin)"]
            DIM_S["<b>dim_store</b> (Retail Footprint & Regional Hubs)"]
            DIM_CMP["<b>dim_campaign</b> | <b>dim_channel</b> | <b>dim_payment_method</b>"]
        end
        subgraph FACTS["Galaxy Multi-Process Facts"]
            FACT_S["<b>fact_sales</b> (497,876 Rows)<br/>Grain: 1 Order Line-Item"]
            FACT_I["<b>fact_inventory</b> (8,300 Rows)<br/>Grain: Monthly Snapshot per Store/SKU"]
            FACT_T["<b>fact_store_targets</b> (413 Rows)<br/>Grain: Store Monthly Quota"]
        end
    end

    %% Stage 6: Curated Marts
    subgraph STAGE6["<b>6. CURATED ANALYTICS MARTS</b>"]
        direction TB
        M1["mart_daily_sales (271.6k)"]
        M2["mart_monthly_sales (425)"]
        M3["mart_product_performance (20)"]
        M4["mart_rfm (Customer Segments)"]
        M5["mart_inventory_health (8.3k)"]
        M6["mart_campaign_performance (8)"]
        M7["v_pipeline_health (SLA Audit)"]
    end

    %% Stage 7: Power BI Consumption
    subgraph STAGE7["<b>7. POWER BI ENTERPRISE SEMANTIC MODEL (.PBIP)</b>"]
        direction TB
        PBI_IN_ENGINE["<b>In-Engine M Data Lifecycle (Optional Direct Stream)</b><br/>00_Params ➔ 01_Source ➔ 02_Staging ➔ 03_Reference ➔ 04_Cleansed ➔ 05_Validated ➔ 06_Trf ➔ 07_Model"]
        PBI_MODEL["<b>Tabular Star / Galaxy Model</b><br/>• Strictly 1:Many Single-Direction Relationships<br/>• _Measures Table: 33+ Financial, Volume, Target, RFM, & Time Intelligence DAX KPIs"]
        PBI_REPORTS["<b>Executive Reporting Suite (5 Pages)</b><br/>Executive Overview | Sales & Regional | Inventory Health | Customer RFM | DQ Sentinel"]
    end

    %% Data Flow Connectors
    S1 & S2 & S3 & S4 ==> STAGE2
    STAGE2 ==> STAGE3
    STAGE3 ==> DQ_ENGINE
    DQ_ENGINE -->|Failed Assertions| QUARANTINE
    DQ_ENGINE -->|Logging| AUDIT
    DQ_ENGINE ==>|Validated Clean Data| STAGE5
    DIM_GEO --> DIM_S & DIM_C
    DIM_CAT --> DIM_P
    CONFORMED ==> FACTS
    FACTS ==> STAGE6
    STAGE6 ==> STAGE7
    STAGE5 -.->|Direct Import / Direct Lake| PBI_MODEL

    %% Styling Classes
    classDef sourceStyle fill:#1E293B,stroke:#0284C7,stroke-width:2px,color:#F8FAFC;
    classDef bronzeStyle fill:#0F172A,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC;
    classDef stagingStyle fill:#1E1B4B,stroke:#818CF8,stroke-width:2px,color:#F8FAFC;
    classDef dqStyle fill:#311018,stroke:#F43F5E,stroke-width:2px,color:#FFE4E6;
    classDef whStyle fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5;
    classDef martStyle fill:#14532D,stroke:#34D399,stroke-width:2px,color:#F0FDF4;
    classDef pbiStyle fill:#4C1D95,stroke:#C084FC,stroke-width:2px,color:#FAF5FF;

    class S1,S2,S3,S4 sourceStyle;
    class B1 bronzeStyle;
    class STG1 stagingStyle;
    class DQ_ENGINE,QUARANTINE,AUDIT dqStyle;
    class DIM_GEO,DIM_CAT,DIM_D,DIM_C,DIM_P,DIM_S,DIM_CMP,FACT_S,FACT_I,FACT_T whStyle;
    class M1,M2,M3,M4,M5,M6,M7 martStyle;
    class PBI_IN_ENGINE,PBI_MODEL,PBI_REPORTS pbiStyle;
```

---

## 2. Excalidraw-Style Hand-Drawn Schematic Visual

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               CLEOPATRA MODERN COSMETICS — DATA PLATFORM LIFECYCLE                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 [1. OPERATIONAL SOURCES]
 ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
 │ PostgreSQL Store DB  │  │   Supply Chain ERP   │  │   Commercial Excel   │  │   Central Bank API   │
 │ • customers.csv      │  │ • inventory_monthly  │  │ • Targets sheet      │  │ • exchange_rates     │
 │ • orders.csv         │  │   (8,400 monthly rows│  │ • Campaigns sheet    │  │   (730 daily FX rates│
 │ • products.csv       │  │    balance snapshot) │  │   (Commercial quotas)│  │    USD/EUR to EGP)   │
 └──────────┬───────────┘  └──────────┬───────────┘  └──────────┬───────────┘  └──────────┬───────────┘
            │                         │                         │                         │
            ▼                         ▼                         ▼                         ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ [2. BRONZE LOSSLESS STORAGE] (SQL Server 2022 / Fabric OneLake)                                    │
 │ • Exact raw string mirror • Audit metadata (source_file, ingestion_time, batch_id, SHA-256 hash)   │
 └─────────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                   │
                                                   ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ [3. STAGING & STANDARDIZATION]                                                                     │
 │ • Phone Cleanup: '+20 10...' ➔ '010...' (11-digit local)    • Text Trim & Non-Printable Clean      │
 │ • Governorate Mapping: 'cairo' ➔ 'Cairo'                    • Currency Coercion: 'جنيه' ➔ 'EGP'    │
 │ • Status Normalization: 'مكتمل' ➔ 'Completed'               • Surrogate Date Keys (YYYYMMDD)       │
 └─────────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                   │
                                                   ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ [4. DATA QUALITY GATEWAY & AUTOMATED QUARANTINE]                                                   │
 │ • 16+ Assertions: NotNull, Unique, Referential Integrity, Math Equation, Positive Quantities       │
 └──────────────────────┬──────────────────────────────────────────────────────┬──────────────────────┘
                        │ (Violations Detected)                                │ (Passed 100% Clean)
                        ▼                                                      ▼
 ┌──────────────────────────────────────────────┐       ┌─────────────────────────────────────────────┐
 │ QUARANTINE TABLES (Never Lost / Never Dropped│       │ [5. KIMBALL GALAXY DATA WAREHOUSE]          │
 │ • dq.rejected_orders      : 4,124 rows       │       │ ┌─────────────────────────────────────────┐ │
 │ • dq.rejected_customers   :   400 rows       │       │ │ SNOWFLAKE HIERARCHIES:                  │ │
 │ • dq.rejected_inventory   :   100 rows       │       │ │ • dim_geography (5 Regions, 3 Tiers)    │ │
 │ • dq.rejected_targets     :     4 rows       │       │ │ • dim_category & dim_subcategory        │ │
 │ Ledger: dq.data_quality_results              │       │ └────────────────────┬────────────────────┘ │
 └──────────────────────────────────────────────┘                              │                      │
                                                                               ▼                      │
                                                        ┌───────────────────────────────────────────┐ │
                                                        │ CONFORMED CORE DIMENSIONS:                │ │
                                                        │ • dim_date     (Calendar, Fri/Sat Weekend)│ │
                                                        │ • dim_customer (SCD Type 2 + Telecom/Age) │ │
                                                        │ • dim_product  (Price Tiers + Domestic)   │ │
                                                        │ • dim_store    (Footprint Class + Hubs)   │ │
                                                        │ • dim_campaign | dim_channel | dim_payment│ │
                                                        └──────────────────────┬────────────────────┘ │
                                                                               │                      │
                                                                               ▼                      │
                                                        ┌───────────────────────────────────────────┐ │
                                                        │ MULTI-GRAIN GALAXY FACT CONSTELLATION:    │ │
                                                        │ • fact_sales     (497,876 line items)     │ │
                                                        │ • fact_inventory (8,300 monthly balances) │ │
                                                        │ • fact_store_targets (413 store quotas)   │ │
                                                        └──────────────────────┬────────────────────┘ │
                                                        └──────────────────────┼──────────────────────┘
                                                                               │
                                                                               ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ [6. CURATED BUSINESS ANALYTICS MARTS]                                                              │
 │ • mart_daily_sales (271.6k)    • mart_monthly_sales (425)       • mart_product_performance (20)    │
 │ • mart_rfm (Customer Segments) • mart_inventory_health (8.3k)   • mart_campaign_performance (8)    │
 └─────────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                   │
                                                   ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ [7. POWER BI ENTERPRISE SEMANTIC MODEL & EXECUTIVE DASHBOARD]                                      │
 │ • Power BI Project (.pbip) Tabular Semantic Model with TMDL definitions                            │
 │ • Dedicated _Measures Table: 33+ Production DAX Measures (Gross Margin %, YTD, AOV, RFM, Stockouts)│
 │ • 5 Executive Visual Reports: Executive Summary | Regional Sales | Inventory | RFM | DQ Audit      │
 └────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Interactive Excalidraw Board File

An editable, importable Excalidraw board file is provided in this repository at:
📂 [project_lifecycle.excalidraw](file:///d:/courses/Data%20Science/Data%20Engineering/Projects/egyptian_cosmetics_market/docs/diagrams/project_lifecycle.excalidraw)

### How to use the Excalidraw Board:
1. Open [https://excalidraw.com](https://excalidraw.com) in any web browser.
2. Click the hamburger menu (☰) in the top-left corner $\rightarrow$ **Open**.
3. Select `docs/diagrams/project_lifecycle.excalidraw`.
4. The complete, fully-editable architecture diagram will instantly render with customizable cards, colored containers, connectors, and typography!
