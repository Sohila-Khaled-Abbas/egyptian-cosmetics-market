# Playbook 08: Merge & Append Architecture in Power Query

## 1. Objective & Scope

In Analytics Engineering, knowing **when to join tables in Power Query (M)** versus **when to maintain separate tables in the Star Schema (Data Model)** is a defining characteristic of senior architecture. 

This playbook details:
1. Architectural decision framework: **Power Query Join vs Star Schema Relationship**.
2. Concrete implementations of:
   - **Merge Queries & Expand**: Enriching transactional orders with standard product costs for line-item COGS.
   - **Group By**: Duplicate order and customer detection, inventory monthly aggregation.
   - **Unpivot**: Transforming wide commercial excel projections into normalized analytical schemas.
   - **Append Queries**: Combining partitioned operational batches.
3. Common pitfalls: nested loop join performance traps, cartesian row explosions, and column projection leaks.

---

## 2. Decision Framework: Power Query Merge vs Tabular Model Relationship

| Scenario | Recommended Strategy | Architectural Rationale |
| :--- | :--- | :--- |
| **Line-Item Financial Calculation** (e.g. looking up `standard_cost` to compute `Cost = Qty * Cost`) | **Power Query Merge & Expand** | Must be evaluated at the transaction grain before loading into VertiPaq. Merging in M allows pre-materializing `cost_egp` and `gross_profit_egp`, enabling ultra-fast VertiPaq column scans. |
| **Reference / Lookup Code Translation** (e.g. mapping `RawStatus` $\rightarrow$ `NormalizedStatus`) | **Power Query Merge (or buffered Record lookup)** | Denormalizing code translations during ETL prevents cluttering the data model with dozens of tiny 2-column reference tables. |
| **Analytical Dimension Filtering** (e.g. slicing Sales by Product Category, Customer Governorate, Campaign) | **Star Schema Relationship ($1:\text{Many}$)** | Slicing and dicing belongs in the tabular engine. Denormalizing full customer and product attributes directly into `FactSales` (500,000 rows) would cause massive memory bloat and destroy VertiPaq compression. |
| **Combining Disparate Monthly Sheets or Partition Files** | **Power Query Append (`Table.Combine`)** | Appending unifies identical schema partitions into a single fact table prior to loading. |

---

## 3. Step-by-Step Implementation of Core Joins

### 3.1: Enriching Orders with Product Cost via Merge (New Query Guide)
To calculate line-item Cost of Goods Sold ($\text{COGS} = \text{Quantity} \times \text{StandardCost}$), we execute a Left Outer Join between `vld_orders` and `cln_products`. 

Executing **Merge Queries as New** generates an independent, dedicated transformation query without modifying the upstream `vld_orders` table.

---

#### 🖱️ Step-by-Step GUI Implementation

##### 1. Execute Merge Queries as New
1. In the left **Queries** pane, click to select **`vld_orders`** (under group `05_Validated`).
2. On the top ribbon, stay on the **Home** tab $\rightarrow$ click the small dropdown arrow next to **Merge Queries** $\rightarrow$ select **Merge Queries as New**.
3. In the **Merge** dialog window:
   - **First Table (Top)**: `vld_orders` is pre-selected. Click the header of column **`product_id`** (it will highlight in green/gray).
   - **Second Table (Dropdown)**: Select table **`cln_products`**.
   - In the `cln_products` preview, click the header of column **`product_id`**.
   - **Join Kind**: Choose **Left Outer (all from first, matching from second)**.
   - Look at the bottom validation message: It will confirm *"The selection matches 499,903 of 499,903 rows from the first table."*
4. Click **OK**.
5. Power Query automatically generates a brand-new query in the Queries pane with the temporary default name **`Merge1`**.

---

##### 2. Non-Conflicting Naming Strategy
To prevent naming collisions and keep data lineage crystal clear, choose the appropriate name based on your current project state:

