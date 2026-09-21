# Playbook 02: Raw Data Ingestion Across Heterogeneous Formats

## 1. Objective & Scope

This playbook details the extraction and ingestion of raw operational files into Power Query using the parameter `pRawDataPath`. We ingest:
1. Four PostgreSQL operational CSV dumps (`customers.csv`, `products.csv`, `stores.csv`, `orders.csv`)
2. One multi-sheet commercial Excel workbook (`commercial_reference_data.xlsx`) containing sheets `Stores`, `Products`, `Targets`, and `Campaigns`
3. One monthly warehouse inventory CSV (`inventory_monthly.csv`)
4. One API-derived JSON file (`exchange_rates.json`)

All queries created in this stage reside in group **`01_Source`** and have **`Enable Load = False`**.

---

## 2. Ingestion Connector Decision Framework

Understanding when to use specific Power Query connectors and functions is critical for performance and maintainability:

| Connector / Function | When to Use | Why Use in This Architecture |
| :--- | :--- | :--- |
| `Csv.Document` | Reading delimited text files (`.csv`, `.tsv`) | High-speed byte-stream parsing. Combined with `Encoding=65001` (UTF-8), it guarantees zero corruption of Arabic text. |
| `Excel.Workbook` | Reading multi-sheet `.xlsx` or `.xls` workbooks | Returns a navigation table with sheet/table metadata (`Name`, `Data`, `Item`, `Kind`), allowing programmatic multi-sheet extraction. |
| `Json.Document` | Ingesting nested hierarchical JSON files/endpoints | Parses JSON arrays and records into native Power Query `List` and `Record` objects for expansion. |
| `File.Contents` | Reading raw binary byte streams | When coupled with parameterization, ensures dynamic file path resolution across environments. |
| `Table.PromoteHeaders` | Elevating row 1 to column headers | Required after raw byte stream loading where column headers are initially treated as data row 1. |

---

## 3. Step-by-Step Ingestion: GUI & M Methods

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      TWO COMPLEMENTARY INGESTION APPROACHES                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  1. GUI Ribbon:       [Home] -> [New Source] -> [Text/CSV] / [Excel] / [JSON]   │
│  2. Advanced Editor:  [Home] -> [New Source] -> [Blank Query] -> Paste M Code   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.1: Ingesting PostgreSQL CSV Exports

#### Source 1: `src_customers` (25,200 raw rows)

##### 🖱️ Option A: GUI Ribbon Method
1. Click **Home** ribbon $\rightarrow$ **New Source** $\rightarrow$ **Text/CSV**.
2. In the file picker, browse to:
   `d:\courses\Data Science\Data Engineering\Projects\egyptian_cosmetics_market\data\raw\postgres_like\customers.csv`
3. In the preview dialog:
   - **File Origin**: Select `65001: Unicode (UTF-8)` to preserve Arabic characters.
   - **Delimiter**: Select `Comma`.
   - Click **OK**.
4. In the left **Queries** pane, right-click the new query $\rightarrow$ **Rename** to `src_customers`.
5. Drag into folder `01_Source`, right-click $\rightarrow$ **Uncheck "Enable Load"**.
6. To make the file path dynamic, click the gear icon ⚙️ next to the **Source** step in the **Applied Steps** pane $\rightarrow$ switch the file path dropdown from *Text* to *Parameter* $\rightarrow$ select `pRawDataPath`.

##### 💻 Option B: Advanced Editor (M Code with Defensive Sanitizer)
1. **Home** $\rightarrow$ **New Source** $\rightarrow$ **Blank Query** $\rightarrow$ Rename to `src_customers`.
2. Click **Advanced Editor** and paste:
```powerquery
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
```

---

#### Source 2: `src_products` (20 raw rows)

##### 🖱️ GUI Method:
- **Home** $\rightarrow$ **New Source** $\rightarrow$ **Text/CSV** $\rightarrow$ browse to `data\raw\postgres_like\products.csv`. Ensure UTF-8.
- Rename query to `src_products`, move to `01_Source`, disable load.

##### 💻 Advanced Editor M Code:
```powerquery
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
```

---

#### Source 3: `src_stores` (35 raw rows)

##### 🖱️ GUI Method:
- **Home** $\rightarrow$ **New Source** $\rightarrow$ **Text/CSV** $\rightarrow$ `data\raw\postgres_like\stores.csv`. UTF-8.
- Rename to `src_stores`, move to `01_Source`, disable load.

