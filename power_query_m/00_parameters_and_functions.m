// ==============================================================================
// FILE: 00_parameters_and_functions.m
// PROJECT: Cleopatra Modern Cosmetics (كليوباترا كوزماتكس الحديثة)
// GROUP: 00_Parameters & Functions
// LOAD SETTING: Enable Load = FALSE for all queries in this file
// ==============================================================================
//
// 📖 ARCHITECTURAL GUIDE: HOW TO SET UP PARAMETERS IN POWER BI DESKTOP
// ------------------------------------------------------------------------------
// There are TWO ways to create parameters in Power Query. Choose the one you prefer:
//
// ------------------------------------------------------------------------------
// METHOD 1: POWER QUERY GUI DIALOG (RECOMMENDED FOR MOST DEVELOPERS)
// ------------------------------------------------------------------------------
// 1. In Power Query Editor ribbon, go to:
//    [Home] Tab -> [Parameters] Section -> Click [Manage Parameters] -> [New Parameter]
//
// 2. In the "Manage Parameters" dialog box, fill in the exact fields:
//    ┌─────────────────────┬─────────────────────────────────────────────────────────────┐
//    │ Parameter Name      │ pRawDataPath                                                │
//    │ Description         │ Root directory containing the data/ folder                  │
//    │ Required            │ [x] Checked (Yes)                                           │
//    │ Type                │ Text                                                        │
//    │ Suggested Values    │ Any value                                                   │
//    │ Current Value       │ D:\courses\Data Science\Data Engineering\Projects\egyptian_cosmetics_market\data │
//    └─────────────────────┴─────────────────────────────────────────────────────────────┘
//
//    ⚠️ CRITICAL GUI WARNING / COMMON PITFALL:
//    In the "Current Value" textbox in this GUI dialog, enter ONLY the plain folder path!
//    - DO NOT surround the path with quotation marks ("...")
//    - DO NOT paste 'meta [IsParameterQuery=true...]' into the GUI box!
//    If you paste quotes or 'meta' into the GUI textbox, Power Query escapes it literally,
//    causing: "Expression.Error: Illegal characters in path".
//
// 3. Repeat for Date Parameters:
//    Parameter 2:
//    - Name: pStartDate
//    - Type: Date
//    - Current Value: 2024-01-01
//
//    Parameter 3:
//    - Name: pEndDate
//    - Type: Date
//    - Current Value: 2026-12-31
//
// ------------------------------------------------------------------------------
// METHOD 2: ADVANCED EDITOR / BLANK QUERY (FOR SCRIPT-BASED SETUP)
// ------------------------------------------------------------------------------
// 1. In Power Query Editor, go to: [Home] Tab -> [New Source] -> [Blank Query]
// 2. In the left "Queries" pane, right-click the query -> [Rename] -> 'pRawDataPath'
// 3. Click [Advanced Editor] on the Home ribbon.
// 4. Replace the entire code with the expression below and click [Done]:
//    "D:\courses\Data Science\Data Engineering\Projects\egyptian_cosmetics_market\data" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
// ==============================================================================


// ==============================================================================
// 1. GLOBAL PARAMETERS (M CODE DEFINITIONS)
// ==============================================================================

// ------------------------------------------------------------------------------
// PARAMETER: pRawDataPath
// Description: Absolute root directory of data/
// In GUI: Type = Text | Value = D:\courses\Data Science\Data Engineering\Projects\egyptian_cosmetics_market\data
// ------------------------------------------------------------------------------
"D:\courses\Data Science\Data Engineering\Projects\egyptian_cosmetics_market\data" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]


// ------------------------------------------------------------------------------
// PARAMETER: pStartDate
// Description: Global calendar start boundary (2024-01-01)
// In GUI: Type = Date | Value = 2024-01-01
// ------------------------------------------------------------------------------
#date(2024, 1, 1) meta [IsParameterQuery=true, Type="Date", IsParameterQueryRequired=true]


// ------------------------------------------------------------------------------
// PARAMETER: pEndDate
// Description: Global calendar end boundary (2026-12-31)
// In GUI: Type = Date | Value = 2026-12-31
// ------------------------------------------------------------------------------
#date(2026, 12, 31) meta [IsParameterQuery=true, Type="Date", IsParameterQueryRequired=true]


// ==============================================================================
// 2. REUSABLE M CUSTOM FUNCTIONS
// ==============================================================================

// ------------------------------------------------------------------------------
// FUNCTION: fnCleanText
// Purpose: Enterprise text sanitizer.
//          1. Converts nulls gracefully.
//          2. Strips non-breaking spaces (ASCII/Unicode 160) common in web scrapes.
//          3. Removes non-printable control characters via Text.Clean.
//          4. Collapses internal repeated spaces ("  " -> " ").
//          5. Trims leading and trailing whitespace.
//          6. Returns null for empty strings to maintain consistent nullability.
// Usage in GUI: [Add Column] -> [Invoke Custom Function] -> Select 'fnCleanText'
// Usage in M:   Table.TransformColumns(Source, {{"customer_name", fnCleanText, type text}})
// ------------------------------------------------------------------------------
(inputVal as any) as nullable text =>
let
    RawText = if inputVal = null then null else Text.From(inputVal),
    Cleaned = if RawText = null then null else
        let
            NoNBSP = Text.Replace(RawText, Character.FromNumber(160), " "),
            StrippedControl = Text.Clean(NoNBSP),
            TrimmedOuter = Text.Trim(StrippedControl),
            NormalizedSpaces = List.Accumulate(
                {1..5}, 
                TrimmedOuter, 
                (state, current) => Text.Replace(state, "  ", " ")
            ),
            FinalResult = if NormalizedSpaces = "" then null else NormalizedSpaces
        in
            FinalResult
