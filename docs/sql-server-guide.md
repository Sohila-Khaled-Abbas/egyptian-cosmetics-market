# SQL Server Database Architecture & Administration Guide

## 1. Environment Specifications

- **Database Engine**: Microsoft SQL Server 2022 (v16.x)
- **Host Instance**: `localhost`
- **Database Name**: `egyptian_cosmetics_dw`
- **Authentication**: Windows Integrated Authentication (`Trusted_Connection=yes`)
- **ODBC Driver**: `ODBC Driver 18 for SQL Server` (`TrustServerCertificate=yes`)
- **Default Collation**: `Arabic_100_CI_AS` (Arabic 100, Case-Insensitive, Accent-Sensitive)

---

## 2. Automated Database Deployment

### Method 1: Python Automated Setup (Recommended)
The project provides an automated, idempotent setup runner that creates the database, all schemas, tables, indexes, and stored procedures in the correct dependency order:
```bash
python scripts/setup_database.py
```

### Method 2: Command-Line `sqlcmd` Setup
If deploying via command-line utilities:
```bash
sqlcmd -S localhost -E -C -i scripts/setup.sql
```

---

## 3. Database Options & Concurrency Configuration

### 3.1 Snapshot Isolation & RCSI
To eliminate read-write blocking between large analytical ETL batch loads and real-time Power BI report refreshes, Row Versioning is enabled:
```sql
ALTER DATABASE [egyptian_cosmetics_dw] SET ALLOW_SNAPSHOT_ISOLATION ON;
ALTER DATABASE [egyptian_cosmetics_dw] SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE;
```

### 3.2 Arabic & Bilingual Collation
The collation `Arabic_100_CI_AS` provides:
- Case-insensitive search on English attributes (`'Serum'` matches `'serum'`).
- Accurate linguistic sorting of Arabic characters (`أ`, `إ`, `آ`, `ا`, `ي`, `ى`, `ة`, `ه`).
- Full compatibility with Unicode `NVARCHAR` columns.

---

## 4. Stored Procedure Catalog

| Stored Procedure | Schema | Purpose | Execution Frequency |
| :--- | :--- | :--- | :--- |
| `staging.usp_load_staging` | `staging` | Cleanses, standardizes phones, casing, currencies, and dates from Bronze | Every ETL run |
| `dq.usp_run_dq_checks` | `dq` | Evaluates 16+ data quality rules and routes anomalies to `rejected_*` | Every ETL run |
| `warehouse.usp_load_dimensions` | `warehouse` | Populates calendar date dim, unknown members (-1), and executes **SCD Type 2** merge on `dim_customer` | Every ETL run |
| `warehouse.usp_load_facts` | `warehouse` | Populates `fact_sales`, `fact_inventory`, and `fact_store_targets` with surrogate keys, filtering out quarantine | Full / Incremental |

---

## 5. Indexing & Query Tuning Strategy

1. **Foreign Key Indexes**:
   Every dimension reference in `fact_sales` has an explicit non-clustered index (`date_key`, `customer_key`, `product_key`, `store_key`, `channel_key`). This prevents full table scans during star-join queries in Power BI.
2. **SCD2 Customer Lookup Index**:
   A composite non-clustered index on `warehouse.dim_customer(customer_id, is_current)` allows instantaneous point-in-time surrogate key lookups during the 502,000-order fact load.
3. **Staging Indexing**:
   Non-clustered indexes on staging natural keys (`order_id`, `customer_id`, `product_id`, `store_id`) enable sub-second joins during data quality and quarantine validation.
