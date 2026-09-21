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
   - Select the `order_status` column.
   - On the **Transform** tab $\rightarrow$ click **Format** $\rightarrow$ select **Capitalize Each Word**.
   - Click **Replace Values**:
     - *Value To Find*: `مكتمل`
     - *Replace With*: `Completed`
     - Click **OK**.
   - Click **Replace Values** again:
     - *Value To Find*: `مرتجع`
     - *Replace With*: `Returned`
     - Click **OK**.
   - Click **Replace Values** again:
     - *Value To Find*: `ملغي`
     - *Replace With*: `Cancelled`
     - Click **OK**.
4. **Normalize Currency**:
   - Select `currency` column $\rightarrow$ **Transform** tab $\rightarrow$ **Replace Values** $\rightarrow$ replace `EGP ` and `جنيه` with `EGP`.

---

### 4.4: Cleansing `cln_stores`

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `stg_stores` $\rightarrow$ select **Reference** $\rightarrow$ Rename to `cln_stores` $\rightarrow$ Move to **`04_Cleansed`**.
2. Hold `Ctrl` and select `store_name_en`, `store_name_ar`, `governorate`, `area`, `store_type`, `distribution_region`.
3. Switch to **Transform** tab $\rightarrow$ click **Format** $\rightarrow$ **Trim**, then **Format** $\rightarrow$ **Clean**.

---

### 4.5: Cleansing `cln_inventory`

#### 🖱️ Step-by-Step GUI Actions:
1. Right-click `stg_inventory` $\rightarrow$ select **Reference** $\rightarrow$ Rename to `cln_inventory` $\rightarrow$ Move to **`04_Cleansed`**.
2. Hold `Ctrl` and select `store_id` and `product_id`.
3. Switch to **Transform** tab $\rightarrow$ click **Format** $\rightarrow$ **Trim**.

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
| `cln_customers` | `04_Cleansed` | $25,200$ | Phone normalized (`010...`), lowercase emails, clean governorates. |
| `cln_products` | `04_Cleansed` | $20$ | Currency canonicalized to `EGP`; clean whitespace. |
| `cln_orders` | `04_Cleansed` | $502,000$ | Status normalized to `Completed`, `Returned`, `Cancelled`. |
| `cln_stores` | `04_Cleansed` | $35$ | Clean governorate and store names. |
| `cln_inventory` | `04_Cleansed` | $8,400$ | Trimmed SKU and store identifiers. |

---

## 6. Under-the-Hood Reference: Complete M Code

For developers who want to inspect the generated code in the **Advanced Editor**, the complete M script for `04_Cleansed` is maintained in:
📂 `power_query_m/04_cleansed_queries.m`
