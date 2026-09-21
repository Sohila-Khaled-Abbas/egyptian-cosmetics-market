// ==============================================================================
// GROUP: 02_Staging
// Purpose: Baseline type enforcement and header cleaning
// Load Setting: Enable Load = FALSE for all queries in this group
// ==============================================================================

// ------------------------------------------------------------------------------
// QUERY: stg_customers
// ------------------------------------------------------------------------------
let
    Source = src_customers,
    TrimmedHeaders = Table.TransformColumnNames(Source, Text.Trim),
    TypedColumns = Table.TransformColumnTypes(TrimmedHeaders, {
        {"customer_id", type text},
        {"customer_name_ar", type text},
        {"customer_name_en", type text},
        {"gender", type text},
        {"birth_year", Int64.Type},
        {"governorate", type text},
        {"area", type text},
        {"phone", type text},
        {"email", type text},
        {"signup_date", type date},
        {"customer_segment", type text}
    }, "en-US")
in
    TypedColumns


// ------------------------------------------------------------------------------
// QUERY: stg_products
// ------------------------------------------------------------------------------
let
    Source = src_products,
    TrimmedHeaders = Table.TransformColumnNames(Source, Text.Trim),
    TypedColumns = Table.TransformColumnTypes(TrimmedHeaders, {
        {"product_id", type text},
        {"product_name_en", type text},
        {"product_name_ar", type text},
        {"brand_en", type text},
        {"brand_ar", type text},
        {"category", type text},
        {"subcategory", type text},
        {"list_price_egp", type number},
        {"standard_cost_egp", type number},
        {"currency", type text},
        {"origin", type text}
    }, "en-US")
in
    TypedColumns


// ------------------------------------------------------------------------------
// QUERY: stg_stores
// ------------------------------------------------------------------------------
let
    Source = src_stores,
    TrimmedHeaders = Table.TransformColumnNames(Source, Text.Trim),
    TypedColumns = Table.TransformColumnTypes(TrimmedHeaders, {
        {"store_id", type text},
        {"store_name_en", type text},
        {"store_name_ar", type text},
        {"governorate", type text},
        {"area", type text},
        {"store_type", type text},
        {"distribution_region", type text}
    }, "en-US")
in
    TypedColumns


// ------------------------------------------------------------------------------
// QUERY: stg_orders
// ------------------------------------------------------------------------------
let
    Source = src_orders,
    TrimmedHeaders = Table.TransformColumnNames(Source, Text.Trim),
    TypedColumns = Table.TransformColumnTypes(TrimmedHeaders, {
        {"order_id", type text},
        {"order_datetime", type datetime},
        {"customer_id", type text},
        {"product_id", type text},
        {"store_id", type text},
        {"campaign_id", type text},
        {"sales_channel_en", type text},
        {"sales_channel_ar", type text},
        {"payment_method_en", type text},
        {"payment_method_ar", type text},
        {"quantity", Int64.Type},
        {"unit_price_egp", type number},
        {"discount_pct", type number},
        {"gross_sales_egp", type number},
        {"discount_egp", type number},
        {"net_sales_egp", type number},
        {"cost_egp", type number},
        {"order_status", type text},
        {"currency", type text}
    }, "en-US")
in
    TypedColumns


// ------------------------------------------------------------------------------
// QUERY: stg_inventory
// ------------------------------------------------------------------------------
let
    Source = src_inventory,
    TrimmedHeaders = Table.TransformColumnNames(Source, Text.Trim),
    TypedColumns = Table.TransformColumnTypes(TrimmedHeaders, {
        {"month", type date},
        {"store_id", type text},
        {"product_id", type text},
        {"opening_stock", Int64.Type},
        {"received_qty", Int64.Type},
        {"sold_qty", Int64.Type},
        {"damaged_qty", Int64.Type},
        {"closing_stock", Int64.Type}
    }, "en-US")
in
    TypedColumns


// ------------------------------------------------------------------------------
// QUERY: stg_targets
// ------------------------------------------------------------------------------
let
    Source = src_targets,
    TrimmedHeaders = Table.TransformColumnNames(Source, Text.Trim),
    TypedColumns = Table.TransformColumnTypes(TrimmedHeaders, {
        {"target_month", type date},
        {"store_id", type text},
        {"sales_target_egp", type number},
        {"order_target", Int64.Type}
    }, "en-US")
in
    TypedColumns


// ------------------------------------------------------------------------------
// QUERY: stg_campaigns
// ------------------------------------------------------------------------------
let
    Source = src_campaigns,
    TrimmedHeaders = Table.TransformColumnNames(Source, Text.Trim),
    TypedColumns = Table.TransformColumnTypes(TrimmedHeaders, {
        {"campaign_id", type text},
        {"campaign_name_en", type text},
        {"campaign_name_ar", type text},
        {"platform", type text},
        {"budget_egp", type number},
        {"expected_conversion_rate", type number}
    }, "en-US")
in
    TypedColumns


// ------------------------------------------------------------------------------
// QUERY: stg_fx_rates
// ------------------------------------------------------------------------------
let
    Source = src_exchange_rates,
    TrimmedHeaders = Table.TransformColumnNames(Source, Text.Trim),
    TypedColumns = Table.TransformColumnTypes(TrimmedHeaders, {
        {"base_currency", type text},
        {"quote_currency", type text},
        {"exchange_rate", type number},
        {"rate_date_raw", Int64.Type},
        {"api_timestamp", type datetimezone}
    }, "en-US")
in
    TypedColumns
