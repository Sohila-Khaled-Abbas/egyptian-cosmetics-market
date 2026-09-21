// ==============================================================================
// GROUP: 04_Cleansed
// Purpose: Deterministic text sanitization, whitespace removal, casing normalization
// Load Setting: Enable Load = FALSE for all queries in this group
// ==============================================================================

// ------------------------------------------------------------------------------
// QUERY: cln_customers
// ------------------------------------------------------------------------------
let
    Source = stg_customers,
    
    // 1. Text Trimming & Cleaning across string columns
    TrimmedText = Table.TransformColumns(Source, {
        {"customer_name_ar", fnCleanText, type text},
        {"customer_name_en", fnCleanText, type text},
        {"governorate", fnStandardizeGovernorate, type text},
        {"area", fnCleanText, type text},
        {"customer_segment", fnCleanText, type text}
    }),
    
    // 2. Email Normalization: lowercase and trim
    CleanedEmail = Table.TransformColumns(TrimmedText, {
        {"email", each if _ = null or Text.Trim(_) = "" then null else Text.Lower(Text.Trim(_)), type text}
    }),
    
    // 3. Phone Number Standardization: +20 prefix to domestic 010...
    CleanedPhone = Table.TransformColumns(CleanedEmail, {
        {"phone", each 
            if _ = null or Text.Trim(_) = "" then null
            else 
                let 
                    rawDigits = Text.Select(_, {"0".."9"}),
                    normalized = if Text.StartsWith(rawDigits, "20") and Text.Length(rawDigits) = 12 
                                 then "0" & Text.Range(rawDigits, 2)
                                 else rawDigits
                in 
                    normalized, 
            type text}
    })
in
    CleanedPhone


// ------------------------------------------------------------------------------
// QUERY: cln_products
// ------------------------------------------------------------------------------
let
    Source = stg_products,
    NormalizedCurrency = Table.TransformColumns(Source, {
        {"currency", fnNormalizeCurrency, type text},
        {"product_name_en", fnCleanText, type text},
        {"product_name_ar", fnCleanText, type text},
        {"brand_en", fnCleanText, type text},
        {"brand_ar", fnCleanText, type text},
        {"category", fnCleanText, type text},
        {"subcategory", fnCleanText, type text},
        {"origin", fnCleanText, type text}
    })
in
    NormalizedCurrency


// ------------------------------------------------------------------------------
// QUERY: cln_stores
// ------------------------------------------------------------------------------
let
    Source = stg_stores,
    CleanedColumns = Table.TransformColumns(Source, {
        {"store_name_en", fnCleanText, type text},
        {"store_name_ar", fnCleanText, type text},
        {"governorate", fnStandardizeGovernorate, type text},
        {"area", fnCleanText, type text},
        {"store_type", fnCleanText, type text},
        {"distribution_region", fnCleanText, type text}
    })
in
    CleanedColumns


// ------------------------------------------------------------------------------
// QUERY: cln_orders (502,000 rows)
// ------------------------------------------------------------------------------
let
    Source = stg_orders,
    NormalizedColumns = Table.TransformColumns(Source, {
        {"order_status", fnNormalizeStatus, type text},
        {"currency", fnNormalizeCurrency, type text},
        {"sales_channel_en", fnCleanText, type text},
        {"sales_channel_ar", fnCleanText, type text},
        {"payment_method_en", fnCleanText, type text},
        {"payment_method_ar", fnCleanText, type text}
    })
in
    NormalizedColumns


// ------------------------------------------------------------------------------
// QUERY: cln_inventory (8,400 rows)
// ------------------------------------------------------------------------------
let
    Source = stg_inventory,
    TrimmedKeys = Table.TransformColumns(Source, {
        {"store_id", Text.Trim, type text},
        {"product_id", Text.Trim, type text}
    })
in
    TrimmedKeys


// ------------------------------------------------------------------------------
// QUERY: cln_targets (417 rows)
// ------------------------------------------------------------------------------
let
    Source = stg_targets,
    TrimmedKeys = Table.TransformColumns(Source, {
        {"store_id", Text.Trim, type text}
    })
in
    TrimmedKeys


// ------------------------------------------------------------------------------
// QUERY: cln_campaigns (7 rows)
// ------------------------------------------------------------------------------
let
    Source = stg_campaigns,
    CleanedColumns = Table.TransformColumns(Source, {
        {"campaign_id", Text.Trim, type text},
        {"campaign_name_en", fnCleanText, type text},
        {"campaign_name_ar", fnCleanText, type text},
        {"platform", fnCleanText, type text}
    })
in
    CleanedColumns


// ------------------------------------------------------------------------------
// QUERY: cln_fx_rates (730 rows)
// ------------------------------------------------------------------------------
let
    Source = stg_fx_rates,
    CleanedCurrencies = Table.TransformColumns(Source, {
        {"base_currency", each Text.Upper(Text.Trim(_)), type text},
        {"quote_currency", each Text.Upper(Text.Trim(_)), type text}
    })
in
    CleanedCurrencies

