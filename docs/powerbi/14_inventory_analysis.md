# Playbook 14: Inventory Analytics, Stockout Risk & Supply Chain Monitoring

## 1. Objective & Scope

In physical and digital cosmetics retail, inventory health is directly tied to cash flow and customer satisfaction. Stockouts on popular serums or foundations result in permanent lost sales, while excess stock on slow-moving body scrubs ties up working capital.

This playbook details:
1. The inventory movement balancing equation:
   $$\text{Closing Stock} = \text{Opening Stock} + \text{Received Qty} - \text{Sold Qty} - \text{Damaged Qty}$$
2. Power Query anomaly detection for negative inventory and invalid damages.
3. authoring DAX measures for **Stockout Risk**, **Low Stock Alerts**, **Sell-Through Rate %**, and **Damaged Loss Ratio**.
4. Dimensional integration between `FactInventory`, `DimProduct`, `DimStore`, and `DimDate`.

---

## 2. Dimensional Model Integration

`FactInventory` operates at the monthly store-product grain:
- **`MonthDateKey`** $\rightarrow$ Joins to `DimDate[DateKey]` (representing the 1st of each month).
- **`StoreKey`** $\rightarrow$ Joins to `DimStore[StoreKey]` (35 stores across 22 governorates).
- **`ProductKey`** $\rightarrow$ Joins to `DimProduct[ProductKey]` (20 cosmetic products).

*All relationships are $1:\text{Many}$, Single Direction.*

---

## 3. Power Query Inventory Balancing & Anomaly Flags

In Playbook 05 and 07, we established that raw inventory contains $100$ corrupted rows:
- $50$ rows with negative closing stock (`closing_stock < 0`)
- $50$ rows with negative damages (`damaged_qty = -1`)

These are quarantined into `rejected_inventory`, leaving **$8,300$ mathematically balanced records** in `fact_inventory`.

In `trf_inventory`, we added two boolean flag columns:
- `is_stockout`: $1$ if `closing_stock = 0`, else $0$.
- `is_low_stock`: $1$ if `closing_stock > 0` and `closing_stock <= 15`, else $0$.

---

## 4. Complete Inventory DAX Measures

In `_Measures` under display folder **`06 Inventory & Stock`**:

### 1. Stock Movement Base Measures
```dax
Opening Stock = 
SUM(fact_inventory[opening_stock])
```

```dax
Received Qty = 
SUM(fact_inventory[received_qty])
```

```dax
Inventory Sold Qty = 
SUM(fact_inventory[sold_qty])
```

```dax
Damaged Qty = 
SUM(fact_inventory[damaged_qty])
```

```dax
Closing Stock = 
SUM(fact_inventory[closing_stock])
```
*Format:* Integer `#,##0` | *Description:* Total units physically available in inventory.

---

### 2. Stock Valuation Measures (EGP)
```dax
Closing Stock Value EGP = 
SUMX(
    fact_inventory,
    fact_inventory[closing_stock] * RELATED(dim_product[Standard Cost EGP])
)
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Balance sheet monetary value of inventory at standard cost.

```dax
Damaged Stock Loss EGP = 
SUMX(
    fact_inventory,
    fact_inventory[damaged_qty] * RELATED(dim_product[Standard Cost EGP])
)
```
*Format:* Currency `#,##0.00 "EGP"` | *Description:* Financial loss incurred due to broken, expired, or damaged cosmetic goods.

---

### 3. Supply Chain Efficiency & Risk KPIs

#### `[Stockout Risk Count]`
```dax
Stockout Risk Count = 
CALCULATE(
    COUNTROWS(fact_inventory),
    fact_inventory[is_stockout] = 1
) + 0
```
*Format:* Integer `#,##0` | *Description:* Count of store-product combinations where inventory is completely depleted (0 units).

#### `[Low Stock Count]`
```dax
Low Stock Count = 
CALCULATE(
    COUNTROWS(fact_inventory),
    fact_inventory[is_low_stock] = 1
) + 0
```
*Format:* Integer `#,##0` | *Description:* SKUs nearing stockout threshold ($\le 15$ units), requiring immediate warehouse replenishment.

#### `[Sell-Through Rate %]`
```dax
Sell-Through Rate % = 
VAR TotalAvailable = [Opening Stock] + [Received Qty]
RETURN
    DIVIDE([Inventory Sold Qty], TotalAvailable, 0)
```
*Format:* Percentage `0.0%` | *Description:* Percentage of available inventory sold during the month. High sell-through ($> 80\%$) signals strong demand; low sell-through ($< 30\%$) signals overstocking.

#### `[Damage Loss Ratio %]`
```dax
Damage Loss Ratio % = 
DIVIDE([Damaged Qty], [Opening Stock] + [Received Qty], 0)
```
*Format:* Percentage `0.00%` | *Description:* Damaged units as a proportion of total stock handled. High rates indicate shipping or warehouse handling defects.

---

## 5. Report Design & Visual Layout (Page 4: Inventory Analytics)

1. **Card Visuals (Top Banner):**
   - `[Closing Stock]` (Total units)
   - `[Closing Stock Value EGP]` (Total working capital tied up)
   - `[Stockout Risk Count]` (Red callout for urgent replenishment)
   - `[Low Stock Count]` (Orange callout for impending reorders)
   - `[Damage Loss Ratio %]` (Quality benchmark)
2. **Matrix (Store $\times$ Product Inventory Heatmap):**
   - Rows: `DimStore[Store Name EN]` (or `Governorate`)
   - Columns: `DimProduct[Category]` $\rightarrow$ `Product Name EN`
   - Values: `[Closing Stock]`
   - Conditional Formatting: Background color scale (Red for 0 units, Yellow for 1-15 units, Green for $\ge 50$ units).
3. **Bar Chart:** Top 10 Products by Damaged Loss Value (`DimProduct[Product Name EN]` vs `[Damaged Stock Loss EGP]`).