| Project State | Recommended Query Name | Architectural Purpose |
| :--- | :--- | :--- |
| **Path A: Building Primary Transformation Fact** (You do not have `trf_sales` yet) | **`trf_sales`** | This merge acts as the canonical foundation for all downstream sales financials (`calc_gross_sales_egp`, `calc_net_sales_egp`, `calc_cogs_egp`, `calc_gross_profit_egp`). |
| **Path B: Dedicated Standalone Merge Query** (You already created `trf_sales` in Playbook 07) | **`mrg_orders_products`** *(or `trf_orders_enriched`)* | Adheres to the enterprise 3-letter prefix convention (`mrg_` = Merged Transformation Entity). Guarantees **zero collision** with `vld_orders`, `trf_sales`, or `fact_sales`. |

**How to Rename in Power Query GUI:**
1. In the right-hand **Query Settings** pane, locate the **PROPERTIES** section at the top.
2. Click inside the **Name** input box, delete `Merge1`, and type **`mrg_orders_products`** (or **`trf_sales`** if building the primary pipeline).
3. Press **Enter** on your keyboard to commit the new name.
*(Alternatively, right-click `Merge1` in the left Queries list $\rightarrow$ select **Rename**).*

---

##### 3. Governance & Query Settings Configuration
By default, Power Query creates new queries in the root folder with model loading enabled. You must configure its governance immediately:

1. **Move to Folder Group**:
   - Right-click the newly renamed query (`mrg_orders_products` or `trf_sales`) $\rightarrow$ select **Move to Group** $\rightarrow$ choose **`06_Transformations`**.
2. **Disable Model Loading**:
   - Right-click the query $\rightarrow$ click **Enable Load** to **UNCHECK** it.
   - The query name in the Queries pane will immediately switch to *italics*.
   > [!IMPORTANT]
   > **Why Disable Load?**
   > Queries in `06_Transformations` serve strictly as intermediate data pipeline steps. Leaving "Enable Load" checked would cause Power BI's VertiPaq tabular engine to load an extra 500,000 duplicate order rows into RAM, doubling memory consumption and creating schema ambiguity with `fact_sales`.
3. **Keep Report Refresh Enabled**:
   - Right-click the query $\rightarrow$ verify **Include in report refresh** remains **CHECKED** so that scheduled refreshes cascade smoothly.

---

##### 4. Expand Joined Column (`standard_cost_egp`)
1. In the data preview window, scroll all the way to the rightmost column (named `cln_products`).
2. Click the **Expand** icon (two opposing arrows) in the column header.
3. In the popup menu:
   - **Uncheck** *(Select All Columns)*.
   - Check **only** `standard_cost_egp`.
   - **Uncheck** *Use original column name as prefix*.
4. Click **OK**.
5. Double-click the header of the newly expanded column $\rightarrow$ rename it to **`product_standard_cost_egp`**.
6. Click the data type icon next to the column header $\rightarrow$ select **Decimal Number** (`1.2`).

---

#### 💻 Full Generated M Expression (New Query)
If you inspect the **Advanced Editor** for this new query, the clean, self-contained M code will look as follows:

```powerquery
let
    // Step 1: Execute Left Outer Join between validated orders and cleansed products
    Source = Table.NestedJoin(
        vld_orders, {"product_id"}, 
        cln_products, {"product_id"}, 
        "cln_products", 
        JoinKind.LeftOuter
    ),
    // Step 2: Expand standard_cost_egp without table prefix
    #"Expanded cln_products" = Table.ExpandTableColumn(
        Source, 
        "cln_products", 
        {"standard_cost_egp"}, 
        {"product_standard_cost_egp"}
    ),
    // Step 3: Explicitly set data type to Decimal Number (1.2)
    #"Changed Type" = Table.TransformColumnTypes(
        #"Expanded cln_products", 
        {{"product_standard_cost_egp", type number}}
    )
in
    #"Changed Type"
```

---

### 3.2: Aggregations Using `Group By` (New Query Guide)
In our pipeline, `Table.Group` is utilized strategically for:
1. **Duplicate Detection in DQ:** Counting occurrences of `order_id` or `customer_id` to flag duplicates.
2. **Inventory Balancing:** Summing monthly movements across store-product combinations.

> [!WARNING]
> **Why Create as a New Query via Reference?**
> In Power Query, clicking **Group By** directly on a table collapses and removes all un-grouped columns from that table. To protect the integrity of your detailed operational table (`cln_orders`) while building a dedicated aggregation or DQ audit table, always **Reference** the base query first.

