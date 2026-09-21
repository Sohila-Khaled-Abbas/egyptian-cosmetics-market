# Operations & Pipeline Engineering Runbook

## 1. Environment & Prerequisites

Before running the pipeline on a local developer workstation or deployment server:
- **Operating System**: Windows 10/11 or Windows Server.
- **Python**: Python 3.10+ (Dependencies installed via `pip install -r requirements.txt`).
- **SQL Server**: SQL Server 2022 instance running on `localhost`.
- **ODBC Driver**: `ODBC Driver 18 for SQL Server` installed.
- **Authentication**: Windows Integrated Auth (User has `sysadmin` or `db_owner` privileges on `localhost`).

---

## 2. Standard Operating Procedures (SOP)

### 2.1 First-Time Database Initialization
To initialize the `egyptian_cosmetics_dw` database, schemas, tables, and procedures:
```bash
python scripts/setup_database.py
```
*Expected duration: < 15 seconds. Verifies all 13 DDL scripts.*

### 2.2 Executing the Full Pipeline (Daily Batch)
To run the complete end-to-end data pipeline:
```bash
python scripts/run_pipeline.py
```
*Pipeline Stages Executed:*
1. **Bronze Ingestion**: Loads raw CSV, Excel, JSON files into `bronze.*`.
2. **Staging Cleansing**: Calls `staging.usp_load_staging`.
3. **Data Quality & Quarantine**: Calls `dq.usp_run_dq_checks` and outputs audit report.
4. **Warehouse Dimensions**: Calls `warehouse.usp_load_dimensions` (applies SCD Type 2).
5. **Warehouse Facts**: Calls `warehouse.usp_load_facts` (excludes quarantined records).
6. **Marts Verification**: Tests all 7 business views in `mart.*`.
7. **Audit Logging**: Finalizes execution record in `audit.pipeline_runs`.

### 2.3 Running Performance Benchmarks
To compare Full Load vs Incremental Load:
```bash
python scripts/benchmark_loads.py
```

### 2.4 Running the Automated Test Suite
To verify code correctness and anomaly detection:
```bash
pytest tests/ -v
```

---

## 3. Incident Triage & Failure Recovery

| Issue / Alert | Root Cause | Remediation Procedure |
| :--- | :--- | :--- |
| **Connection Timeout to SQL Server** | SQL Server service stopped or driver mismatch | Check Windows Services (`MSSQLSERVER`). Verify driver name in `.env` matches `ODBC Driver 18 for SQL Server`. Ensure `TrustServerCertificate=yes`. |
| **High Quarantine Alert (> 1,000 orders)** | Upstream POS/ERP schema change or broken product catalog | Query `dq.rejected_orders` grouped by `rejection_reason`. Notify ERP team if new product IDs were introduced without catalog registration. |
| **Missing Target Records** | Commercial planning Excel sheet missing monthly stores | Check `dq.rejected_targets`. The missing targets are gracefully quarantined without stopping sales reporting. |
| **Lock Timeout during Fact Load** | Long-running analytical query blocking table | Enable Snapshot Isolation (`ALTER DATABASE ... SET READ_COMMITTED_SNAPSHOT ON`). Verify with `sp_who2`. |

---

## 4. Backfill & Historical Reprocessing

To reprocess historical data from a specific date window:
1. Update raw source files or stage target dates in `data/raw/`.
2. Execute the full load pipeline:
   ```bash
   python scripts/run_pipeline.py
   ```
3. Verify SCD2 dimensions remain consistent (historical records preserve `valid_from` and `valid_to`).
