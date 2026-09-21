# Comprehensive Data Dictionary & Schema Specification

## 1. Dimensional Warehouse Layer (`warehouse.*`)

### 1.1 Dimension Tables

#### `warehouse.dim_date` (Calendar Dimension)
| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `date_key` | INT (PK) | NO | Primary key in format YYYYMMDD | `20250517` |
| `full_date` | DATE | NO | Full calendar date | `2025-05-17` |
| `year` | INT | NO | 4-digit calendar year | `2025` |
| `month_number`| INT | NO | Month index (1-12) | `5` |
| `month_name` | NVARCHAR(30) | NO | English month name | `May` |
| `month_short_name`| NVARCHAR(10)| NO | 3-letter month abbreviation | `May` |
| `month_name_ar`| NVARCHAR(30)| NO | Arabic month name | `مايو` |
| `quarter` | NVARCHAR(5) | NO | Calendar quarter | `Q2` |
| `year_month` | NVARCHAR(10) | NO | Formatted year-month string | `2025-05` |
| `year_month_number`| INT | NO | Integer year-month index | `202505` |
| `week_number` | INT | NO | ISO week number (1-53) | `20` |
| `day` | INT | NO | Day of the month (1-31) | `17` |
| `day_name` | NVARCHAR(30) | NO | English day of week | `Saturday` |
| `day_name_ar` | NVARCHAR(30) | NO | Arabic day of week | `السبت` |
| `is_weekend` | BIT | NO | Weekend flag (Friday=1, Saturday=1 in Egypt) | `1` |

---

#### `warehouse.dim_customer` (Slowly Changing Dimension Type 2)
| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `customer_key` | BIGINT (PK) | NO | Surrogate identity key | `1042` |
| `customer_id` | NVARCHAR(50) | NO | Natural business key | `C001248` |
| `customer_name_ar`| NVARCHAR(255)| YES | Arabic customer name | `مريم إبراهيم حسن` |
| `customer_name_en`| NVARCHAR(255)| YES | English customer name | `Mariam Ibrahim Hassan` |
| `gender` | NVARCHAR(20) | YES | Customer gender | `Female` |
| `birth_year` | INT | YES | Year of birth | `1994` |
| `governorate` | NVARCHAR(100)| YES | Normalized Egyptian governorate | `Cairo` |
| `area` | NVARCHAR(100)| YES | City or municipal district | `Nasr City` |
| `phone` | NVARCHAR(50) | YES | Standardized phone (010/011/012/015) | `01023456789` |
| `email` | NVARCHAR(255)| YES | Lowercase standardized email | `mariam.ibrahim@gmail.com` |
| `signup_date` | DATE | YES | Account registration date | `2024-03-15` |
| `customer_segment`| NVARCHAR(50)| YES | Segment (VIP, Standard, Wholesale, New) | `VIP` |
| `valid_from` | DATETIME2 | NO | SCD2 interval effective start | `2025-01-01 00:00:00` |
| `valid_to` | DATETIME2 | YES | SCD2 interval expiration (NULL = current) | `NULL` |
| `is_current` | BIT | NO | Active version flag (1=current, 0=historical) | `1` |
| `row_hash` | CHAR(64) | YES | SHA-256 hash of tracked attributes | `e3b0c442...` |

---

#### `warehouse.dim_product` (Catalog Dimension)
| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `product_key` | INT (PK) | NO | Surrogate identity key | `8` |
| `product_id` | NVARCHAR(50) | NO | Natural business key | `P008` |
| `product_name_en`| NVARCHAR(255)| NO | English commercial name | `Hyaluronic Acid Serum 50ml` |
| `product_name_ar`| NVARCHAR(255)| NO | Arabic commercial name | `سيروم حمض الهيالورونيك 50 مل` |
| `brand_en` | NVARCHAR(100)| YES | English brand name | `Cleopatra Derma` |
| `brand_ar` | NVARCHAR(100)| YES | Arabic brand name | `كليوباترا ديرما` |
| `category` | NVARCHAR(100)| NO | Category (Skincare, Makeup, Haircare, etc.) | `Skincare` |
| `subcategory` | NVARCHAR(100)| NO | Detailed product segment | `Serums` |
| `list_price_egp`| DECIMAL(12,2)| NO | Standard base retail price in EGP | `450.00` |
| `standard_cost_egp`| DECIMAL(12,2)| NO| Manufacturing / import COGS in EGP | `210.00` |
| `currency` | NVARCHAR(10) | YES | Reporting currency | `EGP` |
| `origin` | NVARCHAR(50) | YES | Source origin (Local vs Imported) | `Local` |

---