---

#### 🖱️ Step-by-Step GUI Implementation

##### 1. Create New Query via Reference
1. In the left **Queries** pane, right-click **`cln_orders`** (under group `04_Cleansed`).
2. Select **Reference**.
3. Power Query creates a new query linked to `cln_orders`, with a default name like `cln_orders (2)`.

---

##### 2. Non-Conflicting Naming Strategy

| Use Case | Recommended Query Name | Architectural Purpose |
| :--- | :--- | :--- |
| **Order Duplicate Audit Table** (Flags duplicate transactions) | **`dq_orders_duplicate_audit`** *(or `grp_orders_duplicate_check`)* | Pre-filtered audit query feeding directly into the Page 5 Data Quality Cockpit. Avoids collisions with `vld_orders` or `rejected_orders`. |
| **Customer Order Frequency Summary** (Aggregates lifetime orders) | **`grp_customer_order_counts`** | Aggregated intermediate table used for RFM scoring without altering the raw `cln_customers` grain. |
| **Monthly Inventory Balance Aggregation** | **`grp_inventory_monthly_balance`** | Summarizes stock movements across store-product combinations. |

**How to Rename in GUI:**
1. In the right-hand **Query Settings** pane under **PROPERTIES**, click the **Name** box.
2. Delete `cln_orders (2)` and type **`dq_orders_duplicate_audit`** (or your chosen aggregation name).
3. Press **Enter**.

---

##### 3. Governance & Query Settings Configuration
1. **Move to Folder Group**:
   - Right-click the query $\rightarrow$ **Move to Group** $\rightarrow$ select **`05_Validated`** (for DQ audits) or **`06_Transformations`** (for analytical summaries).
2. **Configure Model Loading**:
   - **For DQ Audit Queries** (e.g. `dq_orders_duplicate_audit`): Keep **Enable Load = CHECKED** if you plan to bind this table to visual tables on Page 5 (Data Quality Cockpit).
   - **For Intermediate Transformations** (e.g. `grp_customer_order_counts`): Right-click $\rightarrow$ **UNCHECK "Enable Load"** (query becomes italicized).

---

##### 4. Configure `Group By` in the GUI
1. Select query **`dq_orders_duplicate_audit`**.
2. On the **Home** ribbon (or **Transform** tab) $\rightarrow$ click **Group By**.
3. In the **Group By** dialog window:
   - Select radio button: **Basic**.
   - Dropdown selector: choose **`order_id`**.
   - *New column name*: type **`OccurrenceCount`**.
   - *Operation*: choose **Count Rows**.
   - Click **OK**.
4. **Filter to Duplicate Keys Only**:
   - Click the filter dropdown arrow in the header of column `OccurrenceCount`.
   - Hover over **Number Filters** $\rightarrow$ select **Greater Than...**.
   - Enter `1` in the value box.
   - Click **OK**.

---

#### 💻 Full Generated M Expression (Group By Query)
```powerquery
let
    // Step 1: Reference cleansed orders base query
    Source = cln_orders,
    // Step 2: Group by order_id and compute row count
    #"Grouped Rows" = Table.Group(
        Source, 
        {"order_id"}, 
        {{"OccurrenceCount", Table.RowCount, Int64.Type}}
    ),
    // Step 3: Filter strictly for duplicated occurrences
    #"Filtered Duplicates" = Table.SelectRows(
        #"Grouped Rows", 
        each [OccurrenceCount] > 1
    )
in
    #"Filtered Duplicates"
```

---

### 3.3: Normalizing Wide Tables Using `Unpivot` (New Query Guide)
Commercial spreadsheets often deliver targets, budgets, or projections as wide matrices where months are individual columns (e.g. `store_id`, `Jan_Target`, `Feb_Target`, `Mar_Target`...). 

To convert this matrix into a normalized, Kimball-compliant tall analytical table without destroying the wide staging view, we execute **Unpivot Other Columns** inside a new referenced query.

