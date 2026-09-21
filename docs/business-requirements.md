# Business Requirements & Domain Context

## 1. Company Profile: Cleopatra Modern Cosmetics (كليوباترا كوزماتكس الحديثة)

**Cleopatra Modern Cosmetics** is a leading omnichannel beauty, personal care, and cosmetic retail enterprise headquartered in New Cairo, Egypt. The company operates:
- **35 Physical Stores**: Across Greater Cairo, Alexandria, Nile Delta, Canal Cities, and Upper Egypt (Retail flagships, pharmacy partner concessions, and express mall kiosks).
- **Digital Direct-to-Consumer Channels**: E-commerce web storefront and native Mobile App.
- **Third-Party Marketplaces**: Amazon Egypt, Noon Egypt, and TikTok Shop.
- **Social Commerce**: Direct sales via Instagram Direct and WhatsApp Business.

---

## 2. Egyptian Market Context & Dynamics

Operating an analytics platform in the Egyptian retail market requires handling domain-specific operational characteristics:

1. **Currency Volatility & Sourcing**:
   Cosmetics in Egypt feature a mix of locally manufactured formulas (`Local`) and imported prestige brands (`Imported` from France, South Korea, and Italy). Due to currency floatation, prices and costs fluctuate against USD and EUR. Tracking Gross Margin % and Currency is critical for commercial sustainability.
2. **Payment Ecosystem in Egypt**:
   - **Cash on Delivery (COD)**: Remains significant (~40-50% of online orders), with higher return and cancellation risk.
   - **Electronic Cards & Meeza (ميزة)**: National payment scheme.
   - **Mobile Wallets & Instant Networks**: Explosive growth in **Vodafone Cash (فودافون كاش)** and **InstaPay (إنستاباي)**.
   - **Alternative Payment & Buy-Now-Pay-Later (BNPL)**: **Fawry (فوري)** and **ValU (ڤاليو)**.
3. **Geographic Distribution & Logistics**:
   Operations span 22 Egyptian governorates grouped into 4 logistics hubs:
   - Greater Cairo (Cairo, Giza, Qalyubia)
   - Alexandria & North Coast (Alexandria, Beheira, Matrouh)
   - Delta & Canal (Dakahlia, Gharbia, Sharqia, Port Said, Suez, Ismailia)
   - Upper Egypt (Faiyum, Minya, Asyut, Sohag, Qena, Luxor, Aswan)

---

## 3. Core Business Questions Answered by the Platform

### 3.1 Commercial & Sales Performance
- What is our daily and monthly Net Revenue, Gross Margin %, and Average Order Value (AOV)?
- How does revenue break down across product categories (Skincare, Makeup, Haircare, Fragrance, Body Care, Gift Sets)?
- What is the margin differential between Locally manufactured products vs Imported luxury lines?
- Which sales channels (Digital Direct vs Marketplace vs Physical Retail) generate the highest customer lifetime value?

### 3.2 Target Achievement & Store Quotas
- Which stores achieved their monthly sales target in EGP and order count?
- What is the revenue variance between actual sales and commercial targets by store and governorate?
- Where are the regional sales gaps requiring tactical promotional support?

### 3.3 Customer Segmentation & Retention (RFM)
- Who are our "Champions" (highest recency, frequency, and spend)?
- Which customer cohorts are "At Risk" or "Lost" and require automated win-back SMS campaigns?
- What is the geographic migration of customers across governorates, tracked via SCD Type 2?

### 3.4 Supply Chain & Inventory Health
- What is our closing stock valuation in EGP across all distribution centers and retail stores?
- Which store-product combinations are experiencing stockouts (closing stock $\le 0$)?
- What is our monthly damage rate (damaged units / total handled stock) and where do logistics shrinkage losses occur?

### 3.5 Marketing Campaign ROI
- What was the return on investment (Revenue / Budget) for paid campaigns across Meta, TikTok, and Google Ads?
- What was the customer acquisition velocity during seasonal campaign pushes (e.g. White Friday, Mother's Day, Summer Glam)?

### 3.6 Data Quality & Observability
- How many defective orders were quarantined this batch and why?
- What is the end-to-end data quality score across all operational data feeds?
- Are there orphan foreign keys or duplicate customer accounts requiring master data management (MDM)?

---

## 4. SLA & Reporting Cadence

| Tier | Cadence | SLA | Primary Stakeholders |
| :--- | :--- | :--- | :--- |
| **Executive Cockpit** | Daily at 06:00 AM EET | < 15 min refresh | CEO, CFO, VP of Commercial |
| **Store Operations** | Hourly Intraday | < 5 min latency | Store Managers, Regional Supervisors |
| **Marketing Attribution**| Daily at 08:00 AM EET | < 30 min refresh | CMO, Performance Marketing Leads |
| **Supply Chain & Stock** | Daily at 05:00 AM EET | < 20 min refresh | VP of Supply Chain, Logistics Directors |
| **Data Quality Audit** | Every ETL Batch Run | Real-time / Immediate | Lead Analytics Engineer, Data Architect |
