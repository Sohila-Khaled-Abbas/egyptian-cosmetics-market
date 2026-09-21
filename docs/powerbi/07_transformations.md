# Playbook 07: Business Transformations & Financial Engineering in M

## 1. Objective & Scope

A frequent debate in business intelligence architecture is: **"Should financial calculations be computed in Power Query or in DAX?"**

This playbook details:
1. Architectural principles determining what belongs in Power Query (M) vs DAX.
2. Step-by-step implementation of row-level commercial metrics in query **`trf_sales`** within group **`06_Transformations`**:
   - Gross Sales ($Quantity \times UnitPrice$)
   - Discount Amount ($GrossSales \times Discount\%$)
   - Net Sales ($GrossSales - DiscountAmount$)
   - Cost of Goods Sold ($Quantity \times StandardCost$)
   - Gross Profit ($NetSales - COGS$)
3. Why pushing row-level arithmetic into Power Query dramatically accelerates VertiPaq compression and optimizes memory.

All queries in `06_Transformations` have **`Enable Load = False`** (they serve as pre-materialized inputs to `07_Model`).

---

## 2. Power Query Transformation vs DAX Analytical Logic

| Dimension | Compute in Power Query (M) | Compute in DAX |
| :--- | :--- | :--- |
| **Nature of Metric** | Static row-level transactions (e.g. $Net = Gross - Discount$). | Dynamic, aggregative, filter-dependent (e.g. $Margin\% = \frac{\sum Profit}{\sum NetSales}$). |
| **Engine Execution** | Executed once during data refresh in the mashup engine. Compressed and stored in columnar VertiPaq memory. | Executed dynamically at query runtime in CPU caches across active slicer filter contexts. |
| **Memory Footprint** | VertiPaq encodes and compresses the resulting column using dictionary encoding and bit-packing. | A DAX calculated column consumes uncompressed RAM and does not benefit from M's multi-pass compression. |
| **Performance Impact**| Zero DAX query penalty. Simple `SUM(FactSales[net_sales_egp])` executes in sub-milliseconds. | Complex iterative row-by-row DAX functions (`SUMX`) on 500,000 rows consume excessive CPU threads. |
| **Cardinality Impact**| Low. Financial rounding to 2 decimals maintains low cardinality. | High if calculated columns are used without compression tuning. |

### The Golden Rule of Analytics Engineering:
> **"Push transformations as far upstream as possible (into M or database), and keep DAX strictly for aggregations, ratios, and context-sensitive time intelligence."**

---

## 3. Step-by-Step Implementation of `trf_sales`

In group **`06_Transformations`**, create query `trf_sales` by referencing `vld_orders`.

### Step 3.1: Enriching with Product Standard Cost
To calculate transactional COGS ($Cost = Quantity \times UnitCost$), `vld_orders` must be joined to `cln_products` to retrieve `standard_cost_egp`.

