# Playbook 20: Troubleshooting, Error Catalog & Diagnostic Playbook

## 1. Objective & Scope

During the implementation and maintenance of enterprise Power BI pipelines, data engineers encounter schema drifts, evaluation timeouts, mashup privacy errors, and DAX relationship blocks.

This playbook provides an exhaustive **Error & Diagnostic Catalog**, detailing the exact root causes, error signatures, and step-by-step resolutions for the 8 most frequent enterprise Power BI issues.

---

## 2. Enterprise Error Catalog & Solutions

### Error 01: `Formula.Firewall: Query references other queries or steps, so it may not access a data source directly.`
- **Error Signature:** Power Query throws firewall violation when refreshing parameterized queries that merge local files with web APIs or cross-group queries.
- **Root Cause:** Power BI Data Privacy Levels (Combine Privacy Levels). Power Query prevents leaking data between sources with differing privacy classifications (e.g. Private vs Public vs Organizational).
- **Step-by-Step Resolution:**
  1. In Power BI Desktop, go to **File** $\rightarrow$ **Options and settings** $\rightarrow$ **Options**.
  2. Under **Current File**, select **Privacy**.
  3. Select: **"Ignore the Privacy Levels and potentially improve performance"**.
  4. Alternatively, ensure all queries that read files reference the parameterized `pRawDataPath` within the same staging boundary.

---

### Error 02: `DataFormat.Error: We couldn't parse the input provided as a Date value.`
- **Error Signature:** Occurs during `Table.TransformColumnTypes` on `order_datetime` or `signup_date`.
- **Root Cause:** Inconsistent date formats in raw files (e.g., `"1900-01-01"` combined with standard ISO timestamps `"2025-05-17 22:32:02"`), or machine locale expecting `DD/MM/YYYY` while the file contains `YYYY-MM-DD`.
- **Step-by-Step Resolution:**
  1. Always provide the explicit culture parameter in M:
     ```powerquery
     Table.TransformColumnTypes(Source, {{"signup_date", type date}}, "en-US")
     ```
  2. For messy text strings, use `DateTime.FromText` wrapped in `try ... otherwise`:
     ```powerquery
     Table.AddColumn(Source, "ParsedDate", each try DateTime.FromText([order_datetime]) otherwise null)
     ```

---

### Error 03: `Expression.Error: The column 'product_id' of the table wasn't found.`
- **Error Signature:** Pipeline fails immediately on a merge or select column step.
- **Root Cause:** Upstream raw file had leading/trailing whitespace in its header row (e.g. `"product_id "` or `" product_id"`), or an upstream step renamed the column prematurely.
- **Step-by-Step Resolution:**
  1. In the very first step of `02_Staging`, inject header trimming:
     ```powerquery
     TrimmedHeaders = Table.TransformColumnNames(Source, Text.Trim)
     ```
  2. Use `MissingField.UseNull` in `Table.SelectColumns`:
     ```powerquery
     Table.SelectColumns(Source, {"product_id", "category"}, MissingField.UseNull)
     ```

---

### Error 04: Arabic Characters Garbled as Gibberish (``)
- **Error Signature:** Arabic product names (`سيروم`, `فاونديشن`) or governorates display as ``.
- **Root Cause:** The CSV file was ingested without specifying UTF-8 code page, defaulting to Windows-1252.
- **Step-by-Step Resolution:**
  1. Open `01_Source` query (e.g. `src_products` or `src_customers`).
  2. In the `Csv.Document` function, add the parameter `Encoding=65001`:
     ```powerquery
     Csv.Document(File.Contents(Path), [Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.Csv])
     ```

---

### Error 05: `Expression.Error: Illegal characters in path.`
- **Error Signature:**
  ```text
  Expression.Error: Illegal characters in path.
  Details:
      "D:\courses\...\synthetic_cosmetics_data" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\raw\postgres_like\customers.csv
  ```
- **Root Cause:**
  When creating or editing the parameter `pRawDataPath` via the Power Query GUI dialog (**Home** $\rightarrow$ **Manage Parameters**), the developer accidentally pasted the entire M code line:
  `"D:\...\data" meta [IsParameterQuery=true, Type="Text"...]`
  into the **"Current Value"** text box. Power Query treats the literal text (including the quotes and the word `meta`) as the file path string! When concatenated with `\raw\postgres_like\customers.csv`, the quotes `"` and brackets `[` are illegal in Windows file paths.
