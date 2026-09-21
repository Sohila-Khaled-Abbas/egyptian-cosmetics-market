# Playbook 03: Data Profiling & Empirical Source Assessment

## 1. Objective & Scope

Before applying any cleaning transformations or writing business calculations, an Analytics Engineer must conduct rigorous **Data Profiling**. Profiling exposes dirty data, schema drifts, null rates, cardinality distributions, and integrity anomalies.

This playbook provides:
1. Exact Power BI Data Profiling UI procedures using Power Query's built-in profiling suite.
2. An empirical Source Profiling Catalog containing verified statistics from the raw Egyptian cosmetics dataset.
3. Diagnostic techniques for handling errors (`Keep Errors`, `Remove Errors`, `Replace Errors`).

---

## 2. Power Query Data Profiling Suite: Step-by-Step UI Guide

Power Query Desktop includes enterprise-grade profiling tools on the **View** ribbon.

### Step 2.1: Enable the Profiling Suite
1. In **Power Query Editor**, click the **View** ribbon.
2. In the **Data Preview** group, check all three options:
   - **Column quality**: Displays percentages for **Valid**, **Error**, and **Empty** values directly above each column header.
   - **Column distribution**: Displays a mini-histogram of unique vs. distinct values directly beneath each column header.
   - **Column profile**: Opens a detailed statistical pane at the bottom of the window displaying Min, Max, Average, Standard Deviation, Null Count, Distinct Count, and Value Distribution frequencies.
3. In the lower-left status bar, change the profiling scope:
   - Default setting is: `Column profiling based on top 1000 rows`.
   - Click this text $\rightarrow$ select: **`Column profiling based on entire dataset`**.
   *(Crucial requirement: Profiling only 1,000 rows on a 502,000-row dataset will completely miss rare anomalies such as the 35 broken foreign keys or 2,000 duplicate orders).*

```
+-----------------------------------------------------------------------------------------+
| View Ribbon -> [x] Column quality   [x] Column distribution   [x] Column profile        |
| Bottom Status Bar -> Click "Profiling based on top 1000 rows" -> Select "Entire dataset"|
+-----------------------------------------------------------------------------------------+
```

### Step 2.2: Interpreting Profiling Metrics
- **Valid %**: Percentage of rows where the data conforms to the expected column datatype without parsing exceptions.
- **Error %**: Percentage of rows where evaluation throws an exception (e.g., trying to parse `"N/A"` as an integer).
- **Empty %**: Percentage of rows containing null or empty string `""`.
- **Distinct**: Count of unique values including duplicates (e.g. if the value `"Cairo"` appears 10 times, it counts once).
- **Unique**: Count of values that appear exactly *once* in the entire column. (If `Unique == RowCount`, the column is a candidate Primary Key).

---

## 3. Handling Errors: Keep, Remove, and Replace

When profiling reveals errors in a column, Power Query provides three actions:

### 1. `Keep Errors` (Diagnostic Isolation)
- **UI Action**: Right-click the column header containing errors $\rightarrow$ **Keep Errors**.
- **What it does**: Injects `Table.SelectRowsWithErrors`. Power Query filters the table to show *only* the rows that caused the error.
- **When to use**: **During investigation only.** Never leave `Keep Errors` on a production model table, as it drops all valid business data. Use it in a temporary diagnostic query to inspect the corrupt raw string values.

### 2. `Remove Errors` (Lossy Deletion)
- **UI Action**: Right-click column header $\rightarrow$ **Remove Errors** (`Table.RemoveRowsWithErrors`).
- **What it does**: Deletes any row that contains an evaluation error.
- **When to use**: Highly restricted in enterprise ETL. Silently deleting rows destroys source-to-target reconciliation and obscures systemic upstream bugs. Our architecture routes errors to **Quarantine** instead of deleting them.

### 3. `Replace Errors` (Deterministic Remediation)
- **UI Action**: Right-click column header $\rightarrow$ **Replace Errors...** (`Table.ReplaceErrorValues`).
- **What it does**: Substitutes a fallback value (e.g., `0` for numeric, `"Unknown"` for text, or `null`).
- **When to use**: When an error is non-fatal and a standardized default is acceptable by business rules (e.g. replacing a corrupt customer age with `null`).

---

## 4. Empirical Source Profiling Catalog

The following metrics represent the exact, verified ground-truth values discovered across the raw operational files:

