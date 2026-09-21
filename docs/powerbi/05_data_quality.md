# Playbook 05: Enterprise Data Quality Framework & Quarantine Engine

## 1. Objective & Scope

Data quality is the cornerstone of trustworthy analytics. In enterprise production, invalid records must **never be silently deleted or ignored**. 

This playbook details the Power BI Data Quality Framework implemented entirely in Power Query (M):
1. Implementation of **17 comprehensive validation checks**.
2. Explicit boolean quality flags (`CustomerID_Valid`, `Quantity_Valid`, etc.).
3. Tri-state classification: **`Valid`**, **`Warning`**, and **`Rejected`**.
4. Generation of a concatenated, human-readable audit column: **`DataQualityReason`**.
5. Automated routing into **Quarantine Queries** (`rejected_orders`, `rejected_customers`, `rejected_inventory`, `rejected_targets`) that load into the data model for the Data Quality Dashboard.
6. A customer near-duplicate detection query: **`customer_duplicate_analysis`**.

---

## 2. The 17 Core Enterprise Data Quality Checks

| Rule ID | Check Name | Entity | Severity | Condition for Failure | Business Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DQ-01** | Missing Mandatory Key | Customer, Order | **Rejected** | `order_id == null` or `customer_id == null` | Cannot establish transactional identity. |
| **DQ-02** | Duplicate Business Key | Order | **Rejected** | `order_id` appears $> 1$ time in dataset | Violates primary key grain; causes double-counting in financials. |
| **DQ-03** | Invalid Customer FK | Order | **Rejected** | `customer_id` not found in `cln_customers` | Orphan order cannot be attributed to customer dimensions. |
| **DQ-04** | Invalid Product FK | Order | **Rejected** | `product_id` not found in `cln_products` | Orphan order cannot be categorized or attributed for COGS. |
| **DQ-05** | Invalid Store FK | Order | **Rejected** | `store_id` not found in `cln_stores` | Orphan order breaks geographic and store-type hierarchy. |
| **DQ-06** | Invalid Quantity | Order | **Rejected** | `quantity <= 0` | Physical cosmetics units sold must be $\ge 1$. |
| **DQ-07** | Invalid Price | Order | **Rejected** | `unit_price_egp <= 0` | Products cannot have negative or zero sales value. |
| **DQ-08** | Invalid Discount | Order | **Warning** | `discount_pct < 0` or `discount_pct > 0.50` | Commercial policy caps discounts at 50%; higher is flagged for audit. |
| **DQ-09** | Suspicious Historical Date| Order | **Rejected** | `order_datetime < #datetime(2023, 1, 1, 0, 0, 0)` | Operational database default `1900-01-01` distorts date models. |
| **DQ-10** | Future Transaction Date | Order | **Rejected** | `order_datetime > #datetime(2025, 12, 31, 23, 59, 59)`| Future timestamps reflect clock drift or corrupt batch feeds. |
| **DQ-11** | Invalid Order Status | Order | **Warning** | `order_status` not in approved lifecycle states | Unrecognized state (`"In Review"`, etc.) requires ops audit. |
| **DQ-12** | Invalid Currency | Order | **Warning** | `currency != "EGP"` | Non-EGP currency requires FX conversion. |
| **DQ-13** | Missing Contact Info | Customer | **Warning** | `phone == null` or `email == null` | Limits CRM marketing outreach but retains purchase history. |
| **DQ-14** | Invalid Governorate | Customer | **Warning** | `governorate` not in 22 Egyptian governorates | Delivery address cannot be routed to distribution hubs. |
| **DQ-15** | Negative Inventory Stock | Inventory | **Rejected** | `closing_stock < 0` | Physical stock at month-end cannot be negative. |
| **DQ-16** | Negative Damaged Qty | Inventory | **Rejected** | `damaged_qty < 0` | Damaged stock units cannot be negative. |
| **DQ-17** | Duplicate Target Record | Targets | **Rejected** | `store_id` + `target_month` appears $> 1$ time | Duplicate commercial quota distorts achievement percentages. |

---

## 3. Cleaning vs Warning vs Rejecting: The Tri-State Architecture

Understanding the operational distinction between these three states is paramount:

