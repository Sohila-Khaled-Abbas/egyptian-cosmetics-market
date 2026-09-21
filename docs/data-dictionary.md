# Enterprise Data Dictionary & Technical Schema Specification

This document provides the complete, authoritative field-level data dictionary and technical schema specification for **Cleopatra Modern Cosmetics (كليوباترا كوزماتكس الحديثة)** across all data platform tiers: Operational Raw Sources, Bronze Ingestion, Staging Standardization, Data Quality Quarantine, Kimball Galaxy Warehouse, and Curated Analytics Marts.

---

## 0. Operational Raw Source Datasets

| Dataset Entity | Physical File Path | Format | Row Count | Primary Key | Business Grain | Description |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **Orders** | `data/raw/postgres_like/orders.csv` | CSV | $502,000$ | `order_id` | 1 Order Line-Item | eCommerce and retail store customer transactions. |
| **Customers** | `data/raw/postgres_like/customers.csv` | CSV | $25,200$ | `customer_id` | 1 Customer Entity | Omnichannel registered customer master. |
| **Products** | `data/raw/postgres_like/products.csv` | CSV | $20$ | `product_id` | 1 Master SKU | Commercial cosmetics catalog with bilingual descriptions. |
| **Stores** | `data/raw/postgres_like/stores.csv` | CSV | $35$ | `store_id` | 1 Store Footprint | Retail boutiques, flagships, and regional hubs. |
| **Monthly Inventory** | `data/raw/csv/inventory_monthly.csv` | CSV | $8,400$ | `month` + `store_id` + `product_id` | Monthly Store-SKU Snapshot | Periodic stock movements, damages, and closing balances. |
| **Commercial Targets** | `data/raw/excel/commercial_reference_data.xlsx` (`Targets`) | XLSX | $417$ | `target_month` + `store_id` | Store Monthly Quota | Monthly sales and order volume performance targets. |
| **Marketing Campaigns**| `data/raw/excel/commercial_reference_data.xlsx` (`Campaigns`)| XLSX | $7$ | `campaign_id` | 1 Marketing Campaign | Marketing promotional campaigns and seasonal events. |
| **Exchange Rates** | `data/raw/api/exchange_rates.json` | JSON | $730$ | `date` + `currency` | Daily Currency Quote | Central Bank of Egypt daily closing rates (USD, EUR, GBP to EGP). |

---

## 1. Bronze Raw Ingestion Layer (`bronze.*`)

All bronze tables store raw values as `NVARCHAR(MAX)` with zero type truncation or casting risk. Every table includes mandatory governance and audit metadata columns:

| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :---: | :--- | :--- |
| `_source_file` | NVARCHAR(500) | NO | Physical file path or URI of source payload | `data/raw/postgres_like/orders.csv` |
| `_batch_id` | UNIQUEIDENTIFIER | NO | Ingestion run identifier (UUID-v4) | `A3F9D1E2-5C8B-4A12-8E3D-9B1A4C2E5F70` |
| `_ingested_at` | DATETIME2 | NO | UTC timestamp when row was inserted into Bronze | `2026-09-21 18:30:15.124` |
| `_row_hash` | CHAR(64) | NO | SHA-256 deterministic fingerprint of all raw fields | `4a54c3b1...` |

### Bronze Tables Inventory:
- `bronze.raw_orders` ($502,000$ rows)
- `bronze.raw_customers` ($25,200$ rows)
- `bronze.raw_products` ($20$ rows)
- `bronze.raw_stores` ($35$ rows)
- `bronze.raw_inventory` ($8,400$ rows)
- `bronze.raw_commercial_targets` ($417$ rows)
- `bronze.raw_campaigns` ($7$ rows)
- `bronze.raw_exchange_rates` ($730$ rows)

---

## 2. Staging & Cleansing Layer (`staging.*`)

Populated by stored procedure `staging.usp_load_staging`. Raw strings are cast to explicit database types, text fields are trimmed and cleaned, phone numbers are standardized, and surrogate integer date keys are generated.

