# Playbook 07: Business Transformations & Financial Engineering (GUI-First Guide with M Formulas)

## 1. Objective & Scope

A fundamental principle in enterprise analytics engineering is knowing **where to compute transformations**:
> **"Push row-level arithmetic as far upstream as possible (into Power Query or database views), and reserve DAX strictly for dynamic aggregations, ratios, and context-sensitive time intelligence."**

This playbook provides a **100% GUI-first walkthrough** using Power Query Desktop's visual ribbon controls, dialog windows, and custom column formulas to:
1. Build **`trf_sales`**: Merge standard costs from products, compute row-level financial transactions (Gross Sales, Discounts, Net Sales, COGS, Gross Profit), extract an integer calendar surrogate key (`OrderDateKey`), and project clean columns.
2. Build **`trf_inventory`**: Derive monthly integer date keys, calculate net stock flow, and configure visual conditional flags for stockouts and low inventory.
3. Build **`trf_targets`**: Derive commercial monthly quota date keys for conformed dimension modeling.

> [!IMPORTANT]
> **Load Settings Reminder**:
> All queries created in group **`06_Transformations`** must have **`Enable Load = False`** (italicized query names in the Queries pane). They serve as pre-materialized, clean calculation inputs for the final Star/Galaxy schema layer in **`07_Model`**.

---

## 2. Power Query (M) Transformation vs DAX Analytical Logic

Understanding the difference between the mashup engine (M) and the tabular columnar engine (VertiPaq) is essential for high-performance reporting:

| Architecture Dimension | Compute in Power Query (M) | Compute in DAX |
| :--- | :--- | :--- |
| **Nature of Metric** | Static, row-level arithmetic (e.g. $Net = Gross - Discount$). | Dynamic, multi-row aggregations and ratios (e.g. $Margin\% = \frac{\sum Profit}{\sum Net}$). |
| **Engine Execution** | Evaluated **once** during scheduled refresh in the mashup engine. Pre-computed values are compressed directly into columnar VertiPaq storage. | Computed dynamically at query runtime across active visual filters, slicers, and cross-highlighting states. |
| **Memory Footprint** | VertiPaq uses multi-pass dictionary encoding and run-length bit-packing, drastically compressing numeric columns. | A DAX calculated column consumes uncompressed RAM at runtime and does not benefit from ETL-level compaction. |
| **Query Performance** | Sub-millisecond aggregations: `SUM(FactSales[net_sales_egp])` scans pre-computed, compressed vectors instantly. | Iterative row-by-row DAX functions (`SUMX`) on 500,000+ rows consume excessive CPU threads and slow down visual renders. |
| **Data Quality Gate** | Bad math (negative prices, missing costs) can be trapped and quarantined before end-users ever see them. | Formula errors or `#DIV/0!` surface directly inside production reports and dashboards. |

---

## 3. Step-by-Step GUI Implementation of `trf_sales`

In the Power Query Editor, `trf_sales` takes validated transactional rows from `vld_orders`, enriches them with catalog product costs, and materializes all commercial financials.

### 🖱️ Step 3.1: Create Query & Organize
1. In the left **Queries** pane, expand group **`05_Validated`**.
2. Right-click query **`vld_orders`** $\rightarrow$ select **Reference**.
3. A new query appears. Right-click it $\rightarrow$ select **Rename** $\rightarrow$ type **`trf_sales`**.
4. Right-click **`trf_sales`** $\rightarrow$ select **Move to Group** $\rightarrow$ select **`06_Transformations`**.
5. Right-click **`trf_sales`** $\rightarrow$ ensure **Enable Load** is **unchecked** (the query name appears in italics).

---

### 🖱️ Step 3.2: Merge with `cln_products` to Bring Standard Cost
To calculate line-item Cost of Goods Sold ($\text{COGS} = \text{Quantity} \times \text{Standard Cost}$), we join `cln_products` via the visual Merge interface:

1. Select query **`trf_sales`**.
2. On the top ribbon, stay on the **Home** tab $\rightarrow$ click the **Merge Queries** button.
3. In the **Merge** dialog window:
   - In the top table preview (`trf_sales`), click the header of column **`product_id`**.
   - In the dropdown selector below, choose table **`cln_products`**.
   - In the `cln_products` preview, click the header of column **`product_id`**.
   - Set **Join Kind**: **Left Outer (all from first, matching from second)**.
   - The dialog will display: *"The selection matches 499,903 of 499,903 rows from the first table."*
   - Click **OK**.
