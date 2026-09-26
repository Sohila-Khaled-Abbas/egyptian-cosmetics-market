# Playbook 04: Power Query Data Cleaning & Type Standardization (GUI-First Guide)

## 1. Objective & Scope

Raw operational data contains whitespace noise, inconsistent casing, localized currency strings, non-standard telephone formats, and uncoerced string types. 

This playbook provides a **100% GUI-first walkthrough** using Power Query Desktop's visual ribbon controls, context menus, and transformation dialogs to:
1. Build the **`02_Staging`** layer (`stg_*`) to decouple raw file streams and enforce baseline data types.
2. Build the **`04_Cleansed`** layer (`cln_*`) to execute visual text trimming, non-printable character cleaning, telephone standardizations, currency unification, and status consolidation.
3. Preserve bilingual Arabic and English attributes for executive reporting.

> [!IMPORTANT]
> **Load Settings Reminder**:
> All queries created in `02_Staging` and `04_Cleansed` must have **`Enable Load = False`** (italicized names in the Queries pane).

---

## 2. Why Data Types Must Be Finalized Before Downstream Modeling

1. **Numeric & Financial Precision**: Columns like `quantity`, `unit_price_egp`, and `net_sales_egp` must be recognized as numeric (`Whole Number` and `Fixed Decimal Number / Currency`) before joins or DAX aggregation.
2. **Key Joining Integrity**: Primary and Foreign keys (`order_id`, `customer_id`, `product_id`, `store_id`) must strictly remain as **`Text`** (`ABC`). Converting IDs to numeric can strip critical alphanumeric codes or leading zeros (e.g. `C0001` or `010...`).
3. **Locale-Aware Parsing**: Dates like `"2025-05-17 22:32:02"` must be parsed using invariant or explicit English formats to prevent month/day transposition on Arabic or European Windows regional settings.

---

## 3. Step-by-Step Staging Layer (`02_Staging`) via GUI

The Staging layer creates decoupled copies of your raw tables, sets proper column types, and prepares clean tables for downstream rules.

---

### 3.1: Building `stg_customers` (25,200 Rows)

#### 🖱️ Step-by-Step GUI Actions:
1. **Reference Source Query**:
   - In the left **Queries** pane, expand folder `01_Source`.
   - Right-click `src_customers` $\rightarrow$ select **Reference**.
   - A new query named `src_customers (2)` appears.
2. **Rename and Organize**:
   - Right-click the new query $\rightarrow$ select **Rename** $\rightarrow$ type `stg_customers`.
   - Right-click `stg_customers` $\rightarrow$ **Move to Group** $\rightarrow$ select **`02_Staging`**.
   - Verify `Enable Load` is unchecked (text appears in italics).
3. **Assign Column Data Types via Column Header Icons**:
   Click the small type icon (e.g., `ABC` or `123`) on the left of each column header:
   * `customer_id` $\rightarrow$ Click icon $\rightarrow$ select **Text** (`ABC`)
   * `customer_name_ar` $\rightarrow$ select **Text** (`ABC`)
   * `customer_name_en` $\rightarrow$ select **Text** (`ABC`)
   * `gender` $\rightarrow$ select **Text** (`ABC`)
   * `birth_year` $\rightarrow$ select **Whole Number** (`123`)
   * `governorate` $\rightarrow$ select **Text** (`ABC`)
   * `area` $\rightarrow$ select **Text** (`ABC`)
   * `phone` $\rightarrow$ select **Text** (`ABC`) *(⚠️ Never select number; preserving leading zeros is mandatory!)*
   * `email` $\rightarrow$ select **Text** (`ABC`)
   * `signup_date` $\rightarrow$ select **Date** (`📅`)
   * `customer_segment` $\rightarrow$ select **Text** (`ABC`)

#### 📋 Expected "Applied Steps" Pane:
* `Source`
* `Changed Type`

---

