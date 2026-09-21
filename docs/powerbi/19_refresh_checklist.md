# Playbook 19: Post-Refresh Data Engineering Validation Checklist

## 1. Objective & Scope

In automated enterprise reporting environments, a successful data refresh does not guarantee correct data. A refresh can succeed with code 200 while silently ingesting thousands of corrupted rows, negative prices, or broken foreign keys.

This playbook provides a **Post-Refresh Standard Operating Procedure (SOP)** and an automated checklist to ensure pipeline integrity after every scheduled or manual refresh.

---

## 2. The 8-Point Post-Refresh Inspection Checklist

| Check # | Inspection Area | Primary Metric / Query | Acceptance Threshold | Failure Action |
| :---: | :--- | :--- | :--- | :--- |
| **01** | **Row Count Volumetrics** | `[Total Raw Orders Ingested]` | Expected growth $\pm 15\%$ of daily average baseline ($500,000+$). | Investigate source database dump file size; verify file was not truncated during FTP transfer. |
| **02** | **Quarantine Spike Rate** | `[DQ Rejection Rate %]` | $\le 0.50\%$ of total raw orders ($< 2,500$ rows). | If rejection rate exceeds $1.0\%$, inspect `rejected_orders[DataQualityReason]` to identify new upstream schema bugs. |
| **03** | **Referential Integrity** | `[Assertion 02 - Orphan Customer Keys]` | Strictly **$0$**. | Check for newly registered customers missing from the PostgreSQL `customers` table export. |
| **04** | **Negative Sales Breach** | `[Assertion 01 - Negative Sales Breach]` | Strictly **$0$**. | Review newly introduced promotional discount codes or negative unit prices in product master. |
| **05** | **New / Unmapped Categories** | Distinct count of `cln_products[category]` | Exactly **$6$** approved categories (Skincare, Makeup, Haircare, Fragrance, Body Care, Gift Sets). | Check for product catalog typos (`"Skin care"` vs `"Skincare"`). Update `ref_category_mapping` if legitimate new line. |
| **06** | **Inventory Balance Integrity** | `[Assertion 04 - Negative Damaged Stock]` | Strictly **$0$**. | Notify warehouse logistics team of negative stock or inventory adjustment errors. |
| **07** | **Commercial Target Coverage** | `COUNTROWS(fact_targets)` | $\ge 415$ active monthly store quotas. | Verify commercial Excel workbook was not overwritten with an empty sheet or outdated targets. |
| **08** | **Date Continuity** | `[Assertion 03 - Date Dimension Gaps]` | Strictly **$0$**. | Ensure `pEndDate` covers the current calendar year. |

---

## 3. Step-by-Step Operator Inspection Workflow

### Step 3.1: Open the Data Quality Dashboard (Page 5)
1. Immediately following refresh completion, navigate to **Page 5: Data Quality & Pipeline Health**.
2. Verify the **Pipeline Health Index** KPI card:
   - Green ($\ge 99.0\%$): Normal operations.
   - Yellow ($95.0\% - 98.9\%$): Warning. Elevate to engineering for review.
   - Red ($< 95.0\%$): Critical anomaly. Do NOT release report to executive stakeholders.

### Step 3.2: Review the Quarantine Table
1. Check if new defect categories have appeared in the Pareto bar chart.
2. If `DataQualityReason` displays an unhandled error message (e.g. `"Unknown Currency: SAR"`), take note of the new currency or payment gateway alias.

### Step 3.3: Verify Reconciliation Ledger
1. In the reconciliation table, confirm that:
   $$\text{Total Raw Rows} - \text{Quarantined Rows} = \text{Valid Production Rows}$$
   $$502,000 - 2,097 = 499,903$$
2. Confirm `[Reconciliation Status]` displays: `"BALANCED (100% Reconciled)"`.

---

## 4. Automated Alerting & Governance Sign-Off

In Power BI Service (Cloud deployment), configure **Data-Driven Alerts**:
1. On the **Page 5** dashboard, select the card `[Quarantined Orders]`.
2. Click **More options (`...`)** $\rightarrow$ **Manage alerts**.
3. Set alert condition:
   - *Threshold:* When value is greater than $2,500$.
   - *Frequency:* Once an hour (or after every refresh).
   - *Action:* Send automated notification to BI Operations Teams channel.