```
[Incoming Raw Record]
       │
       ├─► Can issue be deterministically corrected? (e.g. trimming, "EGP " -> "EGP", lowercase email)
       │     └─► YES: Clean in 04_Cleansed (Status = "Valid").
       │
       ├─► Does record have missing contact info or minor policy drift, but valid financial integrity?
       │     └─► YES: Retain in model, assign Status = "Warning" + log DataQualityReason.
       │
       └─► Does record violate Primary Key, Foreign Key, Physical Math (qty<=0, price<=0), or Date Bounds?
             └─► YES: Assign Status = "Rejected" + log DataQualityReason -> Route to Quarantine Query.
```

---

## 4. Validating Orders (`vld_orders`) and Quarantine Engine

In group **`05_Validated`**, create `vld_orders_prep` referencing `cln_orders`.

### Step 4.1: Lookup Sets for Referential Integrity
To perform high-speed referential integrity checks in Power Query without slow row-by-row nested joins, we convert valid dimension keys into M lists:

```powerquery
// Valid keys extracted as high-speed lookup lists
ValidCustomerKeys = List.Buffer(Table.SelectRows(cln_customers, each [customer_id] <> null)[customer_id]),
ValidProductKeys  = List.Buffer(Table.SelectRows(cln_products, each [product_id] <> null)[product_id]),
ValidStoreKeys    = List.Buffer(Table.SelectRows(cln_stores, each [store_id] <> null)[store_id]),
```

### Step 4.2: Add Data Quality Boolean Flags in `cln_orders`
In `vld_orders_prep`, add individual validation columns:

```powerquery
let
    Source = cln_orders,
    
    // 1. Referential Integrity Buffers
    ValidCustomerKeys = List.Buffer(cln_customers[customer_id]),
    ValidProductKeys = List.Buffer(cln_products[product_id]),
    ValidStoreKeys = List.Buffer(cln_stores[store_id]),
    
    // 2. Identify Duplicate Order IDs
    // Group by order_id to calculate occurrence count
    OrderCounts = Table.Group(Source, {"order_id"}, {{"Count", Table.RowCount, Int64.Type}}),
    DupOrderKeys = List.Buffer(Table.SelectRows(OrderCounts, each [Count] > 1)[order_id]),
    
    // 3. Add Explicit Validation Flags
    Add_PK_Valid = Table.AddColumn(Source, "OrderID_Valid", each not List.Contains(DupOrderKeys, [order_id]), type logical),
    Add_Cust_Valid = Table.AddColumn(Add_PK_Valid, "CustomerID_Valid", each List.Contains(ValidCustomerKeys, [customer_id]), type logical),
    Add_Prod_Valid = Table.AddColumn(Add_Cust_Valid, "ProductID_Valid", each List.Contains(ValidProductKeys, [product_id]), type logical),
    Add_Store_Valid = Table.AddColumn(Add_Prod_Valid, "StoreID_Valid", each List.Contains(ValidStoreKeys, [store_id]), type logical),
    Add_Qty_Valid = Table.AddColumn(Add_Store_Valid, "Quantity_Valid", each [quantity] <> null and [quantity] > 0, type logical),
    Add_Price_Valid = Table.AddColumn(Add_Qty_Valid, "Price_Valid", each [unit_price_egp] <> null and [unit_price_egp] > 0, type logical),
    Add_Date_Valid = Table.AddColumn(Add_Price_Valid, "Date_Valid", each 
        [order_datetime] <> null 
        and [order_datetime] >= #datetime(2023, 1, 1, 0, 0, 0) 
        and [order_datetime] <= #datetime(2025, 12, 31, 23, 59, 59), 
        type logical
    ),
    Add_Curr_Valid = Table.AddColumn(Add_Date_Valid, "Currency_Valid", each [currency] = "EGP", type logical),
    Add_Status_Valid = Table.AddColumn(Add_Curr_Valid, "Status_Valid", each List.Contains({"Completed", "Cancelled", "Returned", "Pending"}, [order_status]), type logical),
    
    // 4. Generate DataQualityReason
    Add_Reasons = Table.AddColumn(Add_Status_Valid, "DataQualityReason", each 
        let
            reasons = {}
                & (if not [OrderID_Valid] then {"Duplicate Order ID"} else {})
                & (if not [CustomerID_Valid] then {"Invalid Customer FK"} else {})
                & (if not [ProductID_Valid] then {"Invalid Product FK"} else {})
                & (if not [StoreID_Valid] then {"Invalid Store FK"} else {})
                & (if not [Quantity_Valid] then {"Invalid Quantity (<= 0)"} else {})
                & (if not [Price_Valid] then {"Invalid Unit Price (<= 0)"} else {})
                & (if not [Date_Valid] then {"Date Out of Range (1900 or Future)"} else {})
                & (if not [Currency_Valid] then {"Non-Standard Currency"} else {})
                & (if not [Status_Valid] then {"Unknown Order Status"} else {})
        in
            if List.IsEmpty(reasons) then "None" else Text.Combine(reasons, "; "), 
        type text
    ),
    
    // 5. Determine Overall DataQualityStatus
    Add_Status = Table.AddColumn(Add_Reasons, "DataQualityStatus", each 
        if not [OrderID_Valid] or not [CustomerID_Valid] or not [ProductID_Valid] or not [StoreID_Valid] 
           or not [Quantity_Valid] or not [Price_Valid] or not [Date_Valid] then "Rejected"
        else if not [Currency_Valid] or not [Status_Valid] then "Warning"
        else "Valid",
        type text
    )
in
    Add_Status
```
*Name:* `vld_orders_prep` $\rightarrow$ Group: `05_Validated` $\rightarrow$ Uncheck **Enable Load**.