#### `warehouse.dim_store` (Store Network Dimension)
| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `store_key` | INT (PK) | NO | Surrogate identity key | `14` |
| `store_id` | NVARCHAR(50) | NO | Natural business key | `S014` |
| `store_name_en` | NVARCHAR(255)| NO | English store name | `Mall of Arabia Flagship` |
| `store_name_ar` | NVARCHAR(255)| NO | Arabic store name | `فرع مول العرب الرئيسي` |
| `governorate` | NVARCHAR(100)| NO | Normalized governorate | `Giza` |
| `area` | NVARCHAR(100)| YES | Shopping district or mall | `6th of October` |
| `store_type` | NVARCHAR(50) | YES | Type (Flagship, Mall Store, Kiosk, Pharmacy)| `Flagship` |
| `distribution_region`| NVARCHAR(100)|YES | Regional distribution hub | `Greater Cairo` |

---

### 1.2 Fact Tables

#### `warehouse.fact_sales` (Transactional Fact Table)
- **Grain**: One row per customer order line transaction.
- **Foreign Keys**: `date_key`, `customer_key`, `product_key`, `store_key`, `campaign_key`, `channel_key`, `payment_method_key`.

| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `sales_key` | BIGINT (PK) | NO | Surrogate auto-incrementing key |
| `order_id` | NVARCHAR(50) | NO | Degenerate dimension (order business identifier) |
| `order_datetime`| DATETIME2 | NO | Transaction timestamp |
| `quantity` | INT | NO | Units sold (strictly positive $\ge 1$) |
| `unit_price_egp`| DECIMAL(12,2)| NO | Selling price per unit |
| `discount_pct` | DECIMAL(5,4) | NO | Applied discount percentage ($0.0000 - 1.0000$) |
| `gross_sales_egp`| DECIMAL(12,2)| NO | `quantity * unit_price_egp` |
| `discount_egp` | DECIMAL(12,2)| NO | `gross_sales_egp * discount_pct` |
| `net_sales_egp` | DECIMAL(12,2)| NO | `gross_sales_egp - discount_egp` |
| `cost_egp` | DECIMAL(12,2)| NO | Total line item cost (`quantity * standard_cost_egp`) |
| `profit_egp` | DECIMAL(12,2)| NO | Gross profit (`net_sales_egp - cost_egp`) |
| `margin_pct` | DECIMAL(6,4) | NO | Gross margin percentage (`profit_egp / net_sales_egp`) |
| `order_status` | NVARCHAR(50) | NO | Lifecycle status (`Completed`, `Cancelled`, `Returned`) |

---

#### `warehouse.fact_inventory` (Periodic Monthly Stock Snapshot)
- **Grain**: One row per store + product + month.

| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `inventory_key` | BIGINT (PK) | NO | Surrogate identity key |
| `month_date_key`| INT (FK) | NO | Reference to `dim_date(date_key)` |
| `store_key` | INT (FK) | NO | Reference to `dim_store(store_key)` |
| `product_key` | INT (FK) | NO | Reference to `dim_product(product_key)` |
| `opening_stock` | INT | NO | Stock balance at start of month |
| `received_qty` | INT | NO | New units received from warehouse hub |
| `sold_qty` | INT | NO | Units sold to customers |
| `damaged_qty` | INT | NO | Units damaged / expired / written off |
| `closing_stock` | INT | NO | Stock balance at month end |
| `net_stock_flow`| INT | NO | Net inventory change (`received - sold - damaged`) |
| `is_low_stock` | BIT | NO | Flag: closing stock between 1 and 20 units |
| `is_stockout` | BIT | NO | Flag: closing stock $\le 0$ units |

---

## 2. Curated Business Marts (`mart.*`)

| View Name | Description | Key Metric Columns |
| :--- | :--- | :--- |
| `mart_daily_sales` | Daily sales trends by channel and store | `net_sales_egp`, `gross_profit_egp`, `total_orders`, `total_units_sold` |
| `mart_monthly_sales` | Monthly commercial target tracking & achievement | `sales_target_egp`, `target_variance_egp`, `achievement_pct` |
| `mart_product_performance`| Product velocity, brand margins, and origins | `revenue_share_pct`, `gross_margin_pct`, `total_units_sold` |
| `mart_rfm` | Customer quantile segmentation (Champions to Lost) | `r_score`, `f_score`, `m_score`, `rfm_segment`, `customer_count` |
| `mart_inventory_health` | Stockout risk, shrinkage loss, and stock valuation | `closing_valuation_egp`, `damage_rate_pct`, `stockout_events` |
| `mart_campaign_performance`| Return on marketing spend across platforms | `revenue_generated_egp`, `roas_multiple`, `cost_per_order_egp` |
| `v_pipeline_health` | Observability view linking pipeline runs to DQ checks | `status`, `duration_seconds`, `pass_rate_pct`, `failed_rows` |