### 3.2: Building `stg_products` (20 Rows)

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `src_products` in `01_Source` $\rightarrow$ select **Reference**.
2. Rename query to `stg_products` $\rightarrow$ move to group **`02_Staging`**.
3. Set column types via header icons:
   * `product_id` $\rightarrow$ **Text** (`ABC`)
   * `product_name_en` $\rightarrow$ **Text** (`ABC`)
   * `product_name_ar` $\rightarrow$ **Text** (`ABC`)
   * `brand_en` $\rightarrow$ **Text** (`ABC`)
   * `brand_ar` $\rightarrow$ **Text** (`ABC`)
   * `category` $\rightarrow$ **Text** (`ABC`)
   * `subcategory` $\rightarrow$ **Text** (`ABC`)
   * `list_price_egp` $\rightarrow$ **Decimal Number** (`1.2`)
   * `standard_cost_egp` $\rightarrow$ **Decimal Number** (`1.2`)
   * `currency` $\rightarrow$ **Text** (`ABC`)
   * `origin` $\rightarrow$ **Text** (`ABC`)

---

### 3.3: Building `stg_stores` (35 Rows)

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `src_stores` in `01_Source` $\rightarrow$ select **Reference**.
2. Rename query to `stg_stores` $\rightarrow$ move to group **`02_Staging`**.
3. Set column types via header icons:
   * `store_id` $\rightarrow$ **Text** (`ABC`)
   * `store_name_en` $\rightarrow$ **Text** (`ABC`)
   * `store_name_ar` $\rightarrow$ **Text** (`ABC`)
   * `governorate` $\rightarrow$ **Text** (`ABC`)
   * `area` $\rightarrow$ **Text** (`ABC`)
   * `store_type` $\rightarrow$ **Text** (`ABC`)
   * `distribution_region` $\rightarrow$ **Text** (`ABC`)

---

### 3.4: Building `stg_orders` (502,000 Rows)

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `src_orders` in `01_Source` $\rightarrow$ select **Reference**.
2. Rename query to `stg_orders` $\rightarrow$ move to group **`02_Staging`**.
3. Set column types via header icons:
   * `order_id` $\rightarrow$ **Text** (`ABC`)
   * `order_datetime` $\rightarrow$ **Date/Time** (`📅🕒`)
   * `customer_id` $\rightarrow$ **Text** (`ABC`)
   * `product_id` $\rightarrow$ **Text** (`ABC`)
   * `store_id` $\rightarrow$ **Text** (`ABC`)
   * `campaign_id` $\rightarrow$ **Text** (`ABC`)
   * `sales_channel_en` $\rightarrow$ **Text** (`ABC`)
   * `sales_channel_ar` $\rightarrow$ **Text** (`ABC`)
   * `payment_method_en` $\rightarrow$ **Text** (`ABC`)
   * `payment_method_ar` $\rightarrow$ **Text** (`ABC`)
   * `quantity` $\rightarrow$ **Whole Number** (`123`)
   * `unit_price_egp` $\rightarrow$ **Decimal Number** (`1.2`)
   * `discount_pct` $\rightarrow$ **Decimal Number** (`1.2`)
   * `gross_sales_egp` $\rightarrow$ **Decimal Number** (`1.2`)
   * `discount_egp` $\rightarrow$ **Decimal Number** (`1.2`)
   * `net_sales_egp` $\rightarrow$ **Decimal Number** (`1.2`)
   * `cost_egp` $\rightarrow$ **Decimal Number** (`1.2`)
   * `order_status` $\rightarrow$ **Text** (`ABC`)
   * `currency` $\rightarrow$ **Text** (`ABC`)

---

### 3.4b: Building `stg_orders_historical` (50,200 Rows)

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `src_orders_historical` in `01_Source` $\rightarrow$ select **Reference**.
2. Rename query to `stg_orders_historical` $\rightarrow$ move to group **`02_Staging`**.
3. Set identical column types via header icons matching `stg_orders`:
   * `order_id`, `customer_id`, `product_id`, `store_id`, `campaign_id` $\rightarrow$ **Text** (`ABC`)
   * `order_datetime` $\rightarrow$ **Date/Time** (`📅🕒`)
   * `sales_channel_en`, `sales_channel_ar`, `payment_method_en`, `payment_method_ar`, `order_status`, `currency` $\rightarrow$ **Text** (`ABC`)
   * `quantity` $\rightarrow$ **Whole Number** (`123`)
   * `unit_price_egp`, `discount_pct`, `gross_sales_egp`, `discount_egp`, `net_sales_egp`, `cost_egp` $\rightarrow$ **Decimal Number** (`1.2`)
4. Verify **Enable Load** is **unchecked** (query name appears in italics).