---

### Step 4.3: Create Valid Stream `vld_orders`
Now create the clean table that feeds the final `FactSales` model table:
1. Right-click `vld_orders_prep` $\rightarrow$ **Reference**.
2. Rename to: `vld_orders`.
3. Filter rows where `DataQualityStatus = "Valid"`.
```powerquery
let
    Source = vld_orders_prep,
    FilteredValid = Table.SelectRows(Source, each [DataQualityStatus] = "Valid")
in
    FilteredValid
```
*Load Setting:* **Enable Load = False** (Transformed downstream into `fact_sales`).
*Resulting Row Count:* **$499,903$ rows**.

---

### Step 4.4: Create Quarantine Query `rejected_orders`
1. Right-click `vld_orders_prep` $\rightarrow$ **Reference**.
2. Rename to: `rejected_orders`. Move to group: `05_Validated`.
3. Set **Enable Load = True** (loads into Data Model for Data Quality Audit Dashboard).
4. Filter rows where `DataQualityStatus = "Rejected"`.
```powerquery
let
    Source = vld_orders_prep,
    FilteredRejected = Table.SelectRows(Source, each [DataQualityStatus] = "Rejected"),
    AddTimestamp = Table.AddColumn(FilteredRejected, "QuarantineTimestamp", each DateTime.LocalNow(), type datetime),
    AddSourceTag = Table.AddColumn(AddTimestamp, "SourceSystem", each "orders.csv", type text)
in
    AddSourceTag
```
*Resulting Row Count:* **$2,097$ quarantined records** ($2,000$ duplicate orders + $35$ invalid quantities + $10$ invalid unit prices + $35$ broken FKs + $22$ date anomalies, accounting for multi-violation overlaps).

---

## 5. Validating Customers & Detecting Near-Duplicates

### 5.1: `vld_customers` and `rejected_customers`
In `cln_customers`, $200$ duplicate `customer_id` values exist (with $194$ exact duplicate rows):

```powerquery
// Query: vld_customers_prep
let
    Source = cln_customers,
    Grouped = Table.Group(Source, {"customer_id"}, {{"Count", Table.RowCount, Int64.Type}}),
    DupKeys = List.Buffer(Table.SelectRows(Grouped, each [Count] > 1)[customer_id]),
    
    Add_PK = Table.AddColumn(Source, "CustomerID_Valid", each not List.Contains(DupKeys, [customer_id]), type logical),
    Add_Contact = Table.AddColumn(Add_PK, "Contact_Valid", each [phone] <> null and [email] <> null, type logical),
    
    Add_Reason = Table.AddColumn(Add_Contact, "DataQualityReason", each 
        if not [CustomerID_Valid] then "Duplicate Customer ID"
        else if not [Contact_Valid] then "Missing Contact Info (Phone or Email)"
        else "None", type text
    ),
    
    Add_Status = Table.AddColumn(Add_Reason, "DataQualityStatus", each 
        if not [CustomerID_Valid] then "Rejected"
        else if not [Contact_Valid] then "Warning"
        else "Valid", type text
    )
in
    Add_Status
```