### 2.1 `staging.stg_orders` ($502,000$ Rows)
| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :---: | :--- |
| `order_id` | NVARCHAR(50) | NO | Business order number |
| `order_datetime` | DATETIME2 | NO | Transaction timestamp |
| `order_date_key` | INT | NO | Surrogate date key formatted `YYYYMMDD` (e.g. `20240921`) |
| `customer_id` | NVARCHAR(50) | NO | Foreign key reference to customer |
| `product_id` | NVARCHAR(50) | NO | Foreign key reference to product SKU |
| `store_id` | NVARCHAR(50) | NO | Foreign key reference to store |
| `campaign_id` | NVARCHAR(50) | YES | Associated marketing campaign (NULL if organic) |
| `sales_channel_en` | NVARCHAR(50) | NO | Standardized sales channel (`Online`, `Store`, `Mobile App`, `Marketplace`) |
| `payment_method_en`| NVARCHAR(50) | NO | Standardized payment method (`Cash on Delivery`, `Credit Card`, `Fawry`, `Vodafone Cash`) |
| `quantity` | INT | NO | Units purchased |
| `unit_price_egp` | DECIMAL(12,2) | NO | Selling price per unit in EGP |
| `discount_pct` | DECIMAL(5,4) | NO | Promotional discount percentage ($0.0000$ to $1.0000$) |
| `gross_sales_egp`| DECIMAL(12,2) | NO | `quantity * unit_price_egp` |
| `discount_egp` | DECIMAL(12,2) | NO | `gross_sales_egp * discount_pct` |
| `net_sales_egp` | DECIMAL(12,2) | NO | `gross_sales_egp - discount_egp` |
| `cost_egp` | DECIMAL(12,2) | NO | Total line item COGS in EGP |
| `order_status` | NVARCHAR(50) | NO | Standardized status (`Completed`, `Returned`, `Cancelled`) |
| `currency` | NVARCHAR(10) | NO | Canonical currency code (`EGP`) |

### 2.2 `staging.stg_customers` ($25,200$ Rows)
| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :---: | :--- |
| `customer_id` | NVARCHAR(50) | NO | Business customer identity key |
| `customer_name_ar`| NVARCHAR(255)| YES | Normalized Arabic customer name |
| `customer_name_en`| NVARCHAR(255)| YES | Normalized English customer name |
| `gender` | NVARCHAR(20) | YES | Gender classification (`Female`, `Male`) |
| `birth_year` | INT | YES | Customer birth year |
| `phone` | NVARCHAR(50) | YES | Standardized local Egyptian mobile (`010...`, `011...`, `012...`, `015...`) |
| `telecom_carrier` | NVARCHAR(50) | YES | Detected network (`Vodafone`, `Orange`, `Etisalat`, `WE`) |
| `email` | NVARCHAR(255)| YES | Lowercase trimmed email address |
| `governorate` | NVARCHAR(100)| YES | Canonical Egyptian governorate |
| `area` | NVARCHAR(100)| YES | Neighborhood or city district |
| `customer_segment`| NVARCHAR(50)| YES | Segment (`VIP`, `Loyal`, `Standard`, `New`) |
| `signup_date` | DATE | YES | Registration date |

---

## 3. Data Quality Sentinel & Isolated Quarantine Layer (`dq.*`)

Populated by stored procedure `dq.usp_run_dq_checks`. Any record violating business assertions is quarantined immediately to ensure $100\%$ clean analytical warehouse loading.

### 3.1 Data Quality Audit Table (`dq.data_quality_results`)
Tracks execution telemetry for each rule: `check_id`, `rule_name`, `target_table`, `assertion_type`, `records_checked`, `records_failed`, `pass_rate_pct`, `executed_at`.

### 3.2 Isolated Quarantine Tables
Defective rows are routed into dedicated quarantine tables where they remain accessible for root-cause analysis and business remediation:

#### `dq.rejected_orders` ($4,124$ Rows)
- **Orphaned Customer Keys ($2,840$ rows)**: `customer_id` does not exist in customer master.
- **Math Failure / Negative Metrics ($812$ rows)**: `quantity <= 0`, `unit_price_egp <= 0`, or `gross_sales != quantity * unit_price`.
- **Invalid Store Keys ($310$ rows)**: Store identifier does not match active retail locations.
- **Future Transaction Dates ($162$ rows)**: Order timestamp occurs after current system time.

#### `dq.rejected_customers` ($400$ Rows)
- **Malformed Egyptian Phone Numbers ($260$ rows)**: Fails 11-digit regex `^01[0125][0-9]{8}$`.
- **Unmapped Governorates ($95$ rows)**: Geographic name does not map to the 22 official Egyptian governorates.
- **Missing Required Attributes ($45$ rows)**: Null or blank customer names.

#### `dq.rejected_inventory` ($100$ Rows)
- **Negative Closing Balances ($62$ rows)**: Closing stock drops below zero.
- **Stock Balance Equation Violation ($38$ rows)**: `opening_stock + received_qty - sold_qty - damaged_qty != closing_stock`.

#### `dq.rejected_targets` ($4$ Rows)
- **Negative Target Revenue ($4$ rows)**: Sales target set to negative values in commercial Excel workbook.

---

## 4. Kimball Galaxy Data Warehouse Layer (`warehouse.*`)

Loaded by stored procedures `warehouse.usp_load_dimensions` and `warehouse.usp_load_facts`.

### 4.1 Conformed Dimension Tables

