// ==============================================================================
// GROUP: 07_Model
// Purpose: Enterprise Galaxy & Snowflake Schema Dimensional Model for VertiPaq
// Architecture: Fact Constellation (Sales, Inventory, Targets) + Snowflaked Hierarchies
// Load Setting: Enable Load = TRUE for all queries in this group
// ==============================================================================

// ==============================================================================
// 1. SNOWFLAKE HIERARCHIES & ENRICHED REFERENCE DIMENSIONS
// ==============================================================================

// ------------------------------------------------------------------------------
// QUERY: dim_geography (22 Egyptian Governorates + National Hierarchy)
// Snowflake Dimension: Normalizes Geographic hierarchy for dim_store and dim_customer
// ------------------------------------------------------------------------------
let
    Source = ref_governorates,
    // Ensure uniqueness at Governorate level
    Deduplicated = Table.Distinct(Source, {"governorate_en"}),
    Sorted = Table.Sort(Deduplicated, {{"governorate_en", Order.Ascending}}),
    AddKey = Table.AddIndexColumn(Sorted, "GeographyKey", 1, 1, Int64.Type),

    // Add Economic Region Hierarchy (AR & EN)
    Add_RegionEN = Table.AddColumn(AddKey, "Economic Region EN", each 
        let g = [governorate_en] in
        if List.Contains({"Cairo", "Giza", "Qalyubia"}, g) then "Greater Cairo"
        else if List.Contains({"Alexandria", "Beheira", "Matrouh"}, g) then "Alexandria & West Coast"
        else if List.Contains({"Dakahlia", "Gharbia", "Monufia", "Kafr El Sheikh", "Damietta", "Sharqia"}, g) then "Nile Delta"
        else if List.Contains({"Port Said", "Ismailia", "Suez"}, g) then "Canal Zone"
        else if List.Contains({"Fayoum", "Beni Suef", "Minya", "Asyut", "Sohag", "Qena", "Luxor", "Aswan"}, g) then "Upper Egypt"
        else if List.Contains({"Red Sea", "South Sinai", "North Sinai", "New Valley"}, g) then "Frontier & Sinai"
        else "Other Egypt",
        type text
    ),
    Add_RegionAR = Table.AddColumn(Add_RegionEN, "Economic Region AR", each 
        let r = [Economic Region EN] in
        if r = "Greater Cairo" then "القاهرة الكبرى"
        else if r = "Alexandria & West Coast" then "الإسكندرية والساحل الشمالي"
        else if r = "Nile Delta" then "دلتا النيل"
        else if r = "Canal Zone" then "مدن القناة"
        else if r = "Upper Egypt" then "صعيد مصر"
        else if r = "Frontier & Sinai" then "المحافظات الحدودية وسيناء"
        else "محافظات أخرى",
        type text
    ),

    // Add Market Development Tier (Metropolitan Tier 1 vs Regional Tier 2 vs Frontier Tier 3)
    Add_MarketTier = Table.AddColumn(Add_RegionAR, "Market Tier", each 
        let g = [governorate_en] in
        if List.Contains({"Cairo", "Giza", "Alexandria"}, g) then "Tier 1 - Metropolitan Hub"
        else if List.Contains({"Dakahlia", "Gharbia", "Sharqia", "Qalyubia", "Port Said", "Suez", "Asyut", "Luxor"}, g) then "Tier 2 - Secondary Urban"
        else "Tier 3 - Regional Frontier",
        type text
    ),

    // Add Logistics Delivery SLA & Shipping Zone
    Add_ShippingZone = Table.AddColumn(Add_MarketTier, "Logistics Shipping Zone", each 
        let tier = [Market Tier] in
        if Text.StartsWith(tier, "Tier 1") then "Zone 1 (Same-Day / 24h)"
        else if Text.StartsWith(tier, "Tier 2") then "Zone 2 (24h - 48h Delivery)"
        else "Zone 3 (48h - 72h Extended)",
        type text
    ),
    Add_CourierSLA = Table.AddColumn(Add_ShippingZone, "Courier SLA Days", each 
        let tier = [Market Tier] in
        if Text.StartsWith(tier, "Tier 1") then 1
        else if Text.StartsWith(tier, "Tier 2") then 2
        else 3,
        Int64.Type
    ),
    Add_CourierCost = Table.AddColumn(Add_CourierSLA, "Standard Courier Cost EGP", each 
        let tier = [Market Tier] in
        if Text.StartsWith(tier, "Tier 1") then 35.00
        else if Text.StartsWith(tier, "Tier 2") then 50.00
        else 75.00,
        type number
    ),

    Renamed = Table.RenameColumns(Add_CourierCost, {
        {"governorate_en", "Governorate EN"},
        {"governorate_ar", "Governorate AR"},
        {"region_en", "Distribution Region EN"},
        {"region_ar", "Distribution Region AR"}
    }),
    Projected = Table.SelectColumns(Renamed, {
        "GeographyKey", "Governorate EN", "Governorate AR", 
        "Economic Region EN", "Economic Region AR", "Distribution Region EN", "Distribution Region AR",
        "Market Tier", "Logistics Shipping Zone", "Courier SLA Days", "Standard Courier Cost EGP"
    })
