# Microsoft Fabric Data Factory & Lakehouse Architecture Blueprint

## 1. Executive Summary & Cloud Migration Vision

While the current operational deployment runs on **SQL Server 2022** and **Power BI Desktop**, this blueprint provides the enterprise migration roadmap to **Microsoft Fabric**. Fabric unifies data integration, lakehouse engineering, and business intelligence onto **OneLake**, eliminating silos and enabling **Direct Lake** semantic modeling.

```mermaid
flowchart LR
    subgraph "External Sources"
        PG[(Postgres OLTP)]
        ERP[(ERP Inventory)]
        EXCEL[Commercial Excel]
        API[Forex API]
    end

    subgraph "Microsoft Fabric OneLake"
        subgraph "Bronze Lakehouse (Files)"
            B_FILES[Raw Files / Staging]
        end

        subgraph "Silver Lakehouse (Delta Parquet)"
            S_ORDERS[stg_orders]
            S_CUST[stg_customers]
            S_PROD[stg_products]
            S_INV[stg_inventory]
        end

        subgraph "Gold Lakehouse (Delta Parquet)"
            G_DIM_D[dim_date]
            G_DIM_C[dim_customer - SCD2]
            G_FACT_S[fact_sales]
            G_FACT_I[fact_inventory]
        end
    end

    subgraph "Consumption"
        PBI_DL[Power BI Direct Lake Mode<br/>Zero Refresh / Sub-second DAX]
    end

    PG & ERP & EXCEL & API -->|Fabric Data Factory Copy Pipeline| B_FILES
    B_FILES -->|Fabric PySpark Notebook| S_ORDERS & S_CUST & S_PROD & S_INV
    S_ORDERS & S_CUST & S_PROD & S_INV -->|Delta MERGE (SCD2)| G_DIM_D & G_DIM_C & G_FACT_S & G_FACT_I
    G_DIM_D & G_DIM_C & G_FACT_S & G_FACT_I -->|Direct Lake| PBI_DL
```

---

## 2. Fabric Data Factory Pipeline Design

### 2.1 Copy Activities & Orchestration
1. **Pipeline: `PL_Ingest_Cleopatra_Bronze`**:
   - **Activity 1**: Copy data from PostgreSQL/REST into `Files/bronze/postgres_like/orders.parquet`.
   - **Activity 2**: Copy `commercial_reference_data.xlsx` into OneLake.
   - **Activity 3**: Web activity polling Forex API and writing JSON payload.
2. **Parameters**:
   - `pExecutionDate` (YYYY-MM-DD)
   - `pIsIncremental` (Boolean)

---

## 3. PySpark Delta Lake Transformations

### 3.1 SCD Type 2 Implementation in Fabric PySpark
```python
from delta.tables import DeltaTable
from pyspark.sql.functions import current_timestamp, lit, col

# Reference Silver staging and Gold target
silver_customers = spark.read.table("silver_lakehouse.stg_customers")
gold_dim_customer = DeltaTable.forName(spark, "gold_lakehouse.dim_customer")

# Step 1: Detect changed records
staged_updates = (
    silver_customers.alias("s")
    .join(gold_dim_customer.toDF().alias("t"), "customer_id")
    .where(
        "t.is_current = true AND ("
        "t.governorate <> s.governorate_clean OR "
        "t.area <> s.area OR "
        "t.customer_segment <> s.customer_segment)"
    )
    .select("s.*")
)

# Step 2: Delta Lake MERGE statement to expire and insert new versions
# (Handled natively in Fabric notebooks with ACID transaction guarantees)
```

---

## 4. Direct Lake Mode in Power BI

### Why Direct Lake is Revolutionary:
- **Zero Refresh Latency**: Power BI queries the Delta Parquet files directly in OneLake through the VertiPaq engine without duplicating data or running slow DirectQuery SQL translations.
- **Extreme Scale**: Supports billions of rows with columnar Parquet compression.
- **Unified Governance**: Governed centrally via Microsoft Purview and Fabric workspace roles.