---

### 3.5: Building `stg_inventory` (8,400 Rows)

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `src_inventory` in `01_Source` $\rightarrow$ select **Reference**.
2. Rename query to `stg_inventory` $\rightarrow$ move to group **`02_Staging`**.
3. Set column types via header icons:
   * `month` $\rightarrow$ **Date** (`📅`)
   * `store_id` $\rightarrow$ **Text** (`ABC`)
   * `product_id` $\rightarrow$ **Text** (`ABC`)
   * `opening_stock`, `received_qty`, `sold_qty`, `damaged_qty`, `closing_stock` $\rightarrow$ select each column and set to **Whole Number** (`123`).

---

### 3.6: Building `stg_targets` (417 Rows)

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `src_targets` in `01_Source` $\rightarrow$ select **Reference**.
2. Rename query to `stg_targets` $\rightarrow$ move to group **`02_Staging`**.
3. Set column types via header icons:
   * `target_month` $\rightarrow$ **Date** (`📅`)
   * `store_id` $\rightarrow$ **Text** (`ABC`)
   * `sales_target_egp` $\rightarrow$ **Decimal Number** (`1.2`)
   * `order_target` $\rightarrow$ **Whole Number** (`123`)

---

### 3.7: Building `stg_campaigns` (7 Rows)

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `src_campaigns` in `01_Source` $\rightarrow$ select **Reference**.
2. Rename query to `stg_campaigns` $\rightarrow$ move to group **`02_Staging`**.
3. Set column types via header icons:
   * `campaign_id` $\rightarrow$ **Text** (`ABC`)
   * `campaign_name_en` $\rightarrow$ **Text** (`ABC`)
   * `campaign_name_ar` $\rightarrow$ **Text** (`ABC`)
   * `start_date` $\rightarrow$ **Date** (`📅`)
   * `end_date` $\rightarrow$ **Date** (`📅`)
   * `budget_egp` $\rightarrow$ **Decimal Number** (`1.2`)
   * `discount_pct` $\rightarrow$ **Decimal Number** (`1.2`)

---

### 3.8: Building `stg_fx_rates` (730 Rows)

#### 📋 Central Bank FX API Data Dictionary (`exchange_rates.json`):
The raw API payload schema maps 730 records (USD and EUR closing exchange rates against EGP spanning 2023–2024):

| JSON Field Key | Sample Value | Data Type in JSON | Target Power Query Type | Semantic Description |
| :--- | :--- | :--- | :--- | :--- |
| `rate_date` | `1735689600000` | Integer (Epoch ms) | **Whole Number** (`123`) | Unix epoch timestamp in milliseconds representing quote date. |
| `base_currency` | `"USD"` / `"EUR"` | String (ISO 4217) | **Text** (`ABC`) | Base foreign currency being exchanged. |
| `rate` | `31.0082` | Float / Decimal | **Decimal Number** (`1.2`) | Daily exchange rate multiplier (EGP per 1 unit of `base_currency`). |
| `quote_currency` | `"EGP"` | String (ISO 4217) | **Text** (`ABC`) | Domestic quote currency (`EGP`). |
| `api_timestamp` | `"2025-01-01T09:00:00Z"` | String (ISO 8601 UTC) | **Date** (`📅`) or **Date/Time/Zone** (`🌐`) | Timestamp when the exchange rate quote was fetched from the API. |

#### 🖱️ Step-by-Step GUI Actions:
1. **Reference Source**:
   - Right-click `src_exchange_rates` in group `01_Source` $\rightarrow$ select **Reference**.
   - Rename the query to `stg_fx_rates` $\rightarrow$ drag/move into group **`02_Staging`**.
2. **Set Column Types via Header Icons**:
   - Click the type icon next to `base_currency` $\rightarrow$ select **Text** (`ABC`).
   - Click the type icon next to `quote_currency` $\rightarrow$ select **Text** (`ABC`).
   - Click the type icon next to `rate` (or `exchange_rate`) $\rightarrow$ select **Decimal Number** (`1.2`).
   - Click the type icon next to `rate_date` (or `rate_date_raw`) $\rightarrow$ select **Whole Number** (`123`).
   - Click the type icon next to `api_timestamp` $\rightarrow$ select **Date/Time/Timezone** (`🌐`) or **Date** (`📅`).