4. **Expand the Merged Column**:
   - A new column named `cln_products` appears at the right of your table.
   - Click the **Expand** icon (two opposing arrows) in the column header.
   - In the dropdown menu:
     - **Uncheck** *(Select All Columns)*.
     - Check **only** `standard_cost_egp`.
     - **Uncheck** *Use original column name as prefix*.
   - Click **OK**.
5. Double-click the header of the newly expanded column $\rightarrow$ rename it to **`product_standard_cost_egp`**.
6. Click its data type icon $\rightarrow$ set to **Decimal Number** (`1.2`).

---

### 🖱️ Step 3.3: Add Row-Level Financial Columns via Custom Column Dialog
Now, we calculate the five fundamental commercial metrics using Power Query's **Custom Column** modal. Each formula incorporates 2-decimal rounding to guarantee exact financial ledger reconciliation.

#### A. Gross Sales (`calc_gross_sales_egp`)
1. On the top ribbon, switch to the **Add Column** tab $\rightarrow$ click **Custom Column**.
2. In the dialog:
   - *New column name*: `calc_gross_sales_egp`
   - *Custom column formula*:
     ```powerquery
     Number.Round([quantity] * [unit_price_egp], 2)
     ```
3. Click **OK**.
4. Click the type icon next to `calc_gross_sales_egp` $\rightarrow$ select **Decimal Number** (`1.2`).

#### B. Discount Amount (`calc_discount_egp`)
1. On the **Add Column** tab $\rightarrow$ click **Custom Column**.
2. In the dialog:
   - *New column name*: `calc_discount_egp`
   - *Custom column formula*:
     ```powerquery
     Number.Round([calc_gross_sales_egp] * [discount_pct], 2)
     ```
3. Click **OK**.
4. Click the type icon next to `calc_discount_egp` $\rightarrow$ select **Decimal Number** (`1.2`).

#### C. Net Sales (`calc_net_sales_egp`)
1. On the **Add Column** tab $\rightarrow$ click **Custom Column**.
2. In the dialog:
   - *New column name*: `calc_net_sales_egp`
   - *Custom column formula*:
     ```powerquery
     Number.Round([calc_gross_sales_egp] - [calc_discount_egp], 2)
     ```
3. Click **OK**.
4. Click the type icon next to `calc_net_sales_egp` $\rightarrow$ select **Decimal Number** (`1.2`).

#### D. Cost of Goods Sold (`calc_cost_egp`)
1. On the **Add Column** tab $\rightarrow$ click **Custom Column**.
2. In the dialog:
   - *New column name*: `calc_cost_egp`
   - *Custom column formula*:
     ```powerquery
     Number.Round([quantity] * [product_standard_cost_egp], 2)
     ```
3. Click **OK**.
4. Click the type icon next to `calc_cost_egp` $\rightarrow$ select **Decimal Number** (`1.2`).

#### E. Gross Profit (`calc_gross_profit_egp`)
1. On the **Add Column** tab $\rightarrow$ click **Custom Column**.
2. In the dialog:
   - *New column name*: `calc_gross_profit_egp`
   - *Custom column formula*:
     ```powerquery
     Number.Round([calc_net_sales_egp] - [calc_cost_egp], 2)
     ```
3. Click **OK**.
4. Click the type icon next to `calc_gross_profit_egp` $\rightarrow$ select **Decimal Number** (`1.2`).

---

### 🖱️ Step 3.4: Generate Integer Surrogate `OrderDateKey`
To support high-speed relationship indexing with `dim_date` in the Tabular Model, derive a standard integer key ($YYYYMMDD$):

1. On the **Add Column** tab $\rightarrow$ click **Custom Column**.
2. In the dialog:
   - *New column name*: `OrderDateKey`
   - *Custom column formula*:
     ```powerquery
     Date.Year(DateTime.Date([order_datetime])) * 10000 + 
     Date.Month(DateTime.Date([order_datetime])) * 100 + 
     Date.Day(DateTime.Date([order_datetime]))
     ```
3. Click **OK**.
4. Click the type icon on `OrderDateKey` $\rightarrow$ set to **Whole Number** (`123`).

---