in
    Cleaned


// ------------------------------------------------------------------------------
// FUNCTION: fnNormalizeCurrency
// Purpose: Unifies diverse regional currency notations to canonical 'EGP'.
//          Handles: 'EGP', 'EGP ', 'جنيه', 'جنيه مصري' -> 'EGP'
//                   'USD', 'دولار' -> 'USD'
//                   'EUR', 'يورو' -> 'EUR'
// ------------------------------------------------------------------------------
(currVal as any) as text =>
let
    RawText = if currVal = null then "" else Text.Trim(Text.From(currVal)),
    Normalized = 
        if RawText = "EGP" or RawText = "EGP " or RawText = "جنيه" or RawText = "جنيه مصري" or RawText = "LE" or RawText = "L.E." or RawText = "ج.م" then "EGP"
        else if RawText = "USD" or RawText = "دولار" then "USD"
        else if RawText = "EUR" or RawText = "يورو" then "EUR"
        else if RawText = "" then "EGP"
        else RawText
in
    Normalized


// ------------------------------------------------------------------------------
// FUNCTION: fnNormalizeStatus
// Purpose: Normalizes order status casing variants and bilingual Arabic labels.
//          Handles: 'Completed', 'completed', 'Complete', 'مكتمل' -> 'Completed'
//                   'Cancelled', 'canceled', 'ملغي' -> 'Cancelled'
//                   'Returned', 'مرتجع' -> 'Returned'
//                   'Pending', 'قيد التنفيذ' -> 'Pending'
// ------------------------------------------------------------------------------
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


// ------------------------------------------------------------------------------
// FUNCTION: fnStandardizeGovernorate
// Purpose: Validates and standardizes Egyptian governorate names.
//          Ensures proper capitalization and unifies compound names
//          (e.g., 'Kafr El Sheikh', 'Port Said', 'Red Sea', 'North Sinai').
// ------------------------------------------------------------------------------
(govVal as any) as text =>
let
    Raw = if govVal = null then "Unknown" else Text.Trim(Text.From(govVal)),
    Proper = Text.Proper(Raw),
    Standardized = 
        if Proper = "Red Sea" or Proper = "Redsea" or Proper = "البحر الأحمر" then "Red Sea"
        else if Proper = "North Sinai" or Proper = "Northsinai" or Proper = "شمال سيناء" then "North Sinai"
        else if Proper = "South Sinai" or Proper = "Southsinai" or Proper = "جنوب سيناء" then "South Sinai"
        else if Proper = "Port Said" or Proper = "Portsaid" or Proper = "بورسعيد" then "Port Said"
        else if Proper = "Kafr El Sheikh" or Proper = "Kafrelsheikh" or Proper = "كفر الشيخ" then "Kafr El Sheikh"
        else if Proper = "Beni Suef" or Proper = "Benisuef" or Proper = "بني سويف" then "Beni Suef"
        else if Proper = "Cairo" or Proper = "القاهرة" then "Cairo"
        else if Proper = "Giza" or Proper = "الجيزة" then "Giza"
        else if Proper = "Alexandria" or Proper = "الإسكندرية" then "Alexandria"
        else if Proper = "Dakahlia" or Proper = "الدقهلية" then "Dakahlia"
        else if Proper = "Sharqia" or Proper = "الشرقية" then "Sharqia"
        else if Proper = "Gharbia" or Proper = "الغربية" then "Gharbia"
        else if Proper = "Monufia" or Proper = "المنوفية" then "Monufia"
        else if Proper = "Qalyubia" or Proper = "القليوبية" then "Qalyubia"
        else if Proper = "Beheira" or Proper = "البحيرة" then "Beheira"
        else if Proper = "Damietta" or Proper = "دمياط" then "Damietta"
        else if Proper = "Ismailia" or Proper = "الإسماعيلية" then "Ismailia"
        else if Proper = "Suez" or Proper = "السويس" then "Suez"
        else if Proper = "Faiyum" or Proper = "الفيوم" then "Faiyum"
        else if Proper = "Minya" or Proper = "المنيا" then "Minya"
        else if Proper = "Asyut" or Proper = "أسيوط" then "Asyut"
        else if Proper = "Sohag" or Proper = "سوهاج" then "Sohag"
        else if Proper = "Qena" or Proper = "قنا" then "Qena"
        else if Proper = "Luxor" or Proper = "الأقصر" then "Luxor"
        else if Proper = "Aswan" or Proper = "أسوان" then "Aswan"
        else if Proper = "Matrouh" or Proper = "مطروح" then "Matrouh"
        else if Proper = "New Valley" or Proper = "الوادي الجديد" then "New Valley"
        else Proper
in
    Standardized


// ------------------------------------------------------------------------------
// FUNCTION: fnValidatePositiveNumber
// Purpose: Boundary validator returning true if numeric and >= minVal.
// ------------------------------------------------------------------------------
(val as any, minVal as number) as logical =>
let
    IsNumeric = try (val <> null and Number.From(val) >= minVal) otherwise false
in
    IsNumeric