> [!NOTE]
> **Schema Note (`store_id` vs `store_name`):**
> In our operational database, `stg_targets` contains only **`store_id`**, `target_month`, `sales_target_egp`, and `order_target`. The descriptive name `store_name` does not exist in the raw targets table; store names are conformed inside **`dim_store`** (from `cln_stores`).
> When selecting the fixed descriptor column to unpivot around, select **`store_id`** (not `store_name`).

---

#### 🖱️ Step-by-Step GUI Implementation

##### 1. Create New Query via Reference
1. In the left **Queries** pane, right-click the staging query (e.g. **`stg_targets`**).
2. Select **Reference**.
3. Power Query creates a new query named `stg_targets (2)`.

---

##### 2. Non-Conflicting Naming Strategy

| Project State | Recommended Query Name | Architectural Rationale |
| :--- | :--- | :--- |
| **Normalized Commercial Targets** | **`trf_targets_unpivoted`** *(or `unp_targets_monthly`)* | Follows the `trf_` prefix for transformed staging or `unp_` for unpivoted matrices. Guarantees **zero collision** with `src_targets`, `stg_targets`, `cln_targets`, `vld_targets`, or `fact_targets`. |

**How to Rename in GUI:**
1. In the right-hand **Query Settings** pane $\rightarrow$ under **PROPERTIES** $\rightarrow$ click inside **Name**.
2. Delete `stg_targets (2)` $\rightarrow$ type **`trf_targets_unpivoted`** $\rightarrow$ press **Enter**.

---

##### 3. Governance & Query Settings Configuration
1. **Move to Folder Group**:
   - Right-click **`trf_targets_unpivoted`** $\rightarrow$ select **Move to Group** $\rightarrow$ choose **`06_Transformations`**.
2. **Disable Model Loading**:
   - Right-click the query $\rightarrow$ click **Enable Load** to **UNCHECK** it (text becomes italicized).
   - Only the final conformed model table (`fact_targets` in `07_Model`) should load into VertiPaq.
3. **Keep Refresh Enabled**:
   - Verify **Include in report refresh** remains **CHECKED**.

---

##### 4. Configure `Unpivot Other Columns` in the GUI
1. In the data preview table, click the header of column **`store_id`** to select it.
   *(If unpivoting multiple metric columns while preserving dates, hold `Ctrl` and select both `store_id` and `target_month`).*
2. On the top ribbon, switch to the **Transform** tab.
3. Click the dropdown arrow next to **Unpivot Columns** $\rightarrow$ select **Unpivot Other Columns**.
   > [!TIP]
   > **Why "Unpivot Other Columns" instead of "Unpivot Only Selected Columns"?**
   > Selecting "Unpivot Other Columns" dynamically accommodates schema growth. When new projection months (e.g. `Oct_Target`, `Nov_Target`) are added to the Excel sheet in future quarters, Power Query will automatically include them without requiring formula edits or throwing schema errors!
4. **Rename and Format Generated Columns**:
   - A new column named `Attribute` contains the unpivoted headers: Double-click header $\rightarrow$ rename to **`MonthName`**.
   - A new column named `Value` contains the numeric values: Double-click header $\rightarrow$ rename to **`target_revenue_egp`**.
   - Click the data type icon on `target_revenue_egp` $\rightarrow$ set to **Decimal Number** (`1.2`).

---

#### 💻 Full Generated M Expression (Unpivot Query)
```powerquery
let
    // Step 1: Reference staging targets
    Source = stg_targets,
    // Step 2: Unpivot all dynamic columns while keeping store_id fixed
    #"Unpivoted Other Columns" = Table.UnpivotOtherColumns(
        Source, 
        {"store_id"}, 
        "MonthName", 
        "target_revenue_egp"
    ),
    // Step 3: Enforce strict data types on normalized attributes
    #"Changed Type" = Table.TransformColumnTypes(
        #"Unpivoted Other Columns", 
        {
            {"MonthName", type text}, 
            {"target_revenue_egp", type number}
        }
    )
in
    #"Changed Type"
```

---

### 3.4: Combining Sources Using `Append Queries as New` (New Query Guide)
When transactional data is partitioned across multiple operational files or batches (e.g. `orders_2024.csv` and `orders_2025.csv`, or `orders_historical` and `orders_current`), we combine them into a single consolidated stream using **Append Queries as New**.