- **Step-by-Step Resolution (GUI):**
  1. On the **Home** ribbon, click **Manage Parameters** $\rightarrow$ **Edit Parameters**.
  2. Select `pRawDataPath`.
  3. Clear the field completely and enter **ONLY** the raw folder directory path:
     `D:\courses\Data Science\Data Engineering\Projects\egyptian_cosmetics_market\data`
  4. Ensure there are **NO** surrounding double quotes `""`, **NO** trailing backslashes, and **NO** `meta [...]` syntax.
  5. Click **OK** and click **Apply changes**.
- **Defensive M Code Fix:**
  In your source queries, use the self-healing sanitizer provided in `01_source_queries.m`:
  ```powerquery
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
  SourceBytes = File.Contents(SourcePath)
  ```

---

### Error 06: `Expression.Error: The value isn't a single-character string. Details: Value= "'"`
- **Error Signature:** `Expression.Error: The value isn't a single-character string. Details: Value= "'"` or `Value= "\/"`.
- **Root Cause:** In the Power Query M standard library, functions `Text.Trim`, `Text.TrimStart`, and `Text.TrimEnd` take an optional second argument `trimChars as any`. If passed as a `text` value, it **must** be exactly one character (length = 1). Passing multi-character strings like `" ""'"` or `"\/"` causes M to throw this error.
- **Step-by-Step Resolution:**
  1. If stripping quotes and whitespace, use standard `Text.Trim(text)` (which strips all whitespace by default) combined with `Text.Replace(text, """", "")` and `Text.Replace(text, "'", "")`.
  2. If using `trimChars` for multiple characters, you **must** pass a **List of single-character strings** instead of a single concatenated string:
     ```powerquery
     // Valid List syntax:
     CleanBasePath = Text.TrimEnd(Text.Trim(WithoutMeta, {" ", """", "'", "#(tab)", "#(cr)", "#(lf)"}), {"\", "/"})
     ```
  3. Or use the safe, self-healing path sanitizer in `01_source_queries.m`.

---

### Error 07: `Memory Limit Exceeded / Evaluation was canceled`
- **Error Signature:** Power BI Desktop crashes or freezes during "Applying query changes" on the 502,000-row orders file.
- **Root Cause:** Leaving `Enable Load = True` on all intermediate staging, cleansed, and transformed queries. The Mashup engine attempts to allocate separate tabular memory buffers for 6 copies of 500,000 rows ($3,000,000\text{ total rows}$).
- **Step-by-Step Resolution:**
  1. In Power Query Editor, review the Queries pane.
  2. Right-click and **uncheck "Enable Load"** on every query in:
     - `01_Source`
     - `02_Staging`
     - `03_Reference`
     - `04_Cleansed`
     - `06_Transformations`
  3. Keep **Enable Load = True** *only* on the 10 final tables in `07_Model` and `rejected_*` audit queries.

---

### Error 06: `A circular dependency was detected: 'DimCustomer'[CustomerKey]`
- **Error Signature:** DAX calculated column or relationship throws circular dependency exception.
- **Root Cause:** Attempting to create a DAX calculated column that references a measure that relies on the same table.
- **Step-by-Step Resolution:**
  1. Eliminate the DAX calculated column.
  2. Push the calculation upstream into Power Query M (`trf_customer`), where row-by-row procedural evaluation is strictly linear and immune to circular context loops.

---

### Error 07: `Cartesian Product / Out of Memory during Table.NestedJoin`
- **Error Signature:** An M merge step runs indefinitely or consumes all available gigabytes of RAM.
- **Root Cause:** Joining on a dimension column that contains duplicate keys. A Left Outer Join multiplies rows exponentially.
- **Step-by-Step Resolution:**
  1. In the dimension query (e.g. `cln_products` or `dim_customer`), apply `Table.Distinct` before the join:
     ```powerquery
     DeduplicatedDim = Table.Distinct(Source, {"product_id"})
     ```
  2. Buffer the dimension table in memory:
     ```powerquery
     BufferedDim = Table.Buffer(DeduplicatedDim)
     ```

---

### Error 08: `The date column contains duplicate or invalid values` when Marking as Date Table
- **Error Signature:** Power BI refuses to mark `DimDate` as an official Date Table.
- **Root Cause:** The date column contains nulls, duplicates, or non-contiguous missing dates.
- **Step-by-Step Resolution:**
  1. Verify `DimDate` was generated via `List.Dates(StartDate, DayCount, #duration(1,0,0,0))`.
  2. Ensure the column datatype is explicitly set to `type date` (NOT `datetime`).
  3. Verify that `DayCount` exactly equals `DATEDIFF(StartDate, EndDate, DAY) + 1`.
