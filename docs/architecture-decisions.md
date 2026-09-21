# Architecture Decision Records (ADRs)

## ADR-001: Medallion Architecture Coupled with Kimball Dimensional Model

### Status: ACCEPTED
### Context
Operational data arrives in varied formats (Postgres dumps, multi-sheet Excel workbooks, ERP CSVs, REST JSON) with intentional anomalies. The analytics platform must preserve raw history, allow idempotent re-processing, and provide sub-second star-schema query performance for Power BI.

### Decision
Implement a hybrid **Medallion (Bronze $\rightarrow$ Staging) and Kimball Dimensional (Warehouse $\rightarrow$ Marts)** pattern:
- **Bronze**: Lossless staging of raw data with audit lineage (`batch_id`, `row_hash`).
- **Staging**: Typed, standardized intermediate schema where quality rules are evaluated.
- **Warehouse**: Kimball Star Schema with surrogate keys and point-in-time dimensional tracking.
- **Marts**: Curated views exposing business metrics.

### Consequences
- **Positive**: Complete audit traceability; ability to replay history; optimal VertiPaq tabular compression in Power BI.
- **Trade-off**: Requires initial storage duplication across Bronze and Warehouse.

---

## ADR-002: Slowly Changing Dimension Type 2 (SCD2) on `dim_customer`

### Status: ACCEPTED
### Context
Customer demographics (Governorate, Area, Segment) evolve over time. If a VIP customer moves from Cairo to Alexandria, historical sales made while living in Cairo must remain attributed to Cairo for regional sales tax and store performance reporting.

### Decision
Implement SCD Type 2 tracking on `warehouse.dim_customer` using tracking attributes: `governorate`, `area`, `customer_segment`.
- When an attribute changes: expire existing record (`valid_to = @CurrentTimestamp`, `is_current = 0`) and insert new record (`valid_from = @CurrentTimestamp`, `valid_to = NULL`, `is_current = 1`).
- Fact sales joins on `customer_id` + order date between `valid_from` and `valid_to`.

### Consequences
- **Positive**: Perfect historical accuracy for temporal and geographic sales attribution.
- **Trade-off**: Slightly more complex join logic compared to Type 1 overwrite.

---

## ADR-003: Collation Selection: `Arabic_100_CI_AS`

### Status: ACCEPTED
### Context
The Egyptian retail market requires storing both Arabic product/store names and English brand/code names. Standard Latin collations cause collation conflicts, and binary collations make case-insensitive search difficult.

### Decision
Configure the database with `Arabic_100_CI_AS` (Arabic 100, Case-Insensitive, Accent-Sensitive).
All text columns storing localized strings use `NVARCHAR`.

### Consequences
- **Positive**: Arabic linguistic sorting works out-of-the-box; English searches are case-insensitive.
- **Trade-off**: `NVARCHAR` uses 2 bytes per character; mitigated by columnstore and tabular compression.

---

## ADR-004: Adoption of Power BI Project Format (`.pbip`)

### Status: ACCEPTED
### Context
Binary `.pbix` files are black boxes in Git, preventing code reviews, causing binary merge conflicts, and obscuring M/DAX changes.

### Decision
Adopt the Power BI Project format (`Cleopatra_Cosmetics_Report.pbip`) with TMDL (Tabular Model Definition Language).

### Consequences
- **Positive**: Clean Git diffs for DAX measures and Power Query M code; seamless peer review; CI/CD deployment readiness.
- **Trade-off**: Requires Power BI Desktop Developer Mode enabled.

---

## ADR-005: Defensive Path Sanitization in Power Query

### Status: ACCEPTED
### Context
Users configuring Power Query parameters via the GUI sometimes accidentally paste the whole M code declaration (including quotes and `meta [...]`), causing `Expression.Error: Illegal characters in path`.

### Decision
Every source query in `power_query_m/01_source_queries.m` includes defensive string sanitization that automatically strips quotes, `meta [...]`, and trailing slashes.

### Consequences
- **Positive**: Zero broken imports; self-healing parameters across all environments.
- **Trade-off**: Extra M evaluation step (< 1 millisecond).
