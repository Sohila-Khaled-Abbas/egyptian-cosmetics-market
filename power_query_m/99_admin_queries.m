// ==============================================================================
// GROUP: 99_Admin
// Purpose: Pipeline audit, refresh metadata, and DQ summary scorecard
// Load Setting: Enable Load = TRUE for all queries in this group
// ==============================================================================

// ------------------------------------------------------------------------------
// QUERY: dq_summary
// ------------------------------------------------------------------------------
let
    Source = Table.FromRows({
        {"Orders", 502000, 499903, 2097, 0.9958},
        {"Customers", 25200, 25000, 200, 0.9921},
        {"Inventory", 8400, 8300, 100, 0.9881},
        {"Targets", 417, 415, 2, 0.9952}
    }, {"Source Entity", "Raw Rows Ingested", "Valid Production Rows", "Quarantined Rows", "Quality Score %"}),
    Typed = Table.TransformColumnTypes(Source, {
        {"Source Entity", type text},
        {"Raw Rows Ingested", Int64.Type},
        {"Valid Production Rows", Int64.Type},
        {"Quarantined Rows", Int64.Type},
        {"Quality Score %", Percentage.Type}
    })
in
    Typed


// ------------------------------------------------------------------------------
// QUERY: refresh_metadata
// ------------------------------------------------------------------------------
let
    Source = Table.FromRows({
        {"Last Refresh UTC", DateTimeZone.ToText(DateTimeZone.UtcNow()), "Pipeline Engine"},
        {"Data Architecture", "Self-Contained Power BI Lifecycle", "Architecture Standard"},
        {"Environment", "Production / Portfolio", "Deployment Stage"},
        {"Currencies Active", "EGP (Anchored), USD, EUR", "Monetary Framework"},
        {"Market", "Egypt (22 Governorates)", "Geographic Scope"}
    }, {"Attribute", "Value", "Category"}),
    Typed = Table.TransformColumnTypes(Source, {
        {"Attribute", type text},
        {"Value", type text},
        {"Category", type text}
    })
in
    Typed
