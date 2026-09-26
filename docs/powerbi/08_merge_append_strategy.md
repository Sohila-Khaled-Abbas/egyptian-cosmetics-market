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

### 3.2: Aggregations Using `Group By`
In our pipeline, `Table.Group` is utilized strategically for two operations:
1. **Duplicate Detection in DQ:** Counting occurrences of `order_id` and `customer_id` to flag duplicates.
2. **Inventory Balancing:** Summing monthly movements across store-product combinations.

#### Step-by-Step Group By in M:
```powerquery
// Grouping to find order duplicate keys
OrderCounts = Table.Group(
    cln_orders, 
    {"order_id"}, 
    {{"OccurrenceCount", Table.RowCount, Int64.Type}}
),
DuplicateKeysOnly = Table.SelectRows(OrderCounts, each [OccurrenceCount] > 1)
```

---

### 3.3: Normalizing Wide Tables Using `Unpivot`
Commercial spreadsheets often display months as columns (e.g. `Jan_Target`, `Feb_Target`, `Mar_Target`). If an incoming Excel report uses this format, we normalize it using **Unpivot Columns**:

1. Select the fixed descriptor columns (e.g. `store_id`, `store_name`).
2. On the **Transform** ribbon, click the drop-down arrow next to **Unpivot Columns** $\rightarrow$ select **Unpivot Other Columns**.
3. Rename resulting columns:
   - `Attribute` $\rightarrow$ `MonthName`
   - `Value` $\rightarrow$ `SalesTarget`

#### Corresponding M Expression:
```powerquery
UnpivotedTargets = Table.UnpivotOtherColumns(
    Source, 
    {"store_id", "store_name"}, 
    "MonthName", 
    "SalesTarget"
)
```

---

### 3.4: Combining Sources Using `Append Queries`
When ingesting historical and current transactional data from separate files:
1. On the **Home** ribbon, click the dropdown next to **Append Queries** $\rightarrow$ select **Append Queries as New**.
2. Select **Two tables** (or **Three or more tables**).
3. Select `orders_historical` and `orders_current`.
4. Click **OK**.
5. **Rename & Organize (Collision Prevention)**:
   - Power Query generates default query `Append1`.
   - In **Query Settings** $\rightarrow$ **Name**, rename to **`stg_orders_combined`** (or **`app_orders_all`**).
   - Move to group **`02_Staging`** (or **`06_Transformations`**).
   - Right-click $\rightarrow$ uncheck **Enable Load** if it feeds into downstream cleansing.

#### Corresponding M Expression:
```powerquery
let
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