##### 💻 Advanced Editor M Code:
```powerquery
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
```

---

#### Source 4: `src_orders` (502,000 raw rows)

##### 🖱️ GUI Method:
- **Home** $\rightarrow$ **New Source** $\rightarrow$ **Text/CSV** $\rightarrow$ `data\raw\postgres_like\orders.csv`. UTF-8.
- Rename to `src_orders`, move to `01_Source`, disable load.

##### 💻 Advanced Editor M Code:
```powerquery
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
```

---

### 3.2: Ingesting Warehouse Monthly Inventory

#### Source 5: `src_inventory` (8,400 raw rows)

##### 🖱️ GUI Method:
- **Home** $\rightarrow$ **New Source** $\rightarrow$ **Text/CSV** $\rightarrow$ `data\raw\csv\inventory_monthly.csv`. UTF-8.
- Rename to `src_inventory`, move to `01_Source`, disable load.

##### 💻 Advanced Editor M Code:
```powerquery
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
```

---

### 3.3: Ingesting Commercial Excel Workbook (Multi-Sheet)

We ingest the workbook once as `src_excel_workbook`, then reference it to extract `src_targets` and `src_campaigns`.

#### Query: `src_excel_workbook`

##### 🖱️ GUI Method:
- **Home** $\rightarrow$ **New Source** $\rightarrow$ **Excel Workbook** $\rightarrow$ `data\raw\excel\commercial_reference_data.xlsx`.
- In Navigator, select the root folder/file and click **OK**.
- Rename to `src_excel_workbook`, move to `01_Source`, disable load.

##### 💻 Advanced Editor M Code:
```powerquery
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
```

#### Query: `src_targets` (417 target records)
##### 🖱️ GUI Method:
1. In the **Queries** pane, right-click `src_excel_workbook` $\rightarrow$ click **Reference**.
2. In the table view, locate the row where column `Item` = `"Targets"`.
3. Click on the green hyperlinked text **`[Table]`** in the `Data` column. Power Query automatically drills down and navigates to the sheet!
4. Click **Transform** tab $\rightarrow$ **Use First Row as Headers**.
5. Rename query to `src_targets`, move to `01_Source`, disable load.

##### 💻 Advanced Editor M Code:
```powerquery
let
    Source = src_excel_workbook,
    TargetRow = Source{[Item="Targets", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(TargetRow, [PromoteAllScalars=true])
in
    PromotedHeaders
```

#### Query: `src_campaigns` (7 marketing campaigns)
##### 🖱️ GUI Method:
1. Right-click `src_excel_workbook` $\rightarrow$ **Reference**.
2. Click the `[Table]` link in the `Data` column for `Item = "Campaigns"`.
3. Click **Transform** $\rightarrow$ **Use First Row as Headers**.
4. Rename to `src_campaigns`, move to `01_Source`, disable load.

##### 💻 Advanced Editor M Code:
```powerquery
let
    Source = src_excel_workbook,
    CampaignRow = Source{[Item="Campaigns", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(CampaignRow, [PromoteAllScalars=true])
in
    PromotedHeaders
```

---

### 3.4: Ingesting Central Bank / Forex JSON API Dumps

#### Source 8: `src_exchange_rates` (730 exchange rate records)

##### 🖱️ GUI Method:
1. Click **Home** $\rightarrow$ **New Source** $\rightarrow$ **JSON** $\rightarrow$ browse to `data\raw\api\exchange_rates.json`.
2. Power Query displays a list of records. On the **Transform** ribbon, click **To Table** (leave delimiters as default None).
3. In the column header of `Column1`, click the **Expand** icon (two opposing arrows) in the top-right corner.
4. Select columns: `rate_date`, `base_currency`, `rate`, `quote_currency`, `api_timestamp`.
5. Rename query to `src_exchange_rates`, move to `01_Source`, disable load.

##### 💻 Advanced Editor M Code:
```powerquery
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
```

---

## 4. Verification & Health Check

After completing this playbook, inspect your Power Query window:
1. In the **Queries** pane under `01_Source`, you must see all 8 queries in italics (*Enable Load = False*).
2. Click **View** ribbon $\rightarrow$ **Query Dependencies**.
3. Verify that `pRawDataPath` flows into `src_customers`, `src_products`, `src_stores`, `src_orders`, `src_inventory`, `src_excel_workbook`, and `src_exchange_rates`.
4. Verify that `src_excel_workbook` branches into `src_targets` and `src_campaigns`.
5. No red errors or path exceptions should be present.