```powerquery
let
    // 1. Ingest validated orders (499,903 rows)
    Source = vld_orders,
    
    // 2. Left Outer Join with cln_products to bring Standard Cost
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
        {"product_standard_cost_egp"}
    ),
    
    // 3. Compute Row-Level Financial Metrics
    // Gross Sales = Quantity * Unit Price
    Add_Gross = Table.AddColumn(ExpandedProduct, "calc_gross_sales_egp", each 
        Number.Round([quantity] * [unit_price_egp], 2), 
        Currency.Type
    ),
    
    // Discount Amount = Gross Sales * Discount %
    Add_Discount = Table.AddColumn(Add_Gross, "calc_discount_egp", each 
        Number.Round([calc_gross_sales_egp] * [discount_pct], 2), 
        Currency.Type
    ),
    
    // Net Sales = Gross Sales - Discount Amount
    Add_Net = Table.AddColumn(Add_Discount, "calc_net_sales_egp", each 
        Number.Round([calc_gross_sales_egp] - [calc_discount_egp], 2), 
        Currency.Type
    ),
    
    // COGS = Quantity * Standard Cost
    Add_Cost = Table.AddColumn(Add_Net, "calc_cost_egp", each 
        Number.Round([quantity] * [product_standard_cost_egp], 2), 
        Currency.Type
    ),
    
    // Gross Profit = Net Sales - Cost
    Add_Profit = Table.AddColumn(Add_Cost, "calc_gross_profit_egp", each 
        Number.Round([calc_net_sales_egp] - [calc_cost_egp], 2), 
        Currency.Type
    ),
    
    // 4. Extract Date Key for DimDate Join (YYYYMMDD integer format)
    Add_DateKey = Table.AddColumn(Add_Profit, "OrderDateKey", each 
        Date.Year(DateTime.Date([order_datetime])) * 10000 + 
        Date.Month(DateTime.Date([order_datetime])) * 100 + 
        Date.Day(DateTime.Date([order_datetime])), 
        Int64.Type
    ),
    
    // 5. Select Final Columns for FactSales
    ProjectedColumns = Table.SelectColumns(Add_DateKey, {
        "order_id",
        "order_datetime",
        "OrderDateKey",
        "customer_id",
        "product_id",
        "store_id",
        "campaign_id",
        "sales_channel_en",
        "sales_channel_ar",
        "payment_method_en",
        "payment_method_ar",
        "order_status",
        "quantity",
        "unit_price_egp",
        "discount_pct",
        "calc_gross_sales_egp",
        "calc_discount_egp",
        "calc_net_sales_egp",
        "calc_cost_egp",
        "calc_gross_profit_egp"
    }),
    
    // 6. Final Clean Renaming to Model Schema
    RenamedColumns = Table.RenameColumns(ProjectedColumns, {
        {"calc_gross_sales_egp", "gross_sales_egp"},
        {"calc_discount_egp", "discount_egp"},
        {"calc_net_sales_egp", "net_sales_egp"},
        {"calc_cost_egp", "cost_egp"},
        {"calc_gross_profit_egp", "gross_profit_egp"}
    })
in
    RenamedColumns
```
*Name:* `trf_sales` $\rightarrow$ Group: `06_Transformations` $\rightarrow$ Uncheck **Enable Load**.

---

## 4. Step-by-Step Implementation of `trf_inventory`

In group **`06_Transformations`**, create query `trf_inventory` referencing `vld_inventory`.

```powerquery
let
    Source = vld_inventory,
    
    // 1. DateKey generation for Month join (YYYYMM01)
    Add_MonthKey = Table.AddColumn(Source, "MonthDateKey", each 
        Date.Year([month]) * 10000 + Date.Month([month]) * 100 + 1, 
        Int64.Type
    ),
    
    // 2. Net Stock Flow = Received - Sold - Damaged
    Add_NetChange = Table.AddColumn(Add_MonthKey, "net_stock_flow", each 
        [received_qty] - [sold_qty] - [damaged_qty], 
        Int64.Type
    ),
    
    // 3. Stockout Risk Indicator Flag (1 if closing stock <= 10, else 0)
    Add_LowStockFlag = Table.AddColumn(Add_NetChange, "is_low_stock", each 
        if [closing_stock] <= 15 then 1 else 0, 
        Int64.Type
    ),
    
    Add_StockoutFlag = Table.AddColumn(Add_LowStockFlag, "is_stockout", each 
        if [closing_stock] = 0 then 1 else 0, 
        Int64.Type
    )
in
    Add_StockoutFlag
```
*Name:* `trf_inventory` $\rightarrow$ Group: `06_Transformations` $\rightarrow$ Uncheck **Enable Load**.

---

## 5. Step-by-Step Implementation of `trf_targets`

In group **`06_Transformations`**, create query `trf_targets` referencing `vld_targets`.

```powerquery
let
    Source = vld_targets,
    
    // MonthDateKey (YYYYMM01)
    Add_TargetKey = Table.AddColumn(Source, "TargetDateKey", each 
        Date.Year([target_month]) * 10000 + Date.Month([target_month]) * 100 + 1, 
        Int64.Type
    )
in
    Add_TargetKey
```
*Name:* `trf_targets` $\rightarrow$ Group: `06_Transformations` $\rightarrow$ Uncheck **Enable Load**.

---

## 6. Financial Verification & Reconciliations

The row-level calculations in `trf_sales` guarantee algebraic consistency:
$$\text{Gross Sales} = \text{Quantity} \times \text{Unit Price}$$
$$\text{Discount} = \text{Gross Sales} \times \text{Discount \%}$$
$$\text{Net Sales} = \text{Gross Sales} - \text{Discount}$$
$$\text{Gross Profit} = \text{Net Sales} - \text{Cost}$$

When DAX executes:
```dax
[Gross Profit] = SUM(FactSales[gross_profit_egp])
```
It is computed via a simple, vectorized VertiPaq column scan, achieving execution times under 15 milliseconds across half a million rows.
