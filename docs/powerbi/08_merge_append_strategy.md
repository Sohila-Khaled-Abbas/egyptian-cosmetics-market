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

### 3.1: Enriching Orders with Product Cost via Merge
To calculate `calc_cost_egp` ($Quantity \times StandardCost$), we execute a Left Outer Join between `vld_orders` and `cln_products`:

1. In Power Query Editor, select `vld_orders`.
2. On **Home** ribbon, click **Merge Queries** $\rightarrow$ **Merge Queries as New** (or within step).
3. Configuration:
   - First Table: `vld_orders`, select column `product_id`.
   - Second Table: `cln_products`, select column `product_id`.
   - Join Kind: **Left Outer (all from first, matching from second)**.
4. Click **OK**.
5. In the newly created table column (`ProductRef`), click the **Expand** icon (two opposing arrows) in the column header.
6. **Uncheck "(Select All Columns)"** $\rightarrow$ Check *only* `standard_cost_egp`.
7. **Uncheck "Use original column name as prefix"**.
8. Click **OK**.

#### Corresponding M Expression:
```powerquery
MergedProduct = Table.NestedJoin(
    Source, {"product_id"}, 
    cln_products, {"product_id"}, 
    "ProductRef", 
    JoinKind.LeftOuter
),
ExpandedProduct = Table.ExpandTableColumn(
    MergedProduct, 
    "ProductRef", 
    {"standard_cost_egp"}, 
    {"standard_cost_egp"}
)
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
1. On **Home** ribbon, click **Append Queries** $\rightarrow$ **Append Queries as New**.
2. Select **Two tables** (or **Three or more tables**).
3. Select `orders_historical` and `orders_current`.
4. Click **OK**.

#### Corresponding M Expression:
```powerquery
CombinedOrders = Table.Combine({orders_historical, orders_current})
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