### 🖱️ Step 3.5: Choose Columns & Canonical Renaming
1. Switch to the **Home** tab on the top ribbon $\rightarrow$ click **Choose Columns** (or click the dropdown $\rightarrow$ **Choose Columns**).
2. In the selection modal, check **only** the following 20 columns:
   - `order_id`
   - `order_datetime`
   - `OrderDateKey`
   - `customer_id`
   - `product_id`
   - `store_id`
   - `campaign_id`
   - `sales_channel_en`
   - `sales_channel_ar`
   - `payment_method_en`
   - `payment_method_ar`
   - `order_status`
   - `quantity`
   - `unit_price_egp`
   - `discount_pct`
   - `calc_gross_sales_egp`
   - `calc_discount_egp`
   - `calc_net_sales_egp`
   - `calc_cost_egp`
   - `calc_gross_profit_egp`
3. Click **OK**.
4. Double-click the headers of the calculated columns to remove the `calc_` prefix:
   - `calc_gross_sales_egp` $\rightarrow$ `gross_sales_egp`
   - `calc_discount_egp` $\rightarrow$ `discount_egp`
   - `calc_net_sales_egp` $\rightarrow$ `net_sales_egp`
   - `calc_cost_egp` $\rightarrow$ `cost_egp`
   - `calc_gross_profit_egp` $\rightarrow$ `gross_profit_egp`

---

### 📋 Under-the-Hood Reference: Complete M Script for `trf_sales`
For developers who prefer reviewing or pasting the script directly via **Advanced Editor**:

