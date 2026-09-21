// ==============================================================================
// GROUP: 05_Validated
// Purpose: Multi-rule Data Quality evaluation, valid routing, and quarantine extraction
// Load Settings:
//   vld_* queries: Enable Load = FALSE (transformed downstream into fact/dim)
//   rejected_* queries: Enable Load = TRUE (loaded to model for DQ Dashboard)
//   customer_duplicate_analysis: Enable Load = TRUE
// ==============================================================================

// ------------------------------------------------------------------------------
// QUERY: vld_orders_prep (Load: FALSE)
// ------------------------------------------------------------------------------
let
    Source = cln_orders,
    
    // 1. High-speed lookup sets
    ValidCustomerKeys = List.Buffer(cln_customers[customer_id]),
    ValidProductKeys  = List.Buffer(cln_products[product_id]),
    ValidStoreKeys    = List.Buffer(cln_stores[store_id]),
    
    // 2. Identify Duplicate Order IDs
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
    
    // 4. Concatenate DataQualityReason
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
    
    // 5. Assign Tri-State DataQualityStatus
    Add_Status = Table.AddColumn(Add_Reasons, "DataQualityStatus", each 
        if not [OrderID_Valid] or not [CustomerID_Valid] or not [ProductID_Valid] or not [StoreID_Valid] 
           or not [Quantity_Valid] or not [Price_Valid] or not [Date_Valid] then "Rejected"
        else if not [Currency_Valid] or not [Status_Valid] then "Warning"
        else "Valid",
        type text
    )
in
    Add_Status


// ------------------------------------------------------------------------------
// QUERY: vld_orders (Load: FALSE - 499,903 rows)
// ------------------------------------------------------------------------------
let
    Source = vld_orders_prep,
    FilteredValid = Table.SelectRows(Source, each [DataQualityStatus] = "Valid")
in
    FilteredValid


// ------------------------------------------------------------------------------
// QUERY: rejected_orders (Load: TRUE - 2,097 rows)
// ------------------------------------------------------------------------------
let
    Source = vld_orders_prep,
    FilteredRejected = Table.SelectRows(Source, each [DataQualityStatus] = "Rejected"),
    AddTimestamp = Table.AddColumn(FilteredRejected, "QuarantineTimestamp", each DateTime.LocalNow(), type datetime),
    AddSourceTag = Table.AddColumn(AddTimestamp, "SourceSystem", each "orders.csv", type text)
in
    AddSourceTag


// ------------------------------------------------------------------------------
// QUERY: vld_customers_prep (Load: FALSE)
// ------------------------------------------------------------------------------
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


// ------------------------------------------------------------------------------
// QUERY: vld_customers (Load: FALSE - 25,000 rows)
// ------------------------------------------------------------------------------
let
    Source = vld_customers_prep,
    // Deterministic deduplication preserves first occurrence
    Filtered = Table.Distinct(Source, {"customer_id"})
in
    Filtered


// ------------------------------------------------------------------------------
// QUERY: rejected_customers (Load: TRUE - 200 rows)
// ------------------------------------------------------------------------------
let
    Source = vld_customers_prep,
    FilteredRejected = Table.SelectRows(Source, each [DataQualityStatus] = "Rejected"),
    AddSourceTag = Table.AddColumn(FilteredRejected, "SourceSystem", each "customers.csv", type text)
in
    AddSourceTag


// ------------------------------------------------------------------------------
// QUERY: customer_duplicate_analysis (Load: TRUE - Near-Duplicate Phone/Email)
// ------------------------------------------------------------------------------
let
    Source = cln_customers,
    WithPhone = Table.SelectRows(Source, each [phone] <> null),
    GroupedPhone = Table.Group(WithPhone, {"phone"}, {
        {"CustomerCount", Table.RowCount, Int64.Type},
        {"CustomerIDs", each Text.Combine([customer_id], ", "), type text},
        {"Names", each Text.Combine([customer_name_en], ", "), type text}
    }),
    SuspectedDuplicates = Table.SelectRows(GroupedPhone, each [CustomerCount] > 1)
in
    SuspectedDuplicates


// ------------------------------------------------------------------------------
// QUERY: vld_inventory_prep (Load: FALSE)
// ------------------------------------------------------------------------------
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


// ------------------------------------------------------------------------------
// QUERY: vld_inventory (Load: FALSE - 8,300 rows)
// ------------------------------------------------------------------------------
let
    Source = vld_inventory_prep,
    FilteredValid = Table.SelectRows(Source, each [DataQualityStatus] = "Valid")
in
    FilteredValid


// ------------------------------------------------------------------------------
// QUERY: rejected_inventory (Load: TRUE - 100 rows)
// ------------------------------------------------------------------------------
let
    Source = vld_inventory_prep,
    FilteredRejected = Table.SelectRows(Source, each [DataQualityStatus] = "Rejected"),
    AddSourceTag = Table.AddColumn(FilteredRejected, "SourceSystem", each "inventory_monthly.csv", type text)
in
    AddSourceTag


// ------------------------------------------------------------------------------
// QUERY: vld_targets (Load: FALSE - 415 rows)
// ------------------------------------------------------------------------------
let
    Source = cln_targets,
    Sorted = Table.Sort(Source, {{"target_month", Order.Ascending}, {"store_id", Order.Ascending}, {"sales_target_egp", Order.Descending}}),
    Deduplicated = Table.Distinct(Sorted, {"store_id", "target_month"})
in
    Deduplicated


// ------------------------------------------------------------------------------
// QUERY: rejected_targets (Load: TRUE - 2 rows)
// ------------------------------------------------------------------------------
let
    Source = cln_targets,
    Grouped = Table.Group(Source, {"target_month", "store_id"}, {{"Count", Table.RowCount, Int64.Type}}),
    DupKeys = Table.SelectRows(Grouped, each [Count] > 1),
    MergeDups = Table.NestedJoin(Source, {"target_month", "store_id"}, DupKeys, {"target_month", "store_id"}, "Dups", JoinKind.Inner),
    DroppedColumns = Table.RemoveColumns(MergeDups, {"Dups"}),
    AddSourceTag = Table.AddColumn(DroppedColumns, "DataQualityReason", each "Duplicate Store-Month Target Record", type text)
in
    AddSourceTag
