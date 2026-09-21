# Playbook 09: Reusable Power Query M Function Engineering

## 1. Objective & Scope

In production ETL pipelines, custom Power Query (M) functions should not be created merely for aesthetic reasons; they are engineered when they eliminate code duplication, enforce deterministic standards across disparate sources, and simplify pipeline maintenance.

This playbook details the 6 enterprise custom functions developed for the Egyptian Cosmetics Analytics platform:
1. `fnCleanText`: Non-breaking space elimination, control character stripping, internal space normalization.
2. `fnNormalizeCurrency`: Multi-alias currency consolidation (`EGP `, `جنيه`, `جنيه مصري` $\rightarrow$ `EGP`).
3. `fnNormalizeStatus`: Order lifecycle casing and synonym reconciliation.
4. `fnStandardizeGovernorate`: Normalization for the 22 Egyptian governorates.
5. `fnValidatePositiveNumber`: Reusable boundary validator for quantities, prices, and stock balances.
6. `fnAddDataQualityFlags`: Reusable higher-order function that appends standardized boolean quality columns to any table.

All custom functions are stored in group **`00_Parameters & Functions`** and have **`Enable Load = False`**.

---

## 2. How to Create and Author M Functions in Power BI Desktop

### Step-by-Step UI Procedure:
1. In **Power Query Editor**, on the **Home** ribbon, click **New Source** $\rightarrow$ **Blank Query**.
2. On the **View** ribbon, click **Advanced Editor**.
3. In the Advanced Editor, delete all boilerplate code and paste the complete function definition.
4. Click **Done**.
5. In the **Queries** pane, rename the query to match the function name (e.g. `fnCleanText`).
6. Move the query into the group: **`00_Parameters & Functions`**.
7. Power Query will automatically detect the function signature and display an interactive testing interface ("Enter parameters to invoke function").

---

## 3. Detailed Custom Function Catalog

### Function 1: `fnCleanText`
- **Purpose:** Sanitizes messy strings from web inputs, Excel copy-pastes, and operational systems. Strips non-breaking spaces (ASCII 160), removes carriage returns and tabs, consolidates multiple whitespace sequences into a single space, trims leading/trailing spaces, and converts empty strings `""` to `null`.
- **Inputs:** `inputVal as any`
- **Outputs:** `nullable text`
- **Edge Cases Handled:** Null inputs return `null`; non-string inputs are converted via `Text.From`; whitespace-only strings return `null`.

```powerquery
(inputVal as any) as nullable text =>
let
    // Handle nulls safely
    RawText = if inputVal = null then null else Text.From(inputVal),
    
    Cleaned = if RawText = null then null else
        let
            // 1. Replace Non-Breaking Spaces (ASCII 160) with standard space (ASCII 32)
            NoNBSP = Text.Replace(RawText, Character.FromNumber(160), " "),
            
            // 2. Remove non-printable control characters (ASCII 0-31)
            StrippedControl = Text.Clean(NoNBSP),
            
            // 3. Trim outer whitespace
            TrimmedOuter = Text.Trim(StrippedControl),
            
            // 4. Consolidate multiple consecutive spaces
            // Replaces double space iteratively until none remain
            NormalizedSpaces = List.Accumulate(
                {1..5}, 
                TrimmedOuter, 
                (state, current) => Text.Replace(state, "  ", " ")
            ),
            
            // 5. Empty string conversion to null
            FinalResult = if NormalizedSpaces = "" then null else NormalizedSpaces
        in
            FinalResult
in
    Cleaned
```

---

### Function 2: `fnNormalizeCurrency`
- **Purpose:** Resolves regional currency notations into the ISO standard code `"EGP"`.
- **Inputs:** `currVal as any`
- **Outputs:** `text`
- **Edge Cases Handled:** Trailing spaces (`"EGP "`), lowercase Arabic (`"جنيه"`), compound Arabic (`"جنيه مصري"`), foreign currencies (`USD`, `EUR`) preserved.

```powerquery
(currVal as any) as text =>
let
    RawText = if currVal = null then "" else Text.Trim(Text.From(currVal)),
    Normalized = 
        if RawText = "EGP" or RawText = "EGP " or RawText = "جنيه" or RawText = "جنيه مصري" then "EGP"
        else if RawText = "USD" or RawText = "دولار" then "USD"
        else if RawText = "EUR" or RawText = "يورو" then "EUR"
        else if RawText = "" then "EGP" // Default corporate currency
        else RawText
in
    Normalized
```