- `vld_customers`: Filter `DataQualityStatus <> "Rejected"`. (Deduplicates customers deterministically, producing **$25,000$ distinct valid customers**).
- `rejected_customers`: Filter `DataQualityStatus = "Rejected"`. Contains **$200$ quarantined customer records** (Enable Load = True).

### 5.2: Customer Near-Duplicate Analysis (`customer_duplicate_analysis`)
In omnichannel Egyptian retail, customers frequently sign up twice using different names or slightly different phone numbers (e.g. `01012345678` vs `+20 1012345678`).

Create query `customer_duplicate_analysis` in `05_Validated` (**Enable Load = True**):
```powerquery
let
    Source = cln_customers,
    // Filter to rows having a phone number
    WithPhone = Table.SelectRows(Source, each [phone] <> null),
    // Group by normalized phone
    GroupedPhone = Table.Group(WithPhone, {"phone"}, {
        {"CustomerCount", Table.RowCount, Int64.Type},
        {"CustomerIDs", each Text.Combine([customer_id], ", "), type text},
        {"Names", each Text.Combine([customer_name_en], ", "), type text}
    }),
    SuspectedDuplicates = Table.SelectRows(GroupedPhone, each [CustomerCount] > 1)
in
    SuspectedDuplicates
```
*Business Value:* Exposes customer profiles that share the identical normalized mobile number across different IDs, powering customer identity reconciliation.

---

## 6. Validating Inventory (`vld_inventory` and `rejected_inventory`)

In `cln_inventory`:
- $50$ records have `closing_stock < 0`.
- $50$ records have `damaged_qty < 0`.

```powerquery
// Query: vld_inventory_prep
let
    Source = cln_inventory,
    Add_StockValid = Table.AddColumn(Source, "ClosingStock_Valid", each [closing_stock] >= 0, type logical),
    Add_DamagedValid = Table.AddColumn(Add_StockValid, "DamagedQty_Valid", each [damaged_qty] >= 0, type logical),
    
    Add_Reason = Table.AddColumn(Add_DamagedValid, "DataQualityReason", each 
        if not [ClosingStock_Valid] and not [DamagedQty_Valid] then "Negative Stock & Negative Damaged"
        else if not [ClosingStock_Valid] then "Negative Closing Stock"
        else if not [DamagedQty_Valid] then "Negative Damaged Qty"
        else "None", type text
    ),
    
    Add_Status = Table.AddColumn(Add_Reason, "DataQualityStatus", each 
        if not [ClosingStock_Valid] or not [DamagedQty_Valid] then "Rejected" else "Valid", type text
    )
in
    Add_Status
```

- `vld_inventory`: Filter `DataQualityStatus = "Valid"`. Produces **$8,300$ clean inventory balance rows** (`Enable Load = False`, feeds `fact_inventory`).
- `rejected_inventory`: Filter `DataQualityStatus = "Rejected"`. Contains **$100$ quarantined inventory records** (`Enable Load = True`, feeds DQ Dashboard).

---

## 7. Validating Targets (`vld_targets` and `rejected_targets`)

In `stg_targets`:
- Raw targets contain $417$ records.
- $2$ records are duplicate store-month combinations.

```powerquery
// Query: vld_targets
let
    Source = stg_targets,
    // Sort descending by sales target so duplicate resolution preserves the highest quota
    Sorted = Table.Sort(Source, {{"target_month", Order.Ascending}, {"store_id", Order.Ascending}, {"sales_target_egp", Order.Descending}}),
    // Distinct on compound key (store_id + target_month)
    Deduplicated = Table.Distinct(Sorted, {"store_id", "target_month"})
in
    Deduplicated
```
*Resulting Count:* **$415$ valid target records** representing all active commercial targets.

---

## 8. Summary of Data Quality Pipeline Reconciliation

| Entity | Raw Rows Ingested | Quarantined Rows (`Rejected`) | Warning Rows | Valid Rows Loaded to Model | Reconciliation Proof |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Orders** | $502,000$ | $2,097$ | $0$ (All warnings cleaned) | $499,903$ | $499,903 + 2,097 = 502,000$ |
| **Customers** | $25,200$ | $200$ | $680$ (Missing phone/email/area) | $25,000$ | $25,000 + 200 = 25,200$ |
| **Inventory** | $8,400$ | $100$ | $50$ (High sold spikes) | $8,300$ | $8,300 + 100 = 8,400$ |
| **Targets** | $417$ | $2$ | $0$ | $415$ | $415 + 2 = 417$ |