#### `warehouse.dim_date` ($730$ Days)
Role-playing calendar dimension covering 2023–2024. Contains Egyptian weekend logic (Friday/Saturday) and commercial promotional season flags (*Ramadan, Eid El-Fitr, Eid El-Adha, White Friday*).

#### `warehouse.dim_customer` ($24,800$ Active Rows — SCD Type 2)
Implements Slowly Changing Dimension Type 2 with surrogate `customer_key`, `customer_id`, `valid_from`, `valid_to`, `is_current`, and `row_hash`. Enriched with Egyptian Telecom carrier network (`Vodafone`, `Orange`, `Etisalat`, `WE`) and demographic cohorts (*Gen Z, Millennial, Gen X*).

#### `warehouse.dim_product` ($20$ SKUs)
Master cosmetics catalog enriched with commercial market tiers (*Mass <150 EGP, Masstige 150–350 EGP, Prestige 350–600 EGP, Luxury >600 EGP*), formulation origin (*Local Egyptian vs European Import*), list prices, and standard COGS.

#### `warehouse.dim_store` ($35$ Stores)
Omnichannel physical footprints (*Flagship, Mall Boutique, High Street*) across 22 governorates with geographic area and distribution hub assignments.

#### `warehouse.dim_currency` ($730$ Records)
Daily closing currency rates and conversion multipliers for USD, EUR, and GBP to EGP.

---

### 4.2 Snowflake Hierarchy Outriggers

#### `warehouse.dim_geography` ($22$ Governorates)
Normalizes geographic entities into 5 economic regions and 3 courier delivery SLA tiers:
- `geography_key` (PK)
- `governorate_en`, `governorate_ar`
- `economic_region_en`, `economic_region_ar` (*Greater Cairo, Alexandria & Delta, Canal Zone, Upper Egypt, Frontier*)
- `market_tier` (*Tier 1 Metropolitan, Tier 2 Urban, Tier 3 Regional*)
- `courier_sla_hours` ($24$, $48$, $72$ Hours)

#### `warehouse.dim_category` & `warehouse.dim_subcategory`
Normalizes cosmetic product categories into strategic formulation margin classes:
- Skincare (High Margin: $65\%$)
- Haircare (Core Volume: $55\%$)
- Fragrance (Luxury: $70\%$)
- Makeup (High Velocity: $50\%$)

---

### 4.3 Galaxy Multi-Process Fact Tables

#### `warehouse.fact_sales` ($497,876$ Rows)
- **Grain**: 1 individual order line item.
- **Keys**: `sales_key` (PK), `order_id` (Degenerate), `date_key`, `customer_key`, `product_key`, `store_key`, `campaign_key`, `channel_key`, `payment_method_key`.
- **Measures**: `quantity`, `unit_price_egp`, `discount_pct`, `gross_sales_egp`, `discount_egp`, `net_sales_egp`, `cost_egp`, `margin_egp`, `margin_pct`.

#### `warehouse.fact_inventory` ($8,300$ Rows)
- **Grain**: Monthly snapshot per store per SKU.
- **Keys**: `inventory_key` (PK), `date_key`, `store_key`, `product_key`.
- **Measures**: `opening_stock`, `received_qty`, `sold_qty`, `damaged_qty`, `closing_stock`, `days_of_inventory`, `damaged_pct`, `stockout_risk_flag`.

#### `warehouse.fact_store_targets` ($413$ Rows)
- **Grain**: Monthly performance quota per retail store.
- **Keys**: `target_key` (PK), `target_date_key`, `store_key`.
- **Measures**: `sales_target_egp`, `order_target`, `target_achievement_pct`.

---

## 5. Curated Analytics Marts Layer (`mart.*`)

| Mart Entity | Table / View | Row Count | Primary Granularity | Key Business Use Case |
| :--- | :--- | :---: | :--- | :--- |
| **Daily Sales** | `mart.mart_daily_sales` | $271,600$ | Date × Store × Channel | Operational sales tracking and daily revenue trends. |
| **Monthly Sales** | `mart.mart_monthly_sales` | $425$ | Month × Store | Executive C-suite quota tracking and MoM growth. |
| **Product Performance** | `mart.mart_product_performance` | $20$ | SKU Master | SKU margin ranking, return rates, and velocity. |
| **Customer RFM** | `mart.mart_customer_retention_rfm`| $24,800$ | Customer Entity | Customer retention segmentation (Champions, At-Risk, Lost). |
| **Inventory Health** | `mart.mart_inventory_health` | $8,300$ | Month × Store × SKU | Stockout risk detection and days of inventory (DOI). |
| **Marketing ROI** | `mart.mart_marketing_roi` | $7$ | Marketing Campaign | Campaign ROAS, promotional uplift, and CAC. |
| **Pipeline Health** | `mart.v_pipeline_health` | Dynamic | Execution Run | ETL SLA compliance, processing duration, and error audit. |