---

#### 🖱️ Step-by-Step GUI Implementation

##### 1. Execute Append Queries as New
1. In the left **Queries** pane, select the first partition query (e.g. **`orders_historical`** or `stg_orders_2024`).
2. On the top ribbon, stay on the **Home** tab $\rightarrow$ click the dropdown arrow next to **Append Queries** $\rightarrow$ select **Append Queries as New**.
3. In the **Append** dialog window:
   - If combining two tables: Select radio button **Two tables**.
     - Primary table: `orders_historical` (pre-selected).
     - Second table dropdown: Select `orders_current`.
   - If combining three or more batches: Select radio button **Three or more tables** $\rightarrow$ add partitions to the right-hand *Tables to append* list.
4. Click **OK**.
5. Power Query automatically generates a brand-new query named **`Append1`**.

---

##### 2. Non-Conflicting Naming Strategy

| Partition Ingestion Level | Recommended Query Name | Architectural Purpose |
| :--- | :--- | :--- |
| **Raw / Staging Union** (Combining partitions before cleaning) | **`stg_orders_combined`** *(or `stg_orders_all`)* | Combines raw partitions into one staging stream for downstream cleansing (`cln_orders`). Zero collision with individual partition names. |
| **Historical & Incremental Append** | **`app_orders_historical_current`** | Follows the standard `app_` (Append) prefix. Avoids collisions with `src_orders` or `vld_orders`. |

**How to Rename in GUI:**
1. In the right-hand **Query Settings** pane under **PROPERTIES** $\rightarrow$ click inside the **Name** box.
2. Delete `Append1` $\rightarrow$ type **`stg_orders_combined`** (or **`app_orders_historical_current`**) $\rightarrow$ press **Enter**.

---

##### 3. Governance & Query Settings Configuration
1. **Move to Folder Group**:
   - Right-click the newly renamed query $\rightarrow$ select **Move to Group** $\rightarrow$ choose **`02_Staging`** (or **`06_Transformations`**).
2. **Disable Load on Individual Partitions (Crucial for Memory)**:
   - In the Queries pane, right-click `orders_historical` $\rightarrow$ **UNCHECK "Enable Load"**.
   - Right-click `orders_current` $\rightarrow$ **UNCHECK "Enable Load"**.
   > [!CAUTION]
   > **Memory Bloat Warning:**
   > If you leave "Enable Load" checked on both the individual partition queries AND the appended query, Power BI will load the exact same rows twice into the VertiPaq engine, doubling file size and memory footprint!
3. **Configure Load on the Appended Query**:
   - If `stg_orders_combined` feeds downstream into `cln_orders`: **UNCHECK "Enable Load"**.
   - Only the final dimension and fact tables in **`07_Model`** (`fact_sales`) should have **Enable Load = Checked**.

---

#### 💻 Full Generated M Expression (Append Query)
```powerquery
let
    // Step 1: Vertically combine multiple table partitions into a single schema
    Source = Table.Combine({orders_historical, orders_current})
in
    Source
```

---

## 4. Performance Optimization for Power Query Merges

> [!CAUTION]
> **Performance Warning: Avoid Cartesian Row Explosion**
> If the right table in a `Table.NestedJoin` contains duplicate join keys, a Left Outer Join will duplicate rows in the left fact table! On a 500,000-row table, this can silently expand your dataset to millions of rows, corrupting financial totals.
> **Rule:** Always apply `Table.Distinct` to dimension keys before joining.

> [!TIP]
> **Performance Optimization: Use `Table.Buffer` on Lookup Dimensions**
> When merging a small dimension (e.g. 20 products or 35 stores) into 500,000 orders, wrap the right table in `Table.Buffer`:
> ```powerquery
> BufferedProducts = Table.Buffer(Table.SelectColumns(cln_products, {"product_id", "standard_cost_egp"})),
> MergedData = Table.NestedJoin(Source, {"product_id"}, BufferedProducts, {"product_id"}, "Prod", JoinKind.LeftOuter)
> ```
> This pins the 20 product rows into local RAM, eliminating repeated re-evaluations for every partition chunk of the 500,000 order rows.