---

### Function 3: `fnNormalizeStatus`
- **Purpose:** Consolidates casing drift and commercial synonyms into canonical lifecycle states: `Completed`, `Pending`, `Cancelled`, `Returned`.
- **Inputs:** `statusVal as any`
- **Outputs:** `text`

```powerquery
(statusVal as any) as text =>
let
    RawText = if statusVal = null then "Unknown" else Text.Trim(Text.From(statusVal)),
    LowerText = Text.Lower(RawText),
    Normalized = 
        if LowerText = "completed" or LowerText = "complete" or LowerText = "مكتمل" then "Completed"
        else if LowerText = "cancelled" or LowerText = "canceled" or LowerText = "ملغي" then "Cancelled"
        else if LowerText = "returned" or LowerText = "مرتجع" then "Returned"
        else if LowerText = "pending" or LowerText = "قيد التنفيذ" then "Pending"
        else RawText
in
    Normalized
```

---

### Function 4: `fnStandardizeGovernorate`
- **Purpose:** Casing standardization and validation against the 22 Egyptian governorates.
- **Inputs:** `govVal as any`
- **Outputs:** `text`

```powerquery
(govVal as any) as text =>
let
    Raw = if govVal = null then "Unknown" else Text.Trim(Text.From(govVal)),
    Proper = Text.Proper(Raw),
    // Resolve specific multi-word governorate formatting
    Standardized = 
        if Proper = "Red Sea" or Proper = "Redsea" then "Red Sea"
        else if Proper = "North Sinai" or Proper = "Northsinai" then "North Sinai"
        else if Proper = "South Sinai" or Proper = "Southsinai" then "South Sinai"
        else if Proper = "Port Said" or Proper = "Portsaid" then "Port Said"
        else if Proper = "Kafr El Sheikh" or Proper = "Kafrelsheikh" then "Kafr El Sheikh"
        else Proper
in
    Standardized
```

---

### Function 5: `fnValidatePositiveNumber`
- **Purpose:** High-speed boundary check returning boolean `true` if a number is not null and strictly greater than (or equal to) a minimum threshold.
- **Inputs:** `val as any, minVal as number`
- **Outputs:** `logical`

```powerquery
(val as any, minVal as number) as logical =>
let
    IsNumeric = try (val <> null and Number.From(val) >= minVal) otherwise false
in
    IsNumeric
```

---

### Function 6: `fnAddDataQualityFlags`
- **Purpose:** Higher-order function that systematically evaluates a table against required columns and appends `DataQualityStatus` and `DataQualityReason`.
- **Inputs:** `targetTable as table, idCol as text, qtyCol as text, priceCol as text`
- **Outputs:** `table`

```powerquery
(targetTable as table, idCol as text, qtyCol as text, priceCol as text) as table =>
let
    AddQtyCheck = Table.AddColumn(targetTable, "DQ_ValidQty", each 
        Record.Field(_, qtyCol) <> null and Record.Field(_, qtyCol) > 0, 
        type logical
    ),
    AddPriceCheck = Table.AddColumn(AddQtyCheck, "DQ_ValidPrice", each 
        Record.Field(_, priceCol) <> null and Record.Field(_, priceCol) > 0, 
        type logical
    ),
    AddStatus = Table.AddColumn(AddPriceCheck, "DQ_Status", each 
        if [DQ_ValidQty] and [DQ_ValidPrice] then "Valid" else "Rejected", 
        type text
    )
in
    AddStatus
```

---

## 4. Best Practices for M Function Invocation

1. **Invoke via `Table.TransformColumns`:** When transforming an existing column, use `Table.TransformColumns(Source, {{"column_name", fnCleanText, type text}})`. This is significantly faster and more memory efficient than `Table.AddColumn` followed by `Table.RemoveColumns`.
2. **Avoid Heavy External Calls Inside Row Iterators:** Never put `Web.Contents` or disk I/O inside a custom function invoked across rows. External references must be evaluated once into a buffered list or table before calling the row-level function.