3. **Derive Calendar Date via GUI (Optional/Recommended)**:
   - Select the `api_timestamp` column.
   - Go to the **Add Column** ribbon tab $\rightarrow$ click the **Date** dropdown $\rightarrow$ select **Date Only**.
   - Rename this new column to `rate_date_canonical` (or keep `api_timestamp` typed as `Date` for direct date dimension joins).

---

## 4. Step-by-Step Cleansed Layer (`04_Cleansed`) via GUI

The Cleansed layer executes deterministic business standardization: removing whitespace, cleaning unprintable control characters, lowercasing emails, normalizing Egyptian phone numbers, and canonicalizing status codes.

---

### 4.1: Cleansing `cln_customers`

#### 🖱️ Step-by-Step GUI Actions:
1. **Reference Staging**:
   - Right-click `stg_customers` in `02_Staging` $\rightarrow$ select **Reference**.
   - Rename new query to `cln_customers`.
   - Move to group **`04_Cleansed`**.
2. **Trim & Clean Text Columns via Ribbon**:
   - Hold `Ctrl` and select the text columns: `customer_name_ar`, `customer_name_en`, `area`, `customer_segment`.
   - Switch to the **Transform** tab on the top ribbon.
   - Click the **Format** dropdown $\rightarrow$ click **Trim** (removes leading/trailing spaces).
   - Click the **Format** dropdown again $\rightarrow$ click **Clean** (strips non-printable ASCII/control characters).
3. **Lowercase Email Addresses**:
   - Click the `email` column header to select it.
   - On the **Transform** tab $\rightarrow$ click **Format** $\rightarrow$ select **lowercase**.
   - Click **Format** $\rightarrow$ select **Trim**.
4. **Standardize Egyptian Phone Numbers via GUI**:
   - Click the `phone` column header.
   - On the **Transform** tab, click **Replace Values**:
     - *Value To Find*: `+20 ` (note the trailing space)
     - *Replace With*: `0`
     - Click **OK**.
   - Click **Replace Values** again:
     - *Value To Find*: `+20`
     - *Replace With*: `0`
     - Click **OK**.
   - Click **Replace Values** again:
     - *Value To Find*: ` ` (single space)
     - *Replace With*: *(leave empty to remove all spaces)*
     - Click **OK**.
   - Click **Format** $\rightarrow$ **Trim**.
   *(All numbers now follow the unified local Egyptian 11-digit mobile standard `010...`, `011...`, `012...`, `015...`).*
5. **Standardize Governorate Names via Custom Function**:
   - On the top ribbon, switch to the **Add Column** tab.
   - Click the **Invoke Custom Function** button.
   - In the dialog:
     - *New column name*: `clean_governorate`
     - *Function query*: Select **`fnStandardizeGovernorate`** from the dropdown.
     - *governorate*: Select column **`governorate`**.
     - Click **OK**.
   - Right-click the old `governorate` column $\rightarrow$ select **Remove**.
   - Double-click the header of `clean_governorate` $\rightarrow$ rename it back to `governorate`.
   - Move the column back to its original position by dragging its header.

---

### 4.2: Cleansing `cln_products`

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `stg_products` $\rightarrow$ select **Reference** $\rightarrow$ Rename to `cln_products` $\rightarrow$ Move to **`04_Cleansed`**.
2. **Trim & Clean All Text**:
   - Hold `Ctrl` and select `product_name_en`, `product_name_ar`, `brand_en`, `brand_ar`, `category`, `subcategory`, `origin`.
   - **Transform** tab $\rightarrow$ **Format** $\rightarrow$ click **Trim**.
   - **Format** $\rightarrow$ click **Clean**.
3. **Normalize Currency Strings**:
   - Select the `currency` column.
   - On the **Transform** tab, click **Replace Values**:
     - *Value To Find*: `EGP `
     - *Replace With*: `EGP`
     - Click **OK**.
   - Click **Replace Values** again:
     - *Value To Find*: `جنيه`
     - *Replace With*: `EGP`
     - Click **OK**.
   - Click **Replace Values** again:
     - *Value To Find*: `جنيه مصري`
     - *Replace With*: `EGP`
     - Click **OK**.

---