### Source 1: `src_orders` (`raw/postgres_like/orders.csv`)
- **Total Raw Rows:** $502,000$
- **Total Columns:** $19$
- **Candidate Primary Key:** `order_id` (Non-unique! Contains $2,000$ duplicate records).
- **Foreign Keys:**
  - `customer_id` $\rightarrow$ $12$ records reference nonexistent customer `C9999999`.
  - `product_id` $\rightarrow$ $13$ records reference nonexistent product `P999`.
  - `store_id` $\rightarrow$ $10$ records reference nonexistent store `S999`.
  - `campaign_id` $\rightarrow$ Valid foreign keys across `CMP001` - `CMP007`.

| Column Name | Raw Data Type | Null Count | Null % | Distinct | Min Value | Max Value | Suspicious Values / Observations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `order_id` | text | 0 | 0.0% | 500,000 | ORD2025000000001 | ORD2025000500000 | 2,000 business-key duplicate rows (sampled duplicates with modified net sales). |
| `order_datetime` | text | 0 | 0.0% | 496,112 | 1900-01-01 00:00:00 | 2026-04-30 21:14:02 | 15 rows with `1900-01-01` legacy system default; 7 rows with future dates (> 2025-12-31). |
| `customer_id` | text | 0 | 0.0% | 25,001 | C0000001 | C9999999 | 12 orphan rows referencing invalid customer `C9999999`. |
| `product_id` | text | 0 | 0.0% | 21 | P001 | P999 | 13 orphan rows referencing invalid product `P999`. |
| `store_id` | text | 0 | 0.0% | 36 | S001 | S999 | 10 orphan rows referencing invalid store `S999`. |
| `campaign_id` | text | 0 | 0.0% | 7 | CMP001 | CMP007 | Valid. 7 campaigns represented. |
| `sales_channel_en` | text | 0 | 0.0% | 10 | Amazon Egypt | Website | Clean channel distribution across 10 omnichannel streams. |
| `sales_channel_ar` | text | 0 | 0.0% | 10 | أمازون مصر | فرع | Clean Arabic channel representations. |
| `payment_method_en`| text | 0 | 0.0% | 6 | Cash on Delivery | Vodafone Cash | 6 payment options (COD, Cards, InstaPay, Vodafone Cash, Meeza). |
| `payment_method_ar`| text | 0 | 0.0% | 6 | إنستاباي | ميزة | Bilingual Arabic payment method labels. |
| `quantity` | text/number | 0 | 0.0% | 8 | -1 | 6 | 35 invalid quantity records: 20 rows with `0`, 15 rows with `-1`. |
| `unit_price_egp` | text/number | 0 | 0.0% | 21 | -10.0 | 699.0 | 10 records with negative unit price (`-10.0` EGP). |
| `discount_pct` | text/number | 0 | 0.0% | 6 | 0.0 | 0.20 | Valid percentages: 0%, 5%, 10%, 15%, 20%. |
| `gross_sales_egp` | text/number | 0 | 0.0% | 114 | -10.0 | 4,194.0 | Corrupted by negative quantities and prices. |
| `discount_egp` | text/number | 0 | 0.0% | 138 | 0.0 | 838.8 | Valid discount calculation relative to gross. |
| `net_sales_egp` | text/number | 0 | 0.0% | 246 | -10.0 | 3,984.3 | Corrupted by negative gross sales and 2,000 modified duplicate rows. |
| `cost_egp` | text/number | 0 | 0.0% | 105 | -82.0 | 2,370.0 | Corrupted by negative quantities. |
| `order_status` | text | 0 | 0.0% | 6 | Cancelled | completed | Casing/spelling drift: `Completed` (433,489), `completed` (4,516), `Complete` (4,515). Total Completed: 442,520. |
| `currency` | text | 0 | 0.0% | 4 | EGP | جنيه مصري | Formatting inconsistency: `EGP` (314,500), `جنيه` (157,803), `EGP ` (19,657), `جنيه مصري` (10,040). |

---

### Source 2: `src_customers` (`raw/postgres_like/customers.csv`)
- **Total Raw Rows:** $25,200$
- **Total Columns:** $11$
- **Candidate Primary Key:** `customer_id` (Contains $200$ duplicate IDs, of which $194$ are exact duplicate full-row entries).

