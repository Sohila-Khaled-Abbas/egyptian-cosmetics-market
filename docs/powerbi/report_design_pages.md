# Enterprise Report Design & User Experience Playbook (Pages 1 - 5)

## 1. Executive Summary & Design System

A portfolio-grade Power BI report must avoid cluttered, amateur designs ("dashboard soup"). It must embody executive clarity, structured visual hierarchy, purposeful whitespace, and accessible color semantics.

### Corporate Design Palette ("Cleopatra Modern Beauty"):
- **Primary Brand Navy (Dark Contrast):** `#0F2027` (Header banners, primary text, high-level structural containers).
- **Secondary Slate Blue:** `#203A43` (Card outlines, secondary series).
- **Accent Emerald / Green (Positive / Valid):** `#107C41` (Target met, positive margin, clean data quality).
- **Accent Coral / Amber (Warning / At Risk):** `#D97706` (Low stock, moderate discount, customer at-risk).
- **Accent Crimson (Negative / Rejected):** `#D83B01` (Stockouts, quota deficit, quarantined invalid data).
- **Canvas Background:** Neutral warm light gray `#F8FAFC`.
- **Card Background:** Pure white `#FFFFFF` with soft 1px border `#E2E8F0`.
- **Typography:** Segoe UI / Aptos for Latin text; Cairo / Segoe UI for Arabic text.

---

## 2. Global Navigation & Bilingual Slicer Banner

Every page features a persistent top banner ($60\text{ px}$ height):
- **Logo / Company Name:** `كليوباترا كوزماتكس الحديثة | Cleopatra Modern Cosmetics`
- **Current Page Title:** Large bold 18pt font.
- **Global Slicers (Top Right):**
  - **Date Range Slicer:** Slider / dropdown on `DimDate[Date]`.
  - **Governorate Slicer:** Dropdown on `DimStore[Governorate]`.
  - **Language Preference:** Parameterized toggle switching display labels between English and Arabic (`product_name_en` vs `product_name_ar`).

---

## 3. Page 1 — Executive Overview

### Strategic Purpose:
Provides the C-suite (CEO, CFO, Commercial Director) with immediate situational awareness regarding top-line revenue, profitability, quota achievement, and macro sales distribution.

### Visual Architecture & Layout:
```
+---------------------------------------------------------------------------------------------------------------+
| [TOP BANNER] Executive Overview | Filters: Year 2025 | All Governorates | All Channels                        |
+---------------------------------------------------------------------------------------------------------------+
| [CARD 1] Net Sales     | [CARD 2] Gross Profit  | [CARD 3] Margin % | [CARD 4] Orders | [CARD 5] Customers    |
|   142.8M EGP (+14% YoY)|   68.4M EGP (47.9%)    |      47.9%        |     442,520     |      25,000           |
+-------------------------------------------------+-------------------------------------------------------------+
| [CHART 1: Monthly Net Sales vs Target (Trend)]   | [CHART 2: Sales by Egyptian Governorate (Bar Chart)]        |
| - Columns: Actual Net Sales                     | - Cairo: 42.1M EGP                                          |
| - Line: Sales Target                            | - Giza: 28.6M EGP                                           |
| - Visual variance shading                       | - Alexandria: 21.4M EGP                                     |
|                                                 | - Delta & Upper Egypt Hubs                                  |
+-------------------------------------------------+-------------------------------------------------------------+
| [CHART 3: Sales by Product Category (Donut)]    | [CHART 4: Omnichannel Distribution (100% Stacked Bar)]      |
| - Skincare: 38%                                 | - Social Commerce (Instagram, TikTok, FB): 35%              |
| - Fragrance: 26%                                | - Marketplaces (Amazon EG, Noon, Jumia): 32%                |
| - Makeup: 18%                                   | - Physical Stores & Pharmacies: 21%                         |
| - Body Care & Haircare: 18%                     | - Direct Website: 12%                                       |
+---------------------------------------------------------------------------------------------------------------+
```

### Key Interactions & Drill-Throughs:
- **Drill-Through Target:** Right-click any category bar (e.g. "Skincare") $\rightarrow$ **Drill through to Page 2: Sales Analytics**.

---

## 4. Page 2 — Sales & Commercial Analytics

### Strategic Purpose:
Enables Brand Managers, Merchandisers, and Regional Sales Directors to dissect product velocity, discount elasticity, brand profitability, and distribution channel efficiency.

### Visual Architecture & Layout:
1. **Top KPI Bar:**
   - `[Units Sold]` (Total volume)
   - `[Average Selling Price]`
   - `[Average Order Value]`
   - `[Discount %]` (Corporate average promotional discount)