### 4.3: Cleansing `cln_orders` (502,000 Rows)

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `stg_orders` $\rightarrow$ select **Reference** $\rightarrow$ Rename to `cln_orders` $\rightarrow$ Move to **`04_Cleansed`**.
2. **Trim & Clean Text Fields**:
   - Hold `Ctrl` and select `sales_channel_en`, `sales_channel_ar`, `payment_method_en`, `payment_method_ar`.
   - **Transform** tab $\rightarrow$ **Format** $\rightarrow$ **Trim**.
   - **Format** $\rightarrow$ **Clean**.
3. **Normalize Order Status via GUI**:
   > [!NOTE]
   > **Source Reality Check: No Arabic Words in Raw `order_status`**:
   > Profiling of the operational source table (`stg_orders` / `orders.csv`) confirms that `order_status` contains **only English strings** with casing and truncation anomalies:
   > - `Completed` ($433,489$ rows)
   > - `Returned` ($24,729$ rows)
   > - `Cancelled` ($19,770$ rows)
   > - `Pending` ($14,981$ rows)
   > - `completed` ($4,516$ rows — lowercase noise)
   > - `Complete` ($4,515$ rows — truncated spelling)
   > 
   > There are **no Arabic words** (`مكتمل`, `مرتجع`, `ملغي`) in the operational table itself. 
   > The required cleansing action here is to repair English casing and spelling defects. Full bilingual Arabic localization (`مكتمل`, `مرتجع`, `ملغي`, `قيد التنفيذ`), lifecycle categorization, and GAAP financial flags (`Is Revenue Recognized`) are systematically injected downstream in the **Data Modeling & Enrichment** step (via `ref_status_mapping` and `dim_order_status`).

   **Step-by-Step GUI Actions**:
   - Select the `order_status` column.
   - On the top ribbon, switch to the **Transform** tab $\rightarrow$ click **Format** $\rightarrow$ select **Capitalize Each Word** *(this automatically normalizes all `completed` lowercase rows to `Completed`)*.
   - On the **Transform** tab, click **Replace Values**:
     - *Value To Find*: `Complete`
     - *Replace With*: `Completed`
     - Click **OK** *(this unifies truncated `Complete` rows into `Completed`)*.
   *(Result: The column is now 100% standardized into 4 canonical business states: `Completed` [442,520], `Returned` [24,729], `Cancelled` [19,770], and `Pending` [14,981]).*

4. **Normalize Currency Strings via GUI**:
   - Select the `currency` column.
   - On the **Transform** tab, click **Replace Values**:
     - *Value To Find*: `EGP ` *(with trailing space)*
     - *Replace With*: `EGP`
     - Click **OK**.
   - Click **Replace Values** again:
     - *Value To Find*: `جنيه مصري`
     - *Replace With*: `EGP`
     - Click **OK**.
   - Click **Replace Values** again:
     - *Value To Find*: `جنيه`
     - *Replace With*: `EGP`
     - Click **OK**.
   *(All order currency values are now strictly canonicalized to `EGP`).*

5. **Normalize Campaign Foreign Keys (`campaign_id`) via GUI**:
   > [!NOTE]
   > **Resolving 17% Empty / Null Campaign IDs & Legacy `CAMP0X` Formatting:**
   > Profiling of `campaign_id` in the combined order stream reveals two distinct real-world characteristics:
   > 1. **17% Empty / Null values:** Orders resulting from direct walk-ins or organic website visits where no promo campaign was active.
   > 2. **Legacy `CAMP0X` format:** Historical 2024 orders used `CAMP01`–`CAMP07`, while the dimensional model (`dim_campaign`) expects `CMP001`–`CMP007`, where **`CMP006`** explicitly represents `"No Campaign"` (`لا توجد حملة`).
   >
   > If left blank or non-standard, these rows would generate broken relationships or blank member rows in Power BI. Replacing empty values with `CMP006` and unifying `CAMP0` to `CMP00` ensures 100% referential integrity with `dim_campaign`.

   **Step-by-Step GUI Actions**:
   - Select the `campaign_id` column.
   - On the **Transform** ribbon tab $\rightarrow$ click **Replace Values**:
     - *Value To Find*: *(leave completely empty or enter `null`)*
     - *Replace With*: `CMP006`
     - Click **OK** *(this routes all 17% organic/empty sales to the conformed "No Campaign" dimension member)*.
   - Select the `campaign_id` column again $\rightarrow$ click **Replace Values**:
     - *Value To Find*: `CAMP0`
     - *Replace With*: `CMP00`
     - Click **OK** *(this unifies legacy `CAMP01`-`CAMP07` codes to `CMP001`-`CMP007`)*.
   *(Result: `campaign_id` is now 100% valid with 0% empty values, perfectly matching `dim_campaign[campaign_id]`).*

