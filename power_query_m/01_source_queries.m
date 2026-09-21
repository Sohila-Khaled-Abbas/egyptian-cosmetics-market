// ==============================================================================
// FILE: 01_source_queries.m
// PROJECT: Cleopatra Modern Cosmetics (كليوباترا كوزماتكس الحديثة)
// GROUP: 01_Source
// LOAD SETTING: Enable Load = FALSE for all queries in this group
// ==============================================================================
//
// 📖 ARCHITECTURAL GUIDE:
// ------------------------------------------------------------------------------
// These 8 queries establish the lossless raw ingestion layer in Power Query.
// They connect directly to CSV, Excel, and JSON files on disk.
//
// All queries in this file use a defensive path sanitizer that:
// 1. Accepts plain paths like 'D:\...\data' or 'D:\...\data\raw'
// 2. Strips accidental quotes ("..."), whitespace, tabs, and newlines
// 3. Gracefully strips 'meta [IsParameterQuery=true...]' if pasted into the path
// 4. Safely strips trailing slashes without single-character string errors
// ==============================================================================


// ------------------------------------------------------------------------------
// QUERY: src_customers
// Source: raw/postgres_like/customers.csv (25,200 rows)
// ------------------------------------------------------------------------------
let
    RawBase = Text.From(pRawDataPath),
    WithoutMeta = if Text.Contains(RawBase, " meta") then Text.Trim(Text.BeforeDelimiter(RawBase, " meta")) else RawBase,
    WithoutQuotes = Text.Trim(Text.Replace(Text.Replace(Text.Trim(WithoutMeta), """", ""), "'", "")),
    CleanBasePath = if Text.EndsWith(WithoutQuotes, "\") or Text.EndsWith(WithoutQuotes, "/")
                    then Text.Start(WithoutQuotes, Text.Length(WithoutQuotes) - 1)
                    else WithoutQuotes,
    BasePath = if Text.EndsWith(Text.Lower(CleanBasePath), "\raw") or Text.EndsWith(Text.Lower(CleanBasePath), "/raw")
               then CleanBasePath
               else CleanBasePath & "\raw",
    SourcePath = BasePath & "\postgres_like\customers.csv",
    SourceBytes = File.Contents(SourcePath),
    RawCsv = Csv.Document(SourceBytes, [Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(RawCsv, [PromoteAllScalars=true])
in
    PromotedHeaders


// ------------------------------------------------------------------------------
// QUERY: src_products
// Source: raw/postgres_like/products.csv (20 rows)
// ------------------------------------------------------------------------------
let
    RawBase = Text.From(pRawDataPath),
    WithoutMeta = if Text.Contains(RawBase, " meta") then Text.Trim(Text.BeforeDelimiter(RawBase, " meta")) else RawBase,
    WithoutQuotes = Text.Trim(Text.Replace(Text.Replace(Text.Trim(WithoutMeta), """", ""), "'", "")),
    CleanBasePath = if Text.EndsWith(WithoutQuotes, "\") or Text.EndsWith(WithoutQuotes, "/")
                    then Text.Start(WithoutQuotes, Text.Length(WithoutQuotes) - 1)
                    else WithoutQuotes,
    BasePath = if Text.EndsWith(Text.Lower(CleanBasePath), "\raw") or Text.EndsWith(Text.Lower(CleanBasePath), "/raw")
               then CleanBasePath
               else CleanBasePath & "\raw",
    SourcePath = BasePath & "\postgres_like\products.csv",
    SourceBytes = File.Contents(SourcePath),
    RawCsv = Csv.Document(SourceBytes, [Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(RawCsv, [PromoteAllScalars=true])
in
    PromotedHeaders


// ------------------------------------------------------------------------------
// QUERY: src_stores
// Source: raw/postgres_like/stores.csv (35 rows)
// ------------------------------------------------------------------------------
let
    RawBase = Text.From(pRawDataPath),
    WithoutMeta = if Text.Contains(RawBase, " meta") then Text.Trim(Text.BeforeDelimiter(RawBase, " meta")) else RawBase,
    WithoutQuotes = Text.Trim(Text.Replace(Text.Replace(Text.Trim(WithoutMeta), """", ""), "'", "")),
    CleanBasePath = if Text.EndsWith(WithoutQuotes, "\") or Text.EndsWith(WithoutQuotes, "/")
                    then Text.Start(WithoutQuotes, Text.Length(WithoutQuotes) - 1)
                    else WithoutQuotes,
    BasePath = if Text.EndsWith(Text.Lower(CleanBasePath), "\raw") or Text.EndsWith(Text.Lower(CleanBasePath), "/raw")
               then CleanBasePath
               else CleanBasePath & "\raw",
    SourcePath = BasePath & "\postgres_like\stores.csv",
    SourceBytes = File.Contents(SourcePath),
    RawCsv = Csv.Document(SourceBytes, [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(RawCsv, [PromoteAllScalars=true])
in
    PromotedHeaders


// ------------------------------------------------------------------------------
// QUERY: src_orders
// Source: raw/postgres_like/orders.csv (502,000 rows)
// ------------------------------------------------------------------------------
let
    RawBase = Text.From(pRawDataPath),
    WithoutMeta = if Text.Contains(RawBase, " meta") then Text.Trim(Text.BeforeDelimiter(RawBase, " meta")) else RawBase,
    WithoutQuotes = Text.Trim(Text.Replace(Text.Replace(Text.Trim(WithoutMeta), """", ""), "'", "")),
    CleanBasePath = if Text.EndsWith(WithoutQuotes, "\") or Text.EndsWith(WithoutQuotes, "/")
                    then Text.Start(WithoutQuotes, Text.Length(WithoutQuotes) - 1)
                    else WithoutQuotes,
    BasePath = if Text.EndsWith(Text.Lower(CleanBasePath), "\raw") or Text.EndsWith(Text.Lower(CleanBasePath), "/raw")
               then CleanBasePath
               else CleanBasePath & "\raw",
    SourcePath = BasePath & "\postgres_like\orders.csv",
    SourceBytes = File.Contents(SourcePath),
    RawCsv = Csv.Document(SourceBytes, [Delimiter=",", Columns=19, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(RawCsv, [PromoteAllScalars=true])
in
    PromotedHeaders


// ------------------------------------------------------------------------------
// QUERY: src_inventory
// Source: raw/csv/inventory_monthly.csv (8,400 rows)
// ------------------------------------------------------------------------------
let
    RawBase = Text.From(pRawDataPath),
    WithoutMeta = if Text.Contains(RawBase, " meta") then Text.Trim(Text.BeforeDelimiter(RawBase, " meta")) else RawBase,
    WithoutQuotes = Text.Trim(Text.Replace(Text.Replace(Text.Trim(WithoutMeta), """", ""), "'", "")),
    CleanBasePath = if Text.EndsWith(WithoutQuotes, "\") or Text.EndsWith(WithoutQuotes, "/")
                    then Text.Start(WithoutQuotes, Text.Length(WithoutQuotes) - 1)
                    else WithoutQuotes,
    BasePath = if Text.EndsWith(Text.Lower(CleanBasePath), "\raw") or Text.EndsWith(Text.Lower(CleanBasePath), "/raw")
               then CleanBasePath
               else CleanBasePath & "\raw",
    SourcePath = BasePath & "\csv\inventory_monthly.csv",
    SourceBytes = File.Contents(SourcePath),
    RawCsv = Csv.Document(SourceBytes, [Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(RawCsv, [PromoteAllScalars=true])
in
    PromotedHeaders


// ------------------------------------------------------------------------------
// QUERY: src_excel_workbook
// Source: raw/excel/commercial_reference_data.xlsx
// ------------------------------------------------------------------------------
let
    RawBase = Text.From(pRawDataPath),
    WithoutMeta = if Text.Contains(RawBase, " meta") then Text.Trim(Text.BeforeDelimiter(RawBase, " meta")) else RawBase,
    WithoutQuotes = Text.Trim(Text.Replace(Text.Replace(Text.Trim(WithoutMeta), """", ""), "'", "")),
    CleanBasePath = if Text.EndsWith(WithoutQuotes, "\") or Text.EndsWith(WithoutQuotes, "/")
                    then Text.Start(WithoutQuotes, Text.Length(WithoutQuotes) - 1)
                    else WithoutQuotes,
    BasePath = if Text.EndsWith(Text.Lower(CleanBasePath), "\raw") or Text.EndsWith(Text.Lower(CleanBasePath), "/raw")
               then CleanBasePath
               else CleanBasePath & "\raw",
    SourcePath = BasePath & "\excel\commercial_reference_data.xlsx",
    SourceBytes = File.Contents(SourcePath),
    WorkbookData = Excel.Workbook(SourceBytes, false, true)
in
    WorkbookData


// ------------------------------------------------------------------------------
// QUERY: src_targets
// Source: src_excel_workbook -> Targets sheet (417 rows)
// ------------------------------------------------------------------------------
let
    Source = src_excel_workbook,
    TargetRow = Source{[Item="Targets", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(TargetRow, [PromoteAllScalars=true])
in
    PromotedHeaders


// ------------------------------------------------------------------------------
// QUERY: src_campaigns
// Source: src_excel_workbook -> Campaigns sheet (7 rows)
// ------------------------------------------------------------------------------
let
    Source = src_excel_workbook,
    CampaignRow = Source{[Item="Campaigns", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(CampaignRow, [PromoteAllScalars=true])
in
    PromotedHeaders


// ------------------------------------------------------------------------------
// QUERY: src_exchange_rates
// Source: raw/api/exchange_rates.json (730 records)
// ------------------------------------------------------------------------------
let
    RawBase = Text.From(pRawDataPath),
    WithoutMeta = if Text.Contains(RawBase, " meta") then Text.Trim(Text.BeforeDelimiter(RawBase, " meta")) else RawBase,
    WithoutQuotes = Text.Trim(Text.Replace(Text.Replace(Text.Trim(WithoutMeta), """", ""), "'", "")),
    CleanBasePath = if Text.EndsWith(WithoutQuotes, "\") or Text.EndsWith(WithoutQuotes, "/")
                    then Text.Start(WithoutQuotes, Text.Length(WithoutQuotes) - 1)
                    else WithoutQuotes,
    BasePath = if Text.EndsWith(Text.Lower(CleanBasePath), "\raw") or Text.EndsWith(Text.Lower(CleanBasePath), "/raw")
               then CleanBasePath
               else CleanBasePath & "\raw",
    SourcePath = BasePath & "\api\exchange_rates.json",
    SourceBytes = File.Contents(SourcePath),
    JsonData = Json.Document(SourceBytes),
    TableFromList = Table.FromList(JsonData, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    ExpandedRecord = Table.ExpandRecordColumn(
        TableFromList, 
        "Column1", 
        {"rate_date", "base_currency", "rate", "quote_currency", "api_timestamp"}, 
        {"rate_date_raw", "base_currency", "exchange_rate", "quote_currency", "api_timestamp"}
    )
in
    ExpandedRecord