| Column Name | Raw Data Type | Null Count | Null % | Distinct | Min Value | Max Value | Suspicious Values / Observations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `customer_id` | text | 0 | 0.0% | 25,000 | C0000001 | C0025000 | 200 duplicate records; 194 exact duplicate rows. |
| `customer_name_ar`| text | 0 | 0.0% | 276 | آية إبراهيم | يوسف منصور | Arabic names cleanly encoded in UTF-8. |
| `customer_name_en`| text | 0 | 0.0% | 436 | Ahmed Ahmed | Youssef Youssef| English transliterations. |
| `gender` | text | 0 | 0.0% | 2 | Female | Male | 78% Female, 22% Male. |
| `birth_year` | text/number | 0 | 0.0% | 34 | 1970 | 2003 | Customers aged 22 to 55. Clean demographic profile. |
| `governorate` | text | 0 | 0.0% | 44 | Alexandria | sohag | Mixed casing: `Cairo` vs `cairo`, `Giza` vs `giza`. 22 governorates. |
| `area` | text | 151 | 0.6% | 51 | 10th of Ramadan | Zagazig | 151 missing values. |
| `phone` | text | 302 | 1.2% | 24,670 | +20 1000000858 | 01099999718 | 302 nulls. 38 records formatted with international prefix `+20 10...` instead of domestic `010...`. |
| `email` | text | 227 | 0.9% | 24,780 | ahmed.c0000001 | ZAYED.C0000040 | 227 nulls. 40 uppercase email strings (`AHMED.C0000123@EXAMPLE.COM`). |
| `signup_date` | text/date | 0 | 0.0% | 1,099 | 2023-01-01 | 2026-01-05 | Dates spanning 2023 to early 2026. |
| `customer_segment`| text | 0 | 0.0% | 4 | Premium | Student | Segments: Retail, Premium, Student, Professional. |

---

### Source 3: `src_products` (`raw/postgres_like/products.csv`)
- **Total Raw Rows:** $20$
- **Total Columns:** $11$
- **Candidate Primary Key:** `product_id` (Unique: $20$ products, `P001` - `P020`).
- **Categories:** Skincare (5), Makeup (5), Haircare (3), Fragrance (3), Body Care (3), Gift Sets (1).
- **Currencies:** `EGP`, `EGP `, `جنيه`.
- **Price Range:** 99.0 EGP (`Gentle Hand Cream`) to 699.0 EGP (`Beauty Essentials Gift Box`).
- **Cost Range:** 52.0 EGP to 395.0 EGP.

---

### Source 4: `src_stores` (`raw/postgres_like/stores.csv`)
- **Total Raw Rows:** $35$
- **Total Columns:** $7$
- **Candidate Primary Key:** `store_id` (Unique: $35$ stores, `S001` - `S035`).
- **Governorates Covered:** All 22 active Egyptian governorates.
- **Store Types:** Mall, Street, Pharmacy, Kiosk.
- **Distribution Regions:** Cairo Hub, Delta Hub, Upper Egypt Hub, Canal Hub.

---

### Source 5: `src_inventory` (`raw/csv/inventory_monthly.csv`)
- **Total Raw Rows:** $8,400$ ($35\text{ stores} \times 20\text{ products} \times 12\text{ months}$)
- **Total Columns:** $8$
- **Compound Key:** `month` + `store_id` + `product_id`.
- **Identified Anomalies:**
  - $50$ records with negative closing stock (`closing_stock < 0`, e.g. $-3, -7$).
  - $50$ records with negative damaged quantities (`damaged_qty = -1`).
  - $50$ records with implausibly inflated sales spikes (`sold_qty` quadrupled).

---

### Source 6: `src_targets` (`raw/excel/commercial_reference_data.xlsx` $\rightarrow$ `Targets`)
- **Total Raw Rows:** $417$
- **Expected Rows:** $35\text{ stores} \times 12\text{ months} = 420\text{ target records}$.
- **Identified Anomalies:**
  - $5$ missing store-month target combinations ($420 - 5 = 415$).
  - $2$ duplicate store-month target records ($415 + 2 = 417$).
  - Net targets require deduplication and zero-fill reconciliation.

---

## 5. Profiling Summary Checklist

Before proceeding to cleaning:
- [x] Column profiling set to **Entire dataset**.
- [x] Identified 2,000 order duplicate IDs and 200 customer duplicate IDs.
- [x] Identified 35 quantity anomalies and 10 negative price anomalies.
- [x] Identified 35 broken foreign key orders.
- [x] Identified 22 order timestamp anomalies (15 at 1900-01-01, 7 in 2026).
- [x] Identified currency text variations (`EGP`, `EGP `, `جنيه`, `جنيه مصري`).
- [x] Identified casing drift across governorates, customer emails, and order statuses.
- [x] Identified 100 inventory quantity errors (negative stock and damages).
- [x] Identified 2 duplicate targets and 5 missing targets.