2. **Matrix Visual: Brand & Category Profitability Waterfall:**
   - Rows: `DimProduct[Category]` $\rightarrow$ `DimProduct[Brand EN]` $\rightarrow$ `DimProduct[Product Name EN]`
   - Values: `[Units Sold]`, `[Gross Sales]`, `[Discount]`, `[Net Sales]`, `[Cost]`, `[Gross Profit]`, `[Gross Margin %]`.
   - Conditional Formatting: Color scale on `[Gross Margin %]` (Green for $\ge 50\%$, Red for $< 35\%$).
3. **Scatter Plot: Pricing & Elasticity:**
   - X-axis: `[Discount %]`
   - Y-axis: `[Units Sold]`
   - Bubble Size: `[Net Sales]`
   - Legend: `DimProduct[Category]`
   - *Insight:* Shows which skincare SKUs surge in volume under discounts vs luxury fragrances that sell inelastic of promotions.
4. **Clustered Bar Chart: Channel Performance:**
   - Y-axis: `DimChannel[Channel Name EN]`
   - X-axis: `[Net Sales]` and `[Target Variance]`

---

## 5. Page 3 — Customer & RFM Behavioral Analytics

### Strategic Purpose:
Empowers the Growth and CRM teams to monitor customer acquisition velocity, track retention, and execute targeted campaigns based on RFM segmentation.

### Visual Architecture & Layout:
1. **Top KPI Bar:**
   - `[Customers]` (Total active transacting)
   - `[New Customers]` (First-time buyers in period)
   - `[Returning Customers]` (Repeat customer pool)
   - `[Customer Revenue]` (Average LTV per active shopper)
2. **Treemap: Customer RFM Segmentation:**
   - Group: `ref_rfm_segments[SegmentName]` (`Champions`, `Loyal Customers`, `Potential Loyalists`, `At Risk`, `Lost Customers`)
   - Values: `[RFM Customer Count]`
   - Tooltip: Total Segment Spend and Average Frequency.
3. **Line Chart: Customer Cohort Acquisition Trend:**
   - X-axis: `DimDate[Year Month]`
   - Series: `[New Customers]` vs `[Returning Customers]`
4. **Table: High-Value Customer Action Register:**
   - Columns: `Customer ID`, `Customer Name EN`, `Governorate`, `Phone`, `Recency Days`, `Orders`, `Net Spend`, `RFM Segment`.
   - Filtered by default to: `Customer RFM Segment = "At Risk"`.
   - Export Enabled: CRM managers export directly to trigger reactivation SMS promotions.

---

## 6. Page 4 — Inventory & Supply Chain Analytics

### Strategic Purpose:
Provides Logistics and Warehouse Directors with complete visibility over store-level stock balances, depleted SKUs, damaged stock loss value, and replenishment priorities.

### Visual Architecture & Layout:
1. **Top KPI Bar:**
   - `[Closing Stock]` (Total units available)
   - `[Closing Stock Value EGP]` (Capital locked in inventory)
   - `[Stockout Risk Count]` (Urgent red alert for depleted SKUs)
   - `[Low Stock Count]` (Orange warning for impending stockout)
   - `[Damage Loss Ratio %]`
2. **Heatmap Matrix: Store vs Product Stock Balance:**
   - Rows: `DimStore[Governorate]` $\rightarrow$ `DimStore[Store Name EN]`
   - Columns: `DimProduct[Product Name EN]`
   - Values: `[Closing Stock]`
   - Background Formatting: Red for $0$, Yellow for $1-15$, Green for $> 15$.
3. **Bar Chart: Stockout Risk by Category:**
   - Y-axis: `DimProduct[Category]`
   - X-axis: `[Stockout Risk Count]`
4. **Table: Damaged Stock Financial Audit:**
   - Columns: `Store Name`, `Product Name`, `Damaged Units`, `Damaged Stock Loss EGP`.

---

## 7. Page 5 — Data Quality & Pipeline Health

### Strategic Purpose:
Serves as the internal Data Governance cockpit, demonstrating complete pipeline auditability, tracking quarantine counts, and asserting zero data leakage.

### Visual Architecture & Layout:
*(Detailed in Playbook 16: KPI Scorecard, Multi-Entity Quality Matrix, Defect Pareto Visual, and Interactive Quarantine Drill-Through Table).*

---

## 8. UX Standards & Accessibility Guidelines

1. **Meaningful Tooltips (Report Page Tooltips):**
   - Hovering over any bar in the "Sales by Governorate" chart renders a compact tooltip page displaying the top 3 selling products and store formats in that governorate.
2. **Zero Default Slicers Left Empty:**
   - All slicers default to "All" to prevent empty visual states.
3. **Consistent Number Formatting:**
   - Currency is formatted with thousands separators and explicit currency code (`#,##0.00 "EGP"`).
   - Percentages are formatted to one decimal place (`0.0%`).
4. **Accessibility & Color Vision Deficiency:**
   - Color is never used as the sole indicator of status. Red/Green indicators are paired with icons (▲ / ▼) or explicit text labels (`"Valid"`, `"Rejected"`, `"Over Target"`, `"Under Target"`).