in
    Projected


// ------------------------------------------------------------------------------
// QUERY: dim_category (Snowflake Hierarchy Level 1: Product Category)
// Normalizes category metadata and strategic margins
// ------------------------------------------------------------------------------
let
    Source = cln_products,
    Categories = Table.SelectColumns(Source, {"category"}),
    Deduplicated = Table.Distinct(Categories),
    Sorted = Table.Sort(Deduplicated, {{"category", Order.Ascending}}),
    AddKey = Table.AddIndexColumn(Sorted, "CategoryKey", 1, 1, Int64.Type),

    Add_CategoryAR = Table.AddColumn(AddKey, "Category AR", each 
        let c = [category] in
        if c = "Skincare" then "العناية بالبشرة"
        else if c = "Haircare" then "العناية بالشعر"
        else if c = "Makeup" then "المكياج ومستحضرات التجميل"
        else if c = "Fragrance" then "العطور"
        else if c = "Bath & Body" then "العناية بالجسم والاستحمام"
        else c,
        type text
    ),
    Add_MarginClass = Table.AddColumn(Add_CategoryAR, "Strategic Margin Tier", each 
        let c = [category] in
        if c = "Fragrance" or c = "Skincare" then "High Margin Premium (>45%)"
        else if c = "Makeup" then "Core Volume Masstige (35-45%)"
        else "Volume Driver Essential (<35%)",
        type text
    ),
    Add_CategoryLead = Table.AddColumn(Add_MarginClass, "Commercial Category Lead", each 
        let c = [category] in
        if c = "Skincare" then "Dr. Mariam Farouk"
        else if c = "Haircare" then "Eng. Ahmed Tarek"
        else if c = "Makeup" then "Salma Abdelrahman"
        else if c = "Fragrance" then "Karim El-Sayed"
        else "Hoda Mostafa",
        type text
    ),
    Renamed = Table.RenameColumns(Add_CategoryLead, {{"category", "Category EN"}})
in
    Renamed