---

### 4.4: Cleansing `cln_stores`

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `stg_stores` $\rightarrow$ select **Reference** $\rightarrow$ Rename to `cln_stores` $\rightarrow$ Move to **`04_Cleansed`**.
2. **Trim & Clean All Text Columns**:
   - Hold `Ctrl` and select `store_name_en`, `store_name_ar`, `governorate`, `area`, `store_type`, `distribution_region`.
   - Switch to **Transform** tab $\rightarrow$ click **Format** $\rightarrow$ **Trim**.
   - Click **Format** $\rightarrow$ **Clean**.
3. **Normalize Mixed Branch Names (`store_name_ar`) to Pure Unmixed Language**:
   > [!WARNING]
   > **Mixed Script Defect in Source (`store_name_ar`)**:
   > In raw `stores.csv`, the `store_name_ar` column contains an unsightly mix of Arabic prefix with Latin characters:
   > e.g. `فرع Nasr City`, `فرع Heliopolis`, `فرع Dokki`, `فرع Mohandessin`, etc.
   > Mixed scripts create BiDi (Bidirectional / RTL) visual rendering glitches in Power BI cards, tables, and slicers. A field must be **100% Arabic** or **100% English**, never mixed.

   **Standardization Options via GUI**:

   * **Option A: Pure Arabic Normalization via Custom Column (Recommended for Bilingual C-Suite Dashboards)**:
     Power Query's *Column From Examples* can fail with an error when attempting cross-lingual phonetic translations because the pattern synthesizer cannot infer Arabic vocabulary from English words. Instead, use a deterministic **Custom Column M Formula**:
     1. On the top ribbon, switch to the **Add Column** tab $\rightarrow$ click **Custom Column**.
     2. In the **Custom Column** dialog:
        - *New column name*: `store_name_ar_clean`
        - *Custom column formula*: Copy and paste the formula below:

     ```powerquery
     let
         BranchMap = [
             #"فرع Nasr City"           = "فرع مدينة نصر",
             #"فرع Heliopolis"          = "فرع مصر الجديدة",
             #"فرع Dokki"               = "فرع الدقي",
             #"فرع Mohandessin"         = "فرع المهندسين",
             #"فرع Smouha"              = "فرع سموحة",
             #"فرع Sidi Gaber"          = "فرع سيدي جابر",
             #"فرع Mansoura"            = "فرع المنصورة",
             #"فرع Talkha"              = "فرع طلخا",
             #"فرع Tanta"               = "فرع طنطا",
             #"فرع Mahalla"             = "فرع المحلة الكبرى",
             #"فرع Zagazig"             = "فرع الزقازيق",
             #"فرع 10th of Ramadan"     = "فرع العاشر من رمضان",
             #"فرع Banha"               = "فرع بنها",
             #"فرع Shubra El Kheima"    = "فرع شبرا الخيمة",
             #"فرع Damietta"            = "فرع دمياط",
             #"فرع New Damietta"        = "فرع دمياط الجديدة",
             #"فرع Damanhur"            = "فرع دمنهور",
             #"فرع Kafr El Dawwar"      = "فرع كفر الدوار",
             #"فرع Ismailia"            = "فرع الإسماعيلية",
             #"فرع Fayed"               = "فرع فايد",
             #"فرع Suez"                = "فرع السويس",
             #"فرع Ain Sokhna"          = "فرع العين السخنة",
             #"فرع Port Said"           = "فرع بورسعيد",
             #"فرع Fayoum"              = "فرع الفيوم",
             #"فرع Minya"               = "فرع المنيا",
             #"فرع Assiut"              = "فرع أسيوط",
             #"فرع Sohag"               = "فرع سوهاج",
             #"فرع Qena"                = "فرع قنا",
             #"فرع Luxor"               = "فرع الأقصر",
             #"فرع Aswan"               = "فرع أسوان",
             #"فرع Hurghada"            = "فرع الغردقة",
             #"فرع El Gouna"            = "فرع الجونة",
             #"فرع Arish"               = "فرع العريش",
             #"فرع Sharm El Sheikh"     = "فرع شرم الشيخ",
             #"فرع Dahab"               = "فرع دهب"
         ],
         RawText = Text.Trim([store_name_ar]),
         CleanText = Record.FieldOrDefault(BranchMap, RawText, RawText)
     in
         CleanText
     ```

     3. Click **OK**.
     4. Select the old mixed `store_name_ar` column $\rightarrow$ right-click $\rightarrow$ select **Remove**.
     5. Double-click the header of `store_name_ar_clean` $\rightarrow$ rename it to `store_name_ar`.
     6. Click the type icon next to `store_name_ar` $\rightarrow$ select **Text** (`ABC`).
     *(All 35 retail locations now feature 100% authentic, unmixed Arabic branch titles).*

   * **Option B: Pure English Normalization (Single-Language Alternative)**:
     If the organization chooses to eliminate Arabic and keep store labels strictly English:
     - Select `store_name_ar`.
     - On **Transform** tab $\rightarrow$ click **Replace Values**:
       - *Value To Find*: `فرع `
       - *Replace With*: *(leave empty)*
       - Click **OK**.
     - Rename column to `branch_name_en` (e.g. `Nasr City`, `Heliopolis`, `Dokki`).
     *(Result: 100% English string, zero mixed characters).*

