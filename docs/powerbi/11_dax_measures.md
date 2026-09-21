# Playbook 11: Enterprise DAX Semantic Layer & Measures Library

## 1. Objective & Scope

In Power BI architecture, **DAX is strictly reserved for analytical calculations, dynamic aggregations, context-sensitive ratios, and time intelligence**.

This playbook details:
1. Creating a dedicated, empty **`_Measures`** table to centralize all analytical metrics.
2. Structuring measures into 7 organized **Display Folders**.
3. Authoring the complete enterprise DAX measures library covering financial KPIs, volumes, customer metrics, inventory indicators, and commercial target achievements.
4. Explaining why DAX measures must replace row-level calculated columns.

---

## 2. How to Create a Dedicated `_Measures` Table

In Power BI Desktop:
1. On the **Home** ribbon, click **Enter data**.
2. In the *Create Table* dialog:
   - Change table name from `Table` to: **`_Measures`** (the leading underscore forces it to the top of the field list alphabetically).
   - Leave `Column1` blank.
   - Click **Load**.
3. In the **Data** pane on the right, right-click `_Measures` $\rightarrow$ select **New measure**.
4. Create your first measure (e.g. `[Net Sales]`).
5. Once a measure is created inside `_Measures`, right-click the empty `Column1` $\rightarrow$ click **Delete from model**.
6. Switch to Model view and back: the `_Measures` table icon will automatically transform into a **Calculator icon**, signifying an official measure container table.

---

## 3. Display Folder Architecture

To ensure usability for self-service report authors, measures are organized into 7 folders:
- `01 Financial KPIs`
- `02 Order & Volume KPIs`
- `03 Customer & AOV`
- `04 Commercial Targets`
- `05 Time Intelligence`
- `06 Inventory & Stock`
- `07 Data Quality & Pipeline Audit`

To assign a measure to a folder:
1. Switch to **Model view**.
2. In the **Data** pane, select one or more measures.
3. In the **Properties** pane, type the folder name into the **Display folder** property box.

---

## 4. The Complete DAX Measures Library

### Folder 01: Financial KPIs

#### 1. `[Gross Sales]`
```dax
Gross Sales = 
SUM(fact_sales[gross_sales_egp])
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Total gross transactional sales before discounts.

#### 2. `[Discount]`
```dax
Discount = 
SUM(fact_sales[discount_egp])
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Total monetary discount given across completed orders.

#### 3. `[Net Sales]`
```dax
Net Sales = 
CALCULATE(
    SUM(fact_sales[net_sales_egp]),
    fact_sales[order_status] = "Completed"
)
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Recognized commercial revenue from completed transactions.

#### 4. `[Cost]`
```dax
Cost = 
CALCULATE(
    SUM(fact_sales[cost_egp]),
    fact_sales[order_status] = "Completed"
)
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Total standard cost of goods sold (COGS) for completed orders.

#### 5. `[Gross Profit]`
```dax
Gross Profit = 
[Net Sales] - [Cost]
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Net recognized sales minus standard product costs.

#### 6. `[Gross Margin %]`
```dax
Gross Margin % = 
DIVIDE([Gross Profit], [Net Sales], 0)
```
*Format:* Percentage `0.0%` | *Description:* Profitability ratio. Uses DIVIDE to protect against zero-division errors.

#### 7. `[Average Selling Price]`
```dax
Average Selling Price = 
DIVIDE([Net Sales], [Units Sold], 0)
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Realized net revenue per physical unit sold.

---

### Folder 02: Order & Volume KPIs

#### 8. `[Orders]`
```dax
Orders = 
DISTINCTCOUNT(fact_sales[order_id])
```
*Format:* Integer `#,##0` | *Description:* Count of distinct order transactions.

#### 9. `[Completed Orders]`
```dax
Completed Orders = 
CALCULATE(
    [Orders],
    fact_sales[order_status] = "Completed"
)
```
*Format:* Integer `#,##0` | *Description:* Count of successfully completed orders.

#### 10. `[Units Sold]`
```dax
Units Sold = 
CALCULATE(
    SUM(fact_sales[quantity]),
    fact_sales[order_status] = "Completed"
)
```
*Format:* Integer `#,##0` | *Description:* Total physical cosmetic units delivered to customers.

#### 11. `[Average Order Value]`
```dax
Average Order Value = 
DIVIDE([Net Sales], [Completed Orders], 0)
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Basket size: net revenue per completed transaction.

#### 12. `[Cancelled Orders]`
```dax
Cancelled Orders = 
CALCULATE([Orders], fact_sales[order_status] = "Cancelled")
```

#### 13. `[Returned Orders]`
```dax
Returned Orders = 
CALCULATE([Orders], fact_sales[order_status] = "Returned")
```

#### 14. `[Return Rate %]`
```dax
Return Rate % = 
DIVIDE([Returned Orders], [Orders], 0)
```
*Format:* Percentage `0.0%`

---

### Folder 03: Customer & AOV

#### 15. `[Customers]`
```dax
Customers = 
DISTINCTCOUNT(fact_sales[CustomerKey])
```
*Format:* Integer `#,##0` | *Description:* Unique active transacting customers in the current filter context.

