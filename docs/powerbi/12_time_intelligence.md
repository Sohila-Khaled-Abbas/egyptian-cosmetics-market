# Playbook 12: Time Intelligence Engineering & Comparative Growth

## 1. Objective & Scope

Time intelligence enables executives to benchmark current business velocity against historical baselines:
- Year-to-Date (YTD), Quarter-to-Date (QTD), Month-to-Date (MTD)
- Year-over-Year (YoY) and Month-over-Month (MoM) growth rates
- Prior Year (PY) and Prior Month (PM) comparisons

This playbook details:
1. Why native DAX time intelligence requires an official, contiguous Date Table (`DimDate`).
2. The architectural difference between **Date Table Filtering** vs **DAX Time-Intelligence Calculations**.
3. Authoring the complete Time Intelligence measure suite in folder **`05 Time Intelligence`**.

---

## 2. Date Table Filtering vs DAX Time Intelligence

| Concept | Date Table Slicing / Filtering | DAX Time Intelligence (`CALCULATE` + Time Modifiers) |
| :--- | :--- | :--- |
| **How It Works** | User selects a month (e.g. `March 2025`) in a slicer. The filter propagates naturally through the $1:\text{Many}$ relationship to `FactSales`, filtering rows where `OrderDateKey` falls in March 2025. | An analytical measure overrides or shifts the natural filter context using functions like `SAMEPERIODLASTYEAR` or `DATESYTD` to retrieve values outside the current slicer window. |
| **Example Expression** | `[Net Sales]` (automatically evaluates for March 2025 when slicer is set to March 2025). | `[Sales PY] = CALCULATE([Net Sales], SAMEPERIODLASTYEAR(dim_date[Date]))` |
| **Prerequisites** | Clean $1:\text{Many}$ relationship between `dim_date[DateKey]` and `fact_sales[OrderDateKey]`. | 1. Table must be marked as Date Table.<br>2. Must contain a column of `type date` with unique, contiguous, unbroken dates.<br>3. Must cover the full date range of facts. |

---

## 3. The 7 Core Time Intelligence Measures

All measures below reside in `_Measures` under display folder **`05 Time Intelligence`**.

### 1. `[Sales YTD]` (Year-to-Date Net Sales)
Accumulates net sales from January 1st of the selected year through the latest visible date.

```dax
Sales YTD = 
TOTALYTD(
    [Net Sales],
    dim_date[Date]
)
```
*Format:* Currency `#,##0.00 "EGP"`

### 2. `[Sales QTD]` (Quarter-to-Date Net Sales)
```dax
Sales QTD = 
TOTALQTD(
    [Net Sales],
    dim_date[Date]
)
```
*Format:* Currency `#,##0.00 "EGP"`

### 3. `[Sales MTD]` (Month-to-Date Net Sales)
```dax
Sales MTD = 
TOTALMTD(
    [Net Sales],
    dim_date[Date]
)
```
*Format:* Currency `#,##0.00 "EGP"`

### 4. `[Sales PY]` (Prior Year Same Period)
Shifts the current date context backwards by exactly one year. Handles leap years and varying month lengths automatically.

```dax
Sales PY = 
CALCULATE(
    [Net Sales],
    SAMEPERIODLASTYEAR(dim_date[Date])
)
```
*Format:* Currency `#,##0.00 "EGP"`

### 5. `[YoY Sales Growth %]` (Year-over-Year Growth Percentage)
```dax
YoY Sales Growth % = 
VAR CurrentSales = [Net Sales]
VAR PriorYearSales = [Sales PY]
RETURN
    IF(
        NOT ISBLANK(CurrentSales) && NOT ISBLANK(PriorYearSales),
        DIVIDE(CurrentSales - PriorYearSales, PriorYearSales, 0),
        BLANK()
    )
```
*Format:* Percentage `+0.0%;-0.0%;0.0%` | *Description:* Returns blank if prior year data is absent to avoid misleading $+100\%$ spikes in reporting.

### 6. `[Sales PM]` (Prior Month Net Sales)
Shifts the current date context backwards by one month.

```dax
Sales PM = 
CALCULATE(
    [Net Sales],
    PREVIOUSMONTH(dim_date[Date])
)
```
*Format:* Currency `#,##0.00 "EGP"`

### 7. `[MoM Sales Growth %]` (Month-over-Month Growth Percentage)
```dax
MoM Sales Growth % = 
VAR CurrentSales = [Net Sales]
VAR PriorMonthSales = [Sales PM]
RETURN
    IF(
        NOT ISBLANK(CurrentSales) && NOT ISBLANK(PriorMonthSales),
        DIVIDE(CurrentSales - PriorMonthSales, PriorMonthSales, 0),
        BLANK()
    )
```
*Format:* Percentage `+0.0%;-0.0%;0.0%`

---

## 4. Advanced: Prior Period Target Benchmarking

Comparing actual sales against prior year sales alongside commercial targets gives executives a complete 3-way variance view:

```dax
Target vs PY Variance % = 
DIVIDE([Sales Target] - [Sales PY], [Sales PY], 0)
```

---

## 5. Common Pitfalls & Troubleshooting

> [!CAUTION]
> **Referencing Fact Date Column in Time Intelligence Functions**
> Never write:
> `TOTALYTD([Net Sales], fact_sales[order_datetime])`  <-- **WRONG!**
> This causes severe performance degradation, skips dates with zero sales, and throws errors if timestamps contain hours/minutes.
> Always reference the date column in the marked date dimension:
> `TOTALYTD([Net Sales], dim_date[Date])`             <-- **CORRECT!**

> [!TIP]
> **Contiguous Date Requirement**
> If your operational sales only occurred from 2025-01-01 to 2025-12-31, `DimDate` must still contain every single day (all 365 days) without gaps. Skipping weekends or holidays breaks DAX time intelligence internal shift algorithms.