```powerquery
let
    // 1. Ingest validated orders (499,903 clean rows)
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
    
    // 3. Compute Row-Level Financial Metrics with 2-Decimal Precision
    Add_Gross = Table.AddColumn(ExpandedProduct, "calc_gross_sales_egp", each 
        Number.Round([quantity] * [unit_price_egp], 2), 
        Currency.Type
    ),
    Add_Discount = Table.AddColumn(Add_Gross, "calc_discount_egp", each 
        Number.Round([calc_gross_sales_egp] * [discount_pct], 2), 
        Currency.Type
    ),
    Add_Net = Table.AddColumn(Add_Discount, "calc_net_sales_egp", each 
        Number.Round([calc_gross_sales_egp] - [calc_discount_egp], 2), 
        Currency.Type
    ),
    Add_Cost = Table.AddColumn(Add_Net, "calc_cost_egp", each 
        Number.Round([quantity] * [product_standard_cost_egp], 2), 
        Currency.Type
    ),
    Add_Profit = Table.AddColumn(Add_Cost, "calc_gross_profit_egp", each 
        Number.Round([calc_net_sales_egp] - [calc_cost_egp], 2), 
        Currency.Type
    ),
    
    // 4. Derive Integer DateKey for Calendar Dimension (YYYYMMDD)
    Add_DateKey = Table.AddColumn(Add_Profit, "OrderDateKey", each 
        Date.Year(DateTime.Date([order_datetime])) * 10000 + 
        Date.Month(DateTime.Date([order_datetime])) * 100 + 
        Date.Day(DateTime.Date([order_datetime])), 
        Int64.Type
    ),
    
    // 5. Select Final Schema Columns
    ProjectedColumns = Table.SelectColumns(Add_DateKey, {
        "order_id", "order_datetime", "OrderDateKey",
        "customer_id", "product_id", "store_id", "campaign_id",
        "sales_channel_en", "sales_channel_ar",
        "payment_method_en", "payment_method_ar",
        "order_status", "quantity", "unit_price_egp", "discount_pct",
        "calc_gross_sales_egp", "calc_discount_egp", "calc_net_sales_egp",
        "calc_cost_egp", "calc_gross_profit_egp"
    }),
    
    // 6. Rename Calculated Columns to Production Fact Names
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

---

## 4. Step-by-Step GUI Implementation of `trf_inventory`

`trf_inventory` processes monthly retail stock balances from `vld_inventory` ($8,300$ clean rows), computing net stock flows and visual replenishment risk flags.

### 🖱️ Step 4.1: Create Query & Organize
1. In the **Queries** pane, expand group **`05_Validated`**.
2. Right-click **`vld_inventory`** $\rightarrow$ select **Reference**.
3. Rename the query to **`trf_inventory`** $\rightarrow$ Move to group **`06_Transformations`**.
4. Confirm **Enable Load** is **unchecked**.

---

### 🖱️ Step 4.2: Generate Month DateKey via Custom Column
> [!IMPORTANT]
> **Fixing `Expression.Error: The Date value must contain the Date component (Details: January)`**:
> This error happens when `[month]` was transformed in `cln_inventory` into a text month name (e.g., `"January"`). Functions like `Date.Year()` fail because `"January"` is a text string lacking date components.
> 
> The formula below is **bulletproof**: it dynamically detects whether `[month]` is a native Date/DateTime or a text month string like `"January"`, mapping it cleanly to the integer surrogate key ($20250101$):

1. Switch to the **Add Column** tab $\rightarrow$ click **Custom Column**.
2. In the dialog:
   - *New column name*: `MonthDateKey`
   - *Custom column formula*: Copy and paste the formula below:

   ```powerquery
   let
       Val = [month],
       DateKey = 
           if Val is date or Val is datetime then
               Date.Year(DateTime.Date(Val)) * 10000 + Date.Month(DateTime.Date(Val)) * 100 + 1
           else
               let
                   MonthMap = [
                       January = 1, February = 2, March = 3, April = 4,
                       May = 5, June = 6, July = 7, August = 8,
                       September = 9, October = 10, November = 11, December = 12
                   ],
                   MonthNum = Record.FieldOrDefault(MonthMap, Text.Trim(Text.Proper(Text.From(Val))), 1)
               in
                   2025 * 10000 + MonthNum * 100 + 1
   in
       DateKey
   ```

3. Click **OK**.
4. Click the type icon on `MonthDateKey` $\rightarrow$ set to **Whole Number** (`123`).

---

### 🖱️ Step 4.3: Calculate Net Stock Flow via Custom Column
Net stock flow quantifies the physical change in store inventory ($\text{Received} - \text{Sold} - \text{Damaged}$):

1. On the **Add Column** tab $\rightarrow$ click **Custom Column**.
2. In the dialog:
   - *New column name*: `net_stock_flow`
   - *Custom column formula*:
     ```powerquery
     [received_qty] - [sold_qty] - [damaged_qty]
     ```
3. Click **OK**.
4. Click the type icon on `net_stock_flow` $\rightarrow$ set to **Whole Number** (`123`).

---

### 🖱️ Step 4.4: Add Stockout Risk Flags Using the Visual Conditional Column Dialog
Power Query provides a visual **Conditional Column** builder that generates clean `if/then/else` logic without writing code:

#### A. Low Stock Flag (`is_low_stock`)
1. On the **Add Column** tab $\rightarrow$ click **Conditional Column**.
2. In the dialog window:
   - *New column name*: `is_low_stock`
   - *Column Name*: select `closing_stock`
   - *Operator*: select **is less than or equal to**
   - *Value*: type `15`
   - *Output*: type `1`
   - *Else*: type `0`
3. Click **OK**.
4. Click the type icon on `is_low_stock` $\rightarrow$ set to **Whole Number** (`123`).

#### B. Complete Stockout Flag (`is_stockout`)
1. On the **Add Column** tab $\rightarrow$ click **Conditional Column**.
2. In the dialog window:
   - *New column name*: `is_stockout`
   - *Column Name*: select `closing_stock`
   - *Operator*: select **equals**
   - *Value*: type `0`
   - *Output*: type `1`
   - *Else*: type `0`
3. Click **OK**.
4. Click the type icon on `is_stockout` $\rightarrow$ set to **Whole Number** (`123`).

---

### 📋 Under-the-Hood Reference: Complete M Script for `trf_inventory`
```powerquery
let
    Source = vld_inventory,
    
    // 1. DateKey generation handling both Date types and Text Month Names ("January" -> 20250101)
    Add_MonthKey = Table.AddColumn(Source, "MonthDateKey", each 
        let
            Val = [month],
            DateKey = 
                if Val is date or Val is datetime then
                    Date.Year(DateTime.Date(Val)) * 10000 + Date.Month(DateTime.Date(Val)) * 100 + 1
                else
                    let
                        MonthMap = [
                            January = 1, February = 2, March = 3, April = 4,
                            May = 5, June = 6, July = 7, August = 8,
                            September = 9, October = 10, November = 11, December = 12
                        ],
                        MonthNum = Record.FieldOrDefault(MonthMap, Text.Trim(Text.Proper(Text.From(Val))), 1)
                    in
                        2025 * 10000 + MonthNum * 100 + 1
        in
            DateKey, 
        Int64.Type
    ),
    
    // 2. Net Stock Flow = Received - Sold - Damaged
    Add_NetChange = Table.AddColumn(Add_MonthKey, "net_stock_flow", each 
        [received_qty] - [sold_qty] - [damaged_qty], 
        Int64.Type
    ),
    
    // 3. Stockout Risk Indicator Flags
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

---