#### 16. `[Customer Revenue]`
```dax
Customer Revenue = 
DIVIDE([Net Sales], [Customers], 0)
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Average annual/periodic spend per active customer.

#### 17. `[New Customers]`
```dax
New Customers = 
VAR MinDates = 
    ADDCOLUMNS(
        VALUES(dim_customer[CustomerKey]),
        "@FirstPurchase", CALCULATE(MIN(fact_sales[order_datetime]), ALL(dim_date))
    )
VAR CurrentPeriodStart = MIN(dim_date[Date])
VAR CurrentPeriodEnd = MAX(dim_date[Date])
RETURN
    COUNTROWS(
        FILTER(
            MinDates,
            VAR FP = [@FirstPurchase]
            RETURN FP >= CurrentPeriodStart && FP <= CurrentPeriodEnd
        )
    ) + 0
```
*Format:* Integer `#,##0` | *Description:* Customers making their very first transaction in the selected date window.

#### 18. `[Returning Customers]`
```dax
Returning Customers = 
[Customers] - [New Customers]
```
*Format:* Integer `#,##0` | *Description:* Repeat shoppers active in the current filter period.

---

### Folder 04: Commercial Targets & Achievement

#### 19. `[Sales Target]`
```dax
Sales Target = 
SUM(fact_targets[sales_target_egp])
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Budgeted store sales quota.

#### 20. `[Order Target]`
```dax
Order Target = 
SUM(fact_targets[order_target])
```
*Format:* Integer `#,##0`

#### 21. `[Target Achievement %]`
```dax
Target Achievement % = 
DIVIDE([Net Sales], [Sales Target], 0)
```
*Format:* Percentage `0.0%` | *Description:* Commercial quota realization percentage.

#### 22. `[Target Variance]`
```dax
Target Variance = 
[Net Sales] - [Sales Target]
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Net monetary gap above/below commercial quota.

---

### Folder 06: Inventory & Stock

#### 23. `[Opening Stock]`
```dax
Opening Stock = 
SUM(fact_inventory[opening_stock])
```

#### 24. `[Received Qty]`
```dax
Received Qty = 
SUM(fact_inventory[received_qty])
```

#### 25. `[Inventory Sold Qty]`
```dax
Inventory Sold Qty = 
SUM(fact_inventory[sold_qty])
```

#### 26. `[Damaged Qty]`
```dax
Damaged Qty = 
SUM(fact_inventory[damaged_qty])
```

#### 27. `[Closing Stock]`
```dax
Closing Stock = 
SUM(fact_inventory[closing_stock])
```
*Format:* Integer `#,##0` | *Description:* Total month-end units held in warehouse/stores.

#### 28. `[Stockout Risk]`
```dax
Stockout Risk = 
CALCULATE(
    COUNTROWS(fact_inventory),
    fact_inventory[is_stockout] = 1
) + 0
```
*Format:* Integer `#,##0` | *Description:* Count of store-product SKUs completely exhausted (0 units).

#### 29. `[Low Stock Count]`
```dax
Low Stock Count = 
CALCULATE(
    COUNTROWS(fact_inventory),
    fact_inventory[is_low_stock] = 1
) + 0
```
*Format:* Integer `#,##0` | *Description:* SKUs nearing depletion ($\le 15$ units).

---

### Folder 07: Data Quality & Pipeline Audit

#### 30. `[Total Raw Orders Ingested]`
```dax
Total Raw Orders Ingested = 
[Valid Orders] + [Quarantined Orders]
```
*Format:* Integer `#,##0`

#### 31. `[Valid Orders]`
```dax
Valid Orders = 
COUNTROWS(fact_sales)
```
*Format:* Integer `#,##0` | *Value:* $499,903$ rows.

#### 32. `[Quarantined Orders]`
```dax
Quarantined Orders = 
COUNTROWS(rejected_orders)
```
*Format:* Integer `#,##0` | *Value:* $2,097$ rows.

#### 33. `[Data Quality Score %]`
```dax
Data Quality Score % = 
DIVIDE([Valid Orders], [Total Raw Orders Ingested], 0)
```
*Format:* Percentage `0.00%` | *Empirical Value:* $99.58\%$ ($499,903 / 502,000$).

---

## 5. Why Calculated Columns Must Be Avoided for Measures

1. **Static vs Dynamic:** A calculated column like `[Margin %] = fact_sales[gross_profit_egp] / fact_sales[net_sales_egp]` computes at each row. If you average this column in a pivot table, it calculates the **average of margins**, which is a severe mathematical error (it weights a 10 EGP sale identically to a 100,000 EGP sale). A DAX measure evaluates $\frac{\sum Profit}{\sum NetSales}$, producing the mathematically correct weighted gross margin.
2. **RAM Overhead:** Calculated columns persist in RAM across all 500,000 rows. Measures consume zero storage space until executed in visual context.