---

### 4.5: Cleansing `cln_inventory`

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `stg_inventory` $\rightarrow$ select **Reference** $\rightarrow$ Rename to `cln_inventory` $\rightarrow$ Move to **`04_Cleansed`**.
2. **Trim Foreign Key Identifiers**:
   - Hold `Ctrl` and select `store_id` and `product_id`.
   - Switch to **Transform** tab $\rightarrow$ click **Format** $\rightarrow$ **Trim**.
3. **Extract Month Name**:
   - Select the `month` column.
   - On the top ribbon, switch to the **Transform** tab $\rightarrow$ in the **Date & Time Column** group $\rightarrow$ click the **Date** dropdown $\rightarrow$ **Month** $\rightarrow$ select **Name of Month**.
   *(Under the hood in Advanced Editor, this generates the formula)*:
   ```powerquery
   = Table.TransformColumns(Source, {{"month", each Date.MonthName(_, "en-GB"), type text}})
   ```

   > [!TIP]
   > **Architectural Tip: In-Place Transformation vs Adding a Separate Column**:
   > - **In-Place Transformation (`Date.MonthName`)**: Converts the `month` column directly into English month names (`January`, `February`, etc.), which is ideal for single-period descriptive reporting.
   > - **Downstream Multi-Year Note**: If your data spans multiple years (e.g. 2023 and 2024) and downstream queries require joining to a conformed calendar dimension via an integer key (e.g. `MonthDateKey` = `20230101` in Playbook 07), make sure the original date is either preserved in a separate column (via **Add Column** $\rightarrow$ **Date** $\rightarrow$ **Month** $\rightarrow$ **Name of Month** as `month_name`) or reconstructed during downstream modeling.

---

### 4.6: Cleansing `cln_targets`

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `stg_targets` $\rightarrow$ select **Reference** $\rightarrow$ Rename to `cln_targets` $\rightarrow$ Move to **`04_Cleansed`**.
2. **Trim Foreign Key Identifiers**:
   - Click header `store_id` $\rightarrow$ **Transform** tab $\rightarrow$ **Format** $\rightarrow$ **Trim**.
3. **Extract Month Name**:
   - Select the `target_month` column.
   - On the top ribbon, switch to the **Transform** tab $\rightarrow$ in the **Date & Time Column** group $\rightarrow$ click the **Date** dropdown $\rightarrow$ **Month** $\rightarrow$ select **Name of Month**.
   *(Under the hood in Advanced Editor, this generates the formula)*:
   ```powerquery
   = Table.TransformColumns(Source, {{"target_month", each Date.MonthName(_, "en-GB"), type text}})
   ```

   > [!TIP]
   > **Architectural Tip: In-Place Transformation vs Adding a Separate Column**:
   > - **In-Place Transformation (`Date.MonthName`)**: Converts `target_month` directly into English month names (`January`, `February`, etc.), which is ideal for single-period quota visualization.
   > - **Downstream Multi-Year Note**: If target projections span multiple calendar years and downstream models join on an integer calendar key (e.g. `TargetDateKey` = `20230101` in Playbook 07), make sure the original date is either preserved in a separate column (via **Add Column** $\rightarrow$ **Date** $\rightarrow$ **Month** $\rightarrow$ **Name of Month** as `target_month_name`) or reconstructed during downstream modeling.

