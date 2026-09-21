// ==============================================================================
// GROUP: 06_Transformations
// Purpose: Row-level business math, standard cost joins, date key generation
// Load Setting: Enable Load = FALSE for all queries in this group
// ==============================================================================

// ------------------------------------------------------------------------------
// QUERY: trf_sales (499,903 rows)
// ------------------------------------------------------------------------------
let
    Source = vld_orders,
    
    // Left Outer Join with cln_products to retrieve standard cost
    MergedProduct = Table.NestedJoin(
        Source, {"product_id"}, 
        cln_products, {"product_id"}, 
        "ProductRef", 
        JoinKind.LeftOuter
    ),
    ExpandedProduct = Table.ExpandTableColumn(
        MergedProduct, 
        "ProductRef", 
        {"standard_cost_egp"}, 
        {"product_standard_cost_egp"}
    ),
    
    // Compute Row-Level Financial Metrics
    Add_Gross = Table.AddColumn(ExpandedProduct, "calc_gross_sales_egp", each 
        Number.Round([quantity] * [unit_price_egp], 2), 
        Currency.Type
    ),
    Add_Discount = Table.AddColumn(Add_Gross, "calc_discount_egp", each 
        Number.Round([calc_gross_sales_egp] * [discount_pct], 2), 
        Currency.Type
    ),
    Add_Net = Table.AddColumn(Add_Discount, "calc_net_sales_egp", each 
        Number.Round([calc_gross_sales_egp] - [calc_discount_egp], 2), 
        Currency.Type
    ),
    Add_Cost = Table.AddColumn(Add_Net, "calc_cost_egp", each 
        Number.Round([quantity] * [product_standard_cost_egp], 2), 
        Currency.Type
    ),
    Add_Profit = Table.AddColumn(Add_Cost, "calc_gross_profit_egp", each 
        Number.Round([calc_net_sales_egp] - [calc_cost_egp], 2), 
        Currency.Type
    ),
    
    // Generate OrderDateKey integer for DimDate join (YYYYMMDD)
    Add_DateKey = Table.AddColumn(Add_Profit, "OrderDateKey", each 
        Date.Year(DateTime.Date([order_datetime])) * 10000 + 
        Date.Month(DateTime.Date([order_datetime])) * 100 + 
        Date.Day(DateTime.Date([order_datetime])), 
        Int64.Type
    ),
    
    // Select Fact Columns
    ProjectedColumns = Table.SelectColumns(Add_DateKey, {
        "order_id",
        "order_datetime",
        "OrderDateKey",
        "customer_id",
        "product_id",
        "store_id",
        "campaign_id",
        "sales_channel_en",
        "sales_channel_ar",
        "payment_method_en",
        "payment_method_ar",
        "order_status",
        "quantity",
        "unit_price_egp",
        "discount_pct",
        "calc_gross_sales_egp",
        "calc_discount_egp",
        "calc_net_sales_egp",
        "calc_cost_egp",
        "calc_gross_profit_egp"
    }),
    
    RenamedColumns = Table.RenameColumns(ProjectedColumns, {
        {"calc_gross_sales_egp", "gross_sales_egp"},
        {"calc_discount_egp", "discount_egp"},
        {"calc_net_sales_egp", "net_sales_egp"},
        {"calc_cost_egp", "cost_egp"},
        {"calc_gross_profit_egp", "gross_profit_egp"}
    })
in
    RenamedColumns


// ------------------------------------------------------------------------------
// QUERY: trf_inventory (8,300 rows)
// ------------------------------------------------------------------------------
let
    Source = vld_inventory,
    
    // MonthDateKey (YYYYMM01)
    Add_MonthKey = Table.AddColumn(Source, "MonthDateKey", each 
        Date.Year([month]) * 10000 + Date.Month([month]) * 100 + 1, 
        Int64.Type
    ),
    
    Add_NetChange = Table.AddColumn(Add_MonthKey, "net_stock_flow", each 
        [received_qty] - [sold_qty] - [damaged_qty], 
        Int64.Type
    ),
    
    Add_LowStockFlag = Table.AddColumn(Add_NetChange, "is_low_stock", each 
        if [closing_stock] <= 15 then 1 else 0, 
        Int64.Type
    ),
    
    Add_StockoutFlag = Table.AddColumn(Add_LowStockFlag, "is_stockout", each 
        if [closing_stock] = 0 then 1 else 0, 
        Int64.Type
    )
in
    Add_StockoutFlag


// ------------------------------------------------------------------------------
// QUERY: trf_targets (415 rows)
// ------------------------------------------------------------------------------
let
    Source = vld_targets,
    
    Add_TargetKey = Table.AddColumn(Source, "TargetDateKey", each 
        Date.Year([target_month]) * 10000 + Date.Month([target_month]) * 100 + 1, 
        Int64.Type
    )
in
    Add_TargetKey