// ------------------------------------------------------------------------------
// QUERY: dim_subcategory (Snowflake Hierarchy Level 2: Product Subcategory)
// Links dim_product (FK: SubcategoryKey) to dim_category (FK: CategoryKey)
// ------------------------------------------------------------------------------
let
    Source = cln_products,
    Subcategories = Table.SelectColumns(Source, {"category", "subcategory"}),
    Deduplicated = Table.Distinct(Subcategories),
    Sorted = Table.Sort(Deduplicated, {{"category", Order.Ascending}, {"subcategory", Order.Ascending}}),
    AddKey = Table.AddIndexColumn(Sorted, "SubcategoryKey", 1, 1, Int64.Type),

    // Merge with dim_category to retrieve CategoryKey
    MergeCategory = Table.NestedJoin(AddKey, {"category"}, dim_category, {"Category EN"}, "CatDim", JoinKind.Inner),
    ExpandCategory = Table.ExpandTableColumn(MergeCategory, "CatDim", {"CategoryKey"}, {"CategoryKey"}),

    Add_SubcategoryAR = Table.AddColumn(ExpandCategory, "Subcategory AR", each 
        let s = [subcategory] in
        if s = "Moisturizer" then "مرطبات البشرة"
        else if s = "Serum" then "سيروم علاجي"
        else if s = "Cleanser" then "غسول ومنظف"
        else if s = "Sunscreen" then "واقي شمس"
        else if s = "Shampoo" then "شامبو مغذي"
        else if s = "Conditioner" then "بلسم شعر"
        else if s = "Hair Mask" then "ماسك ترميم الشعر"
        else if s = "Hair Oil" then "زيوت وسيروم الشعر"
        else if s = "Foundation" then "كريم أساس"
        else if s = "Lipstick" then "أحمر شفاه"
        else if s = "Mascara" then "ماسكارا"
        else if s = "Eyeshadow" then "ظلال عيون"
        else if s = "Eau de Parfum" then "ماء عطر مركز"
        else if s = "Body Mist" then "معطر رذاذ للجسم"
        else if s = "Body Wash" then "غسول الجسم والشاور"
        else if s = "Body Scrub" then "مقشر الجسم"
        else s,
        type text
    ),
    Add_FormType = Table.AddColumn(Add_SubcategoryAR, "Formulation Type", each 
        let s = [subcategory] in
        if List.Contains({"Serum", "Hair Oil"}, s) then "Oil & Active Serum"
        else if List.Contains({"Moisturizer", "Conditioner", "Hair Mask", "Foundation"}, s) then "Emulsion & Cream"
        else if List.Contains({"Cleanser", "Shampoo", "Body Wash"}, s) then "Foaming Surfactant"
        else if List.Contains({"Sunscreen", "Body Mist", "Eau de Parfum"}, s) then "Fluid & Spray"
        else "Solid / Pigment",
        type text
    ),
    Renamed = Table.RenameColumns(Add_FormType, {{"subcategory", "Subcategory EN"}}),
    Projected = Table.SelectColumns(Renamed, {"SubcategoryKey", "CategoryKey", "Subcategory EN", "Subcategory AR", "Formulation Type"})
in
    Projected


// ==============================================================================
// 2. CONFORMED CORE DIMENSIONS (ENRICHED)
// ==============================================================================