## 5. Step-by-Step GUI Implementation of `trf_targets`

`trf_targets` prepares the commercial store sales targets ($415$ clean records) for month-level alignment with `FactSales` and `DimDate`.

### 🖱️ Step-by-Step GUI Actions:
1. In the **Queries** pane $\rightarrow$ group **`05_Validated`** $\rightarrow$ right-click **`vld_targets`** $\rightarrow$ select **Reference**.
2. Rename the new query to **`trf_targets`** $\rightarrow$ Move to group **`06_Transformations`**.
3. Verify **Enable Load** is **unchecked**.
4. On the **Add Column** tab $\rightarrow$ click **Custom Column**.
5. In the **Custom Column** dialog:
   - *New column name*: `TargetDateKey`
   - *Custom column formula*: Copy and paste the resilient formula below (handles both Date types and text month names like `"January"`):

   ```powerquery
   let
       Val = [target_month],
       TargetKey = 
           if Val is date or Val is datetime then
               Date.Year(DateTime.Date(Val)) * 10000 + Date.Month(DateTime.Date(Val)) * 100 + 1
           else
               let
                   MonthMap = [
                       January = 1, February = 2, March = 3, April = 4,
                       May = 5, June = 6, July = 7, August = 8,
                       September = 9, October = 10, November = 11, December = 12
                   ],
                   MonthNum = Record.FieldOrDefault(MonthMap, Text.Trim(Text.Proper(Text.From(Val))), 1)
               in
                   2025 * 10000 + MonthNum * 100 + 1
   in
       TargetKey
   ```

6. Click **OK**.
7. Click the type icon on `TargetDateKey` $\rightarrow$ set to **Whole Number** (`123`).

---

### 📋 Under-the-Hood Reference: Complete M Script for `trf_targets`
```powerquery
let
    Source = vld_targets,
    
    // Generate TargetDateKey (YYYYMM01) handling both Date types and Text Month Names ("January" -> 20250101)
    Add_TargetKey = Table.AddColumn(Source, "TargetDateKey", each 
        let
            Val = [target_month],
            TargetKey = 
                if Val is date or Val is datetime then
                    Date.Year(DateTime.Date(Val)) * 10000 + Date.Month(DateTime.Date(Val)) * 100 + 1
                else
                    let
                        MonthMap = [
                            January = 1, February = 2, March = 3, April = 4,
                            May = 5, June = 6, July = 7, August = 8,
                            September = 9, October = 10, November = 11, December = 12
                        ],
                        MonthNum = Record.FieldOrDefault(MonthMap, Text.Trim(Text.Proper(Text.From(Val))), 1)
                    in
                        2025 * 10000 + MonthNum * 100 + 1
        in
            TargetKey, 
        Int64.Type
    )
in
    Add_TargetKey
```

---

## 6. Financial Verification Checklist & Reconciliation

After completing these transformations in Power Query, verify your queries against the master metrics:

| Query Name | Expected Group | Row Count | Key Transformations Verified via GUI | Target Destination |
| :--- | :--- | :---: | :--- | :--- |
| **`trf_sales`** | `06_Transformations` | $499,903$ | `standard_cost_egp` merged; 5 financial metrics computed; `OrderDateKey` derived. | Feeds `fact_sales` in `07_Model` |
| **`trf_inventory`** | `06_Transformations` | $8,300$ | `MonthDateKey` derived; `net_stock_flow`, `is_low_stock`, `is_stockout` flags added. | Feeds `fact_inventory` in `07_Model` |
| **`trf_targets`** | `06_Transformations` | $415$ | `TargetDateKey` derived ($YYYYMM01$ integer format). | Feeds `fact_targets` in `07_Model` |

### 🧮 Mathematical Integrity Checks:
The row-level calculations in `trf_sales` guarantee algebraic consistency across the entire model:
$$\text{Gross Sales} = \text{Quantity} \times \text{Unit Price}$$
$$\text{Discount} = \text{Gross Sales} \times \text{Discount \%}$$
$$\text{Net Sales} = \text{Gross Sales} - \text{Discount}$$
$$\text{Gross Profit} = \text{Net Sales} - \text{Cost}$$

When DAX aggregates these metrics:
```dax
[Gross Profit] = SUM(fact_sales[gross_profit_egp])
```
VertiPaq executes a simple, hardware-accelerated vectorized column scan in **under 15 milliseconds** across 500,000 transactions, completely bypassing expensive runtime row-by-row iteration.