---

### 4.7: Cleansing `cln_campaigns`

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `stg_campaigns` $\rightarrow$ select **Reference** $\rightarrow$ Rename to `cln_campaigns` $\rightarrow$ Move to **`04_Cleansed`**.
2. Hold `Ctrl` and select `campaign_id`, `campaign_name_en`, `campaign_name_ar`.
3. Switch to **Transform** tab $\rightarrow$ click **Format** $\rightarrow$ **Trim**, then **Format** $\rightarrow$ **Clean**.

---

### 4.8: Cleansing `cln_fx_rates`

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `stg_fx_rates` $\rightarrow$ select **Reference** $\rightarrow$ Rename to `cln_fx_rates` $\rightarrow$ Move to **`04_Cleansed`**.
2. Hold `Ctrl` and select `base_currency` and `quote_currency` $\rightarrow$ **Transform** tab $\rightarrow$ **Format** $\rightarrow$ **Trim** $\rightarrow$ **Format** $\rightarrow$ **UPPERCASE**.
3. Select `rate` $\rightarrow$ verify all daily conversion multipliers are positive decimal numbers ($> 0$).

---

## 5. Verification Checklist in Power Query GUI

After completing these GUI steps, verify your queries:

| Query Name | Expected Group | Row Count | Key Transformations Verified via GUI |
| :--- | :--- | :---: | :--- |
| `stg_customers` | `02_Staging` | $25,200$ | Baseline data types set; headers trimmed. |
| `stg_products` | `02_Staging` | $20$ | Decimal types on price and cost. |
| `stg_stores` | `02_Staging` | $35$ | Text types set on all geographic keys. |
| `stg_orders` | `02_Staging` | $502,000$ | `order_datetime` typed as Date/Time; numeric metrics typed. |
| `stg_inventory` | `02_Staging` | $8,400$ | Stock counters typed as Whole Numbers (`123`). |
| `stg_targets` | `02_Staging` | $417$ | Quota values typed as Decimal (`1.2`). |
| `stg_campaigns` | `02_Staging` | $7$ | Budget typed as Decimal (`1.2`); dates typed. |
| `stg_fx_rates` | `02_Staging` | $730$ | `rate` typed as Decimal (`1.2`); `base_currency` & `quote_currency` typed as Text. |
| `cln_customers` | `04_Cleansed` | $25,200$ | Phone normalized (`010...`), lowercase emails, clean governorates. |
| `cln_products` | `04_Cleansed` | $20$ | Currency canonicalized to `EGP`; clean whitespace. |
| `cln_orders` | `04_Cleansed` | $502,000$ | Status normalized to `Completed`, `Returned`, `Cancelled`, `Pending`; currency unified to `EGP`. |
| `cln_stores` | `04_Cleansed` | $35$ | Clean governorate and store names; `store_name_ar` normalized to pure unmixed Arabic (`فرع مدينة نصر`). |
| `cln_inventory` | `04_Cleansed` | $8,400$ | Trimmed SKU and store identifiers; month name extracted (`Date.MonthName`). |
| `cln_targets` | `04_Cleansed` | $417$ | Trimmed store key and typed monthly quota; month name extracted (`Date.MonthName`). |
| `cln_campaigns` | `04_Cleansed` | $7$ | Cleaned bilingual event names and trimmed IDs. |
| `cln_fx_rates` | `04_Cleansed` | $730$ | Uppercase currency codes (`USD`, `EUR`, `EGP`) and validated daily multipliers. |

---

## 6. Under-the-Hood Reference: Complete M Code

For developers who want to inspect the generated code in the **Advanced Editor**, the complete M script for `04_Cleansed` is maintained in:
📂 `power_query_m/04_cleansed_queries.m`