// ------------------------------------------------------------------------------
// QUERY: dim_date (1,096 days: 2024-01-01 to 2026-12-31)
// Conformed across FactSales, FactInventory, and FactTargets
// ------------------------------------------------------------------------------
let
    StartDate = pStartDate,
    EndDate = pEndDate,
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    
    DateList = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    TableFromList = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}, null, ExtraValues.Error),
    ChangedType = Table.TransformColumnTypes(TableFromList, {{"Date", type date}}),
    
    Add_DateKey = Table.AddColumn(ChangedType, "DateKey", each 
        Date.Year([Date]) * 10000 + Date.Month([Date]) * 100 + Date.Day([Date]), 
        Int64.Type
    ),
    Add_Year = Table.AddColumn(Add_DateKey, "Year", each Date.Year([Date]), Int64.Type),
    Add_MonthNum = Table.AddColumn(Add_Year, "Month Number", each Date.Month([Date]), Int64.Type),
    Add_MonthName = Table.AddColumn(Add_MonthNum, "Month Name", each Date.MonthName([Date], "en-US"), type text),
    Add_MonthShort = Table.AddColumn(Add_MonthName, "Month Short Name", each Text.Start([Month Name], 3), type text),
    Add_MonthAR = Table.AddColumn(Add_MonthShort, "Month Name AR", each Date.MonthName([Date], "ar-EG"), type text),
    Add_Quarter = Table.AddColumn(Add_MonthAR, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    Add_YearMonth = Table.AddColumn(Add_Quarter, "Year Month", each 
        Text.From([Year]) & "-" & Text.PadStart(Text.From([Month Number]), 2, "0"), 
        type text
    ),
    Add_YearMonthNum = Table.AddColumn(Add_YearMonth, "Year Month Number", each 
        [Year] * 100 + [Month Number], 
        Int64.Type
    ),
    Add_WeekNum = Table.AddColumn(Add_YearMonthNum, "Week Number", each Date.WeekOfYear([Date]), Int64.Type),
    Add_Day = Table.AddColumn(Add_WeekNum, "Day", each Date.Day([Date]), Int64.Type),
    Add_DayName = Table.AddColumn(Add_Day, "Day Name", each Date.DayOfWeekName([Date], "en-US"), type text),
    Add_DayNameAR = Table.AddColumn(Add_DayName, "Day Name AR", each Date.DayOfWeekName([Date], "ar-EG"), type text),
    Add_IsWeekend = Table.AddColumn(Add_DayNameAR, "Is Weekend", each 
        if Date.DayOfWeek([Date], Day.Friday) <= 1 then true else false, 
        type logical
    ), // Weekend in Egypt: Friday (0) and Saturday (1)
    Add_FiscalHalf = Table.AddColumn(Add_IsWeekend, "Fiscal Half", each 
        if [Month Number] <= 6 then "H1" else "H2", 
        type text
    )
in
    Add_FiscalHalf


// ------------------------------------------------------------------------------
// QUERY: dim_customer (25,000 rows, Enriched with Egyptian Demographics & Telecom)
// Links to dim_geography via GeographyKey
// ------------------------------------------------------------------------------
let
    Source = vld_customers,
    Deduplicated = Table.Distinct(Source, {"customer_id"}),
    Sorted = Table.Sort(Deduplicated, {{"customer_id", Order.Ascending}}),
    AddKey = Table.AddIndexColumn(Sorted, "CustomerKey", 1, 1, Int64.Type),

    // Merge GeographyKey from dim_geography
    MergeGeo = Table.NestedJoin(AddKey, {"governorate"}, dim_geography, {"Governorate EN"}, "GeoDim", JoinKind.LeftOuter),
    ExpandGeo = Table.ExpandTableColumn(MergeGeo, "GeoDim", {"GeographyKey"}, {"GeographyKey"}),
    DefaultGeo = Table.ReplaceValue(ExpandGeo, null, 1, Replacer.ReplaceValue, {"GeographyKey"}),

    // Data Enrichment 1: Egyptian Telecom Carrier Provider Detection
    Add_Carrier = Table.AddColumn(DefaultGeo, "Egyptian Telecom Carrier", each 
        let 
            phoneClean = Text.Select(Text.From([phone] ?? ""), {"0".."9"}),
            prefix = Text.Start(phoneClean, 3)
        in
            if prefix = "010" then "Vodafone Egypt"
            else if prefix = "011" then "Etisalat Misr (e&)"
            else if prefix = "012" then "Orange Egypt"
            else if prefix = "015" then "Telecom Egypt (WE)"
            else "Other / Landline",
        type text
    ),

    // Data Enrichment 2: Demographic Age & Generational Cohort
    Add_Age = Table.AddColumn(Add_Carrier, "Age", each 
        if [birth_year] = null then 32 else 2026 - [birth_year], 
        Int64.Type
    ),
    Add_AgeCohort = Table.AddColumn(Add_Age, "Age Cohort", each 
        let a = [Age] in
        if a < 25 then "18-24 (Gen Z)"
        else if a <= 34 then "25-34 (Young Professional)"
        else if a <= 49 then "35-49 (Prime Family)"
        else "50+ (Mature Consumer)",
        type text
    ),

    // Data Enrichment 3: Customer Value Lifecycle Status
    Add_Lifecycle = Table.AddColumn(Add_AgeCohort, "Lifecycle Tier", each 
        let s = [customer_segment] in
        if s = "VIP" then "VIP Platinum"
        else if s = "Loyal" then "Gold Enthusiast"
        else if s = "Occasional" then "Silver Active"
        else "Bronze Starter",
        type text
    ),

    Projected = Table.SelectColumns(Add_Lifecycle, {
        "CustomerKey", "GeographyKey", "customer_id", 
        "customer_name_ar", "customer_name_en", "gender", 
        "Age", "Age Cohort", "Egyptian Telecom Carrier", "phone", "email", 
        "signup_date", "customer_segment", "Lifecycle Tier"
    }),

    Renamed = Table.RenameColumns(Projected, {
        {"customer_name_ar", "Customer Name AR"},
        {"customer_name_en", "Customer Name EN"},
        {"customer_segment", "Original Segment"},
        {"signup_date", "Signup Date"}
    })
in
    Renamed


// ------------------------------------------------------------------------------
// QUERY: dim_product (20 SKUs, Enriched with Egyptian Market Pricing & Formulation)
// Links to dim_subcategory via SubcategoryKey (Snowflake Hierarchy)
// ------------------------------------------------------------------------------
let
    Source = cln_products,
    Deduplicated = Table.Distinct(Source, {"product_id"}),
    Sorted = Table.Sort(Deduplicated, {{"product_id", Order.Ascending}}),
    AddKey = Table.AddIndexColumn(Sorted, "ProductKey", 1, 1, Int64.Type),

    // Merge SubcategoryKey from dim_subcategory
    MergeSubcat = Table.NestedJoin(AddKey, {"subcategory"}, dim_subcategory, {"Subcategory EN"}, "SubcatDim", JoinKind.LeftOuter),
    ExpandSubcat = Table.ExpandTableColumn(MergeSubcat, "SubcatDim", {"SubcategoryKey"}, {"SubcategoryKey"}),

    // Data Enrichment 1: Egyptian Retail Market Segment (Price Tiering)
    Add_MarketSegment = Table.AddColumn(ExpandSubcat, "Market Price Segment", each 
        let price = [list_price_egp] in
        if price < 180.00 then "Mass Market (شعبي / اقتصادي)"
        else if price <= 450.00 then "Masstige (متوسط متميز)"
        else "Prestige / Luxury (فاخر)",
        type text
    ),

    // Data Enrichment 2: Formulation Origin Classification
    Add_OriginEnriched = Table.AddColumn(Add_MarketSegment, "Formulation Sourcing", each 
        let orig = [origin] in
        if orig = "Egypt" or orig = "Local" then "100% Domestic Egyptian Formulation (صنع في مصر)"
        else "Imported Finished Goods (مستورد)",
        type text
    ),

    // Data Enrichment 3: Standard Unit Margin %
    Add_MarginPct = Table.AddColumn(Add_OriginEnriched, "Baseline Margin Pct", each 
        let 
            p = [list_price_egp],
            c = [standard_cost_egp]
        in
            if p > 0 then Number.Round((p - c) / p, 4) else 0,
        type number
    ),

    Renamed = Table.RenameColumns(Add_MarginPct, {
        {"product_name_en", "Product Name EN"},
        {"product_name_ar", "Product Name AR"},
        {"brand_en", "Brand EN"},
        {"brand_ar", "Brand AR"},
        {"list_price_egp", "List Price EGP"},
        {"standard_cost_egp", "Standard Cost EGP"}
    }),
    Projected = Table.SelectColumns(Renamed, {
        "ProductKey", "SubcategoryKey", "product_id", 
        "Product Name EN", "Product Name AR", "Brand EN", "Brand AR", 
        "List Price EGP", "Standard Cost EGP", "Baseline Margin Pct",
        "Market Price Segment", "Formulation Sourcing"
    })
in
    Projected


// ------------------------------------------------------------------------------
// QUERY: dim_store (35 Retail & E-Commerce Locations)
// Links to dim_geography via GeographyKey (Snowflake Hierarchy)
// ------------------------------------------------------------------------------
let
    Source = cln_stores,
    Deduplicated = Table.Distinct(Source, {"store_id"}),
    Sorted = Table.Sort(Deduplicated, {{"store_id", Order.Ascending}}),
    AddKey = Table.AddIndexColumn(Sorted, "StoreKey", 1, 1, Int64.Type),

    // Merge GeographyKey from dim_geography
    MergeGeo = Table.NestedJoin(AddKey, {"governorate"}, dim_geography, {"Governorate EN"}, "GeoDim", JoinKind.LeftOuter),
    ExpandGeo = Table.ExpandTableColumn(MergeGeo, "GeoDim", {"GeographyKey"}, {"GeographyKey"}),
    DefaultGeo = Table.ReplaceValue(ExpandGeo, null, 1, Replacer.ReplaceValue, {"GeographyKey"}),

    // Add Store Footprint Classification
    Add_Footprint = Table.AddColumn(DefaultGeo, "Store Footprint Class", each 
        let t = [store_type] in
        if t = "Flagship" then "Tier 1 Prime Mall Boutique"
        else if t = "Retail Store" then "High-Street Urban Store"
        else if t = "Kiosk" then "Commercial Center Kiosk"
        else if t = "Online Hub" then "E-Commerce Fulfillment Center"
        else "Regional Outlet",
        type text
    ),

    Renamed = Table.RenameColumns(Add_Footprint, {
        {"store_name_en", "Store Name EN"},
        {"store_name_ar", "Store Name AR"},
        {"area", "Local Area / Neighborhood"},
        {"store_type", "Store Format"}
    }),
    Projected = Table.SelectColumns(Renamed, {
        "StoreKey", "GeographyKey", "store_id", 
        "Store Name EN", "Store Name AR", "Local Area / Neighborhood", 
        "Store Format", "Store Footprint Class"
    })
in
    Projected


// ------------------------------------------------------------------------------
// QUERY: dim_campaign (7 Marketing Campaigns)
// ------------------------------------------------------------------------------
let
    Source = stg_campaigns,
    Deduplicated = Table.Distinct(Source, {"campaign_id"}),
    Sorted = Table.Sort(Deduplicated, {{"campaign_id", Order.Ascending}}),
    AddKey = Table.AddIndexColumn(Sorted, "CampaignKey", 1, 1, Int64.Type),
    
    Renamed = Table.RenameColumns(AddKey, {
        {"campaign_name_en", "Campaign Name EN"},
        {"campaign_name_ar", "Campaign Name AR"},
        {"platform", "Marketing Platform"},
        {"budget_egp", "Budget EGP"},
        {"expected_conversion_rate", "Expected Conversion Rate"}
    })
in
    Renamed


// ------------------------------------------------------------------------------
// QUERY: dim_channel (10 Sales Channels)
// ------------------------------------------------------------------------------
let
    Source = ref_channel_mapping,
    Deduplicated = Table.Distinct(Source, {"NormalizedChannel"}),
    AddKey = Table.AddIndexColumn(Deduplicated, "ChannelKey", 1, 1, Int64.Type),
    Renamed = Table.RenameColumns(AddKey, {
        {"NormalizedChannel", "Channel Name EN"},
        {"Channel_AR", "Channel Name AR"},
        {"ChannelGroup", "Channel Group"}
    }),
    Projected = Table.SelectColumns(Renamed, {"ChannelKey", "RawChannel", "Channel Name EN", "Channel Name AR", "Channel Group"})
in
    Projected


// ------------------------------------------------------------------------------
// QUERY: dim_payment_method (6 Payment Methods)
// ------------------------------------------------------------------------------
let
    Source = ref_payment_mapping,
    Deduplicated = Table.Distinct(Source, {"NormalizedPayment"}),
    AddKey = Table.AddIndexColumn(Deduplicated, "PaymentMethodKey", 1, 1, Int64.Type),
    Renamed = Table.RenameColumns(AddKey, {
        {"NormalizedPayment", "Payment Method EN"},
        {"Payment_AR", "Payment Method AR"},
        {"PaymentCategory", "Payment Category"},
        {"IsDigitalPayment", "Is Digital Payment"}
    }),
    Projected = Table.SelectColumns(Renamed, {"PaymentMethodKey", "RawPayment", "Payment Method EN", "Payment Method AR", "Payment Category", "Is Digital Payment"})
in
    Projected


// ==============================================================================
// 3. GALAXY FACT CONSTELLATIONS (FACT SALES, FACT INVENTORY, FACT TARGETS)
// ==============================================================================

// ------------------------------------------------------------------------------
// QUERY: fact_sales (499,903 rows)
// Grain: One row per validated order transaction line item
// ------------------------------------------------------------------------------
let
    Source = trf_sales,
    
    MergeCust = Table.NestedJoin(Source, {"customer_id"}, dim_customer, {"customer_id"}, "CustDim", JoinKind.LeftOuter),
    ExpandCust = Table.ExpandTableColumn(MergeCust, "CustDim", {"CustomerKey"}, {"CustomerKey"}),
    
    MergeProd = Table.NestedJoin(ExpandCust, {"product_id"}, dim_product, {"product_id"}, "ProdDim", JoinKind.LeftOuter),
    ExpandProd = Table.ExpandTableColumn(MergeProd, "ProdDim", {"ProductKey"}, {"ProductKey"}),
    
    MergeStore = Table.NestedJoin(ExpandProd, {"store_id"}, dim_store, {"store_id"}, "StoreDim", JoinKind.LeftOuter),
    ExpandStore = Table.ExpandTableColumn(MergeStore, "StoreDim", {"StoreKey"}, {"StoreKey"}),
    
    MergeCamp = Table.NestedJoin(ExpandStore, {"campaign_id"}, dim_campaign, {"campaign_id"}, "CampDim", JoinKind.LeftOuter),
    ExpandCamp = Table.ExpandTableColumn(MergeCamp, "CampDim", {"CampaignKey"}, {"CampaignKey"}),
    
    MergeChan = Table.NestedJoin(ExpandCamp, {"sales_channel_en"}, dim_channel, {"RawChannel"}, "ChanDim", JoinKind.LeftOuter),
    ExpandChan = Table.ExpandTableColumn(MergeChan, "ChanDim", {"ChannelKey"}, {"ChannelKey"}),
    
    MergePay = Table.NestedJoin(ExpandChan, {"payment_method_en"}, dim_payment_method, {"RawPayment"}, "PayDim", JoinKind.LeftOuter),
    ExpandPay = Table.ExpandTableColumn(MergePay, "PayDim", {"PaymentMethodKey"}, {"PaymentMethodKey"}),
    
    Projected = Table.SelectColumns(ExpandPay, {
        "order_id",
        "order_datetime",
        "OrderDateKey",
        "CustomerKey",
        "ProductKey",
        "StoreKey",
        "CampaignKey",
        "ChannelKey",
        "PaymentMethodKey",
        "order_status",
        "quantity",
        "unit_price_egp",
        "discount_pct",
        "gross_sales_egp",
        "discount_egp",
        "net_sales_egp",
        "cost_egp",
        "gross_profit_egp"
    })
in
    Projected


// ------------------------------------------------------------------------------
// QUERY: fact_inventory (8,300 rows)
// Grain: Monthly snapshot balance per store per SKU
// Conformed Dimensions: dim_date (MonthDateKey), dim_store (StoreKey), dim_product (ProductKey)
// ------------------------------------------------------------------------------
let
    Source = trf_inventory,
    MergeStore = Table.NestedJoin(Source, {"store_id"}, dim_store, {"store_id"}, "StoreDim", JoinKind.LeftOuter),
    ExpandStore = Table.ExpandTableColumn(MergeStore, "StoreDim", {"StoreKey"}, {"StoreKey"}),
    MergeProd = Table.NestedJoin(ExpandStore, {"product_id"}, dim_product, {"product_id"}, "ProdDim", JoinKind.LeftOuter),
    ExpandProd = Table.ExpandTableColumn(MergeProd, "ProdDim", {"ProductKey"}, {"ProductKey"}),
    
    Projected = Table.SelectColumns(ExpandProd, {
        "MonthDateKey",
        "StoreKey",
        "ProductKey",
        "opening_stock",
        "received_qty",
        "sold_qty",
        "damaged_qty",
        "closing_stock",
        "net_stock_flow",
        "is_low_stock",
        "is_stockout"
    })
in
    Projected


// ------------------------------------------------------------------------------
// QUERY: fact_targets (415 rows)
// Grain: Monthly sales quota per retail store
// Conformed Dimensions: dim_date (TargetDateKey), dim_store (StoreKey)
// ------------------------------------------------------------------------------
let
    Source = trf_targets,
    MergeStore = Table.NestedJoin(Source, {"store_id"}, dim_store, {"store_id"}, "StoreDim", JoinKind.LeftOuter),
    ExpandStore = Table.ExpandTableColumn(MergeStore, "StoreDim", {"StoreKey"}, {"StoreKey"}),
    
    Projected = Table.SelectColumns(ExpandStore, {
        "TargetDateKey",
        "StoreKey",
        "sales_target_egp",
        "order_target"
    })
in
    Projected
