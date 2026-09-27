"""
Full Enterprise Power BI TMDL Model Generator for Cleopatra Modern Cosmetics.
Generates:
  1. expressions.tmdl
  2. tables/*.tmdl (all 22 tables + DAX measures)
  3. relationships.tmdl (all 17 Kimball Galaxy + Snowflake relationships)
  4. model.tmdl (with query groups, annotations, table refs)
"""

import os
import re
import uuid

SEMANTIC_MODEL_DIR = r"powerbi\Cleopatra_Cosmetics_Report.SemanticModel\definition"
TABLES_DIR = os.path.join(SEMANTIC_MODEL_DIR, "tables")

def get_guid(seed_text):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(seed_text)))

def parse_m_queries(filepath):
    text = open(filepath, encoding='utf-8').read()
    pattern = r'// (?:QUERY|PARAMETER|FUNCTION):\s*([a-zA-Z0-9_]+)[^\r\n]*[\r\n]+'
    matches = list(re.finditer(pattern, text))
    queries = {}
    for i, m in enumerate(matches):
        q_name = m.group(1)
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        chunk = text[start:end].strip()
        lines = chunk.split('\n')
        code_lines = [l for l in lines if not l.strip().startswith('//')]
        code = '\n'.join(code_lines).strip()
        queries[q_name] = code
    return queries

def parse_dax_measures(filepath):
    text = open(filepath, encoding='utf-8').read()
    folder_pattern = r'// FOLDER:\s*([^\n]+)'
    folder_matches = list(re.finditer(folder_pattern, text))
    all_measures = []
    
    for i, fm in enumerate(folder_matches):
        folder_name = fm.group(1).strip()
        f_start = fm.end()
        f_end = folder_matches[i+1].start() if i+1 < len(folder_matches) else len(text)
        f_chunk = text[f_start:f_end]
        
        # Matches: /// Description (optional), [Measure Name] = \n Code \n /* Format: fmt */
        measure_pattern = r'(?:///\s*([^\n]+)\s*\n)?\[([^\]]+)\]\s*=\s*\n(.*?)(?:\n/\* Format:\s*([^/]+)\*/)?(?=\n\s*(?:///|\[|//\s*-|\Z))'
        matches = list(re.finditer(measure_pattern, f_chunk, re.DOTALL))
        for m in matches:
            desc = m.group(1)
            name = m.group(2).strip()
            code = m.group(3).strip()
            raw_fmt = m.group(4)
            fmt = None
            if raw_fmt:
                raw_fmt = raw_fmt.strip()
                if raw_fmt.startswith("Currency:"):
                    fmt = raw_fmt.replace("Currency:", "").strip()
                elif raw_fmt.startswith("Percentage:"):
                    fmt = raw_fmt.replace("Percentage:", "").strip()
                elif raw_fmt.startswith("Integer:"):
                    fmt = raw_fmt.replace("Integer:", "").strip()
                else:
                    fmt = raw_fmt
            all_measures.append({
                "name": name,
                "code": code,
                "folder": folder_name,
                "desc": desc,
                "format": fmt
            })
    return all_measures

def format_m_code_for_tmdl(code, base_tabs=2):
    tabs = "\t" * base_tabs
    lines = code.split("\n")
    return "\n".join((tabs + l) if l.strip() else "" for l in lines)

def run_build():
    os.makedirs(TABLES_DIR, exist_ok=True)
    
    # 1. Parse all M queries
    m_files = {
        "00": "power_query_m/00_parameters_and_functions.m",
        "01": "power_query_m/01_source_queries.m",
        "02": "power_query_m/02_staging_queries.m",
        "03": "power_query_m/03_reference_queries.m",
        "04": "power_query_m/04_cleansed_queries.m",
        "05": "power_query_m/05_validated_quarantine_queries.m",
        "06": "power_query_m/06_transformation_queries.m",
        "07": "power_query_m/07_model_queries.m",
        "99": "power_query_m/99_admin_queries.m"
    }
    
    parsed = {}
    for k, v in m_files.items():
        parsed[k] = parse_m_queries(v)

    # 2. Build expressions.tmdl (Enable Load = FALSE)
    # Queries in expressions:
    # 00: pRawDataPath, pStartDate, pEndDate, fnCleanText, fnNormalizeCurrency, fnNormalizeStatus, fnStandardizeGovernorate, fnValidatePositiveNumber
    # 01: src_customers, src_products, src_stores, src_orders, src_orders_historical, src_inventory, src_excel_workbook, src_targets, src_campaigns, src_exchange_rates
    # 02: stg_customers, stg_products, stg_stores, stg_orders, stg_orders_historical, stg_orders_combined, stg_inventory, stg_targets, stg_campaigns, stg_fx_rates
    # 03: ref_currency_mapping, ref_status_mapping, ref_governorate_mapping, ref_channel_mapping, ref_payment_mapping
    # 04: cln_customers, cln_products, cln_stores, cln_orders, cln_inventory, cln_targets, cln_campaigns, cln_fx_rates
    # 05: vld_orders_prep, vld_orders, vld_customers_prep, vld_customers, vld_inventory_prep, vld_inventory, vld_targets
    # 06: trf_sales, trf_inventory, trf_targets

    expressions = []
    
    # 00
    for name, code in parsed["00"].items():
        res_type = "Date" if "Date" in name else ("Text" if "Path" in name else "Function")
        expressions.append((name, code, "00_Parameters & Functions", res_type))
    
    # Add fnAddDataQualityFlags
    fn_dq_code = """let
    Source = (targetTable as table, idCol as text, qtyCol as text, priceCol as text) as table =>
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
in
    Source"""
    expressions.append(("fnAddDataQualityFlags", fn_dq_code, "00_Parameters & Functions", "Function"))

    # 01
    for name, code in parsed["01"].items():
        expressions.append((name, code, "01_Source", "Table"))

    # 02
    for name, code in parsed["02"].items():
        expressions.append((name, code, "02_Staging", "Table"))

    # 03
    for name, code in parsed["03"].items():
        expressions.append((name, code, "03_Reference", "Table"))

    # 04
    for name, code in parsed["04"].items():
        expressions.append((name, code, "04_Cleansed", "Table"))

    # 05 (Only non-loaded ones)
    for name in ["vld_orders_prep", "vld_orders", "vld_customers_prep", "vld_customers", "vld_inventory_prep", "vld_inventory", "vld_targets"]:
        if name in parsed["05"]:
            expressions.append((name, parsed["05"][name], "05_Validated", "Table"))

    # 06
    for name, code in parsed["06"].items():
        expressions.append((name, code, "06_Transformations", "Table"))

    # Generate expressions.tmdl text
    expr_text_blocks = []
    for name, code, group, rtype in expressions:
        guid = get_guid(f"expr_{name}")
        lines = []
        trimmed = code.strip()
        if "\n" in trimmed:
            indented = format_m_code_for_tmdl(trimmed, 2)
            lines.append(f"expression {name} = ```\n{indented}\n\t\t```")
        else:
            lines.append(f"expression {name} = {trimmed}")
        lines.append(f"\tlineageTag: {guid}")
        if " " in group or "&" in group:
            lines.append(f"\tqueryGroup: '{group}'")
        else:
            lines.append(f"\tqueryGroup: {group}")
        lines.append("")
        lines.append("\tannotation PBI_NavigationStepName = Navigation")
        lines.append("")
        lines.append(f"\tannotation PBI_ResultType = {rtype}")
        expr_text_blocks.append("\n".join(lines))

    expressions_path = os.path.join(SEMANTIC_MODEL_DIR, "expressions.tmdl")
    with open(expressions_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(expr_text_blocks) + "\n")
    print(f"Wrote {len(expressions)} expressions to {expressions_path}")

    # 3. Build Table TMDL Definitions
    # Table schemas: (name, M code, query_group, list of (col_name, data_type, is_hidden, format_string, is_key))
    tables_meta = [
        # --- 07_Model ---
        ("fact_sales", parsed["07"]["fact_sales"], "07_Model", [
            ("order_id", "string", False, None, False),
            ("order_datetime", "dateTime", False, "yyyy-mm-dd hh:nn:ss", False),
            ("OrderDateKey", "int64", True, "0", False),
            ("CustomerKey", "int64", True, "0", False),
            ("ProductKey", "int64", True, "0", False),
            ("StoreKey", "int64", True, "0", False),
            ("CampaignKey", "int64", True, "0", False),
            ("ChannelKey", "int64", True, "0", False),
            ("PaymentMethodKey", "int64", True, "0", False),
            ("OrderStatusKey", "int64", True, "0", False),
            ("order_status", "string", False, None, False),
            ("quantity", "int64", False, "#,##0", False),
            ("unit_price_egp", "double", False, "#,##0.00", False),
            ("discount_pct", "double", False, "0.0%", False),
            ("gross_sales_egp", "double", False, "#,##0.00", False),
            ("discount_egp", "double", False, "#,##0.00", False),
            ("net_sales_egp", "double", False, "#,##0.00", False),
            ("cost_egp", "double", False, "#,##0.00", False),
            ("gross_profit_egp", "double", False, "#,##0.00", False)
        ]),
        ("fact_inventory", parsed["07"]["fact_inventory"], "07_Model", [
            ("MonthDateKey", "int64", True, "0", False),
            ("StoreKey", "int64", True, "0", False),
            ("ProductKey", "int64", True, "0", False),
            ("opening_stock", "int64", False, "#,##0", False),
            ("received_qty", "int64", False, "#,##0", False),
            ("sold_qty", "int64", False, "#,##0", False),
            ("damaged_qty", "int64", False, "#,##0", False),
            ("closing_stock", "int64", False, "#,##0", False),
            ("net_stock_flow", "int64", False, "#,##0", False),
            ("is_low_stock", "int64", False, "0", False),
            ("is_stockout", "int64", False, "0", False)
        ]),
        ("fact_targets", parsed["07"]["fact_targets"], "07_Model", [
            ("TargetDateKey", "int64", True, "0", False),
            ("StoreKey", "int64", True, "0", False),
            ("sales_target_egp", "double", False, "#,##0.00", False),
            ("order_target", "int64", False, "#,##0", False)
        ]),
        ("dim_date", parsed["07"]["dim_date"], "07_Model", [
            ("DateKey", "int64", True, "0", False),
            ("Date", "dateTime", False, "yyyy-mm-dd", True),
            ("Year", "int64", False, "0", False),
            ("Month Number", "int64", False, "0", False),
            ("Month Name", "string", False, None, False),
            ("Month Short Name", "string", False, None, False),
            ("Month Name AR", "string", False, None, False),
            ("Quarter", "string", False, None, False),
            ("Year Month", "string", False, None, False),
            ("Year Month Number", "int64", False, "0", False),
            ("Week Number", "int64", False, "0", False),
            ("Day", "int64", False, "0", False),
            ("Day Name", "string", False, None, False),
            ("Day Name AR", "string", False, None, False),
            ("Is Weekend", "boolean", False, None, False),
            ("Fiscal Half", "string", False, None, False)
        ]),
        ("dim_customer", parsed["07"]["dim_customer"], "07_Model", [
            ("CustomerKey", "int64", True, "0", False),
            ("GeographyKey", "int64", True, "0", False),
            ("customer_id", "string", False, None, False),
            ("Customer Name AR", "string", False, None, False),
            ("Customer Name EN", "string", False, None, False),
            ("Governorate", "string", False, None, False),
            ("gender", "string", False, None, False),
            ("Age", "int64", False, "0", False),
            ("Age Cohort", "string", False, None, False),
            ("Egyptian Telecom Carrier", "string", False, None, False),
            ("phone", "string", False, None, False),
            ("email", "string", False, None, False),
            ("Signup Date", "dateTime", False, "yyyy-mm-dd", False),
            ("Original Segment", "string", False, None, False),
            ("Lifecycle Tier", "string", False, None, False)
        ]),
        ("dim_product", parsed["07"]["dim_product"], "07_Model", [
            ("ProductKey", "int64", True, "0", False),
            ("SubcategoryKey", "int64", True, "0", False),
            ("product_id", "string", False, None, False),
            ("Product Name EN", "string", False, None, False),
            ("Product Name AR", "string", False, None, False),
            ("Brand EN", "string", False, None, False),
            ("Brand AR", "string", False, None, False),
            ("List Price EGP", "double", False, "#,##0.00", False),
            ("Standard Cost EGP", "double", False, "#,##0.00", False),
            ("Baseline Margin Pct", "double", False, "0.0%", False),
            ("Market Price Segment", "string", False, None, False),
            ("Formulation Sourcing", "string", False, None, False)
        ]),
        ("dim_store", parsed["07"]["dim_store"], "07_Model", [
            ("StoreKey", "int64", True, "0", False),
            ("GeographyKey", "int64", True, "0", False),
            ("store_id", "string", False, None, False),
            ("Store Name EN", "string", False, None, False),
            ("Store Name AR", "string", False, None, False),
            ("Local Area / Neighborhood", "string", False, None, False),
            ("Store Format", "string", False, None, False),
            ("Store Footprint Class", "string", False, None, False)
        ]),
        ("dim_geography", parsed["07"]["dim_geography"], "07_Model", [
            ("GeographyKey", "int64", True, "0", False),
            ("Governorate EN", "string", False, None, False),
            ("Governorate AR", "string", False, None, False),
            ("Economic Region EN", "string", False, None, False),
            ("Economic Region AR", "string", False, None, False),
            ("Distribution Region EN", "string", False, None, False),
            ("Distribution Region AR", "string", False, None, False),
            ("Market Tier", "string", False, None, False),
            ("Logistics Shipping Zone", "string", False, None, False),
            ("Courier SLA Days", "int64", False, "0", False),
            ("Standard Courier Cost EGP", "double", False, "#,##0.00", False)
        ]),
        ("dim_category", parsed["07"]["dim_category"], "07_Model", [
            ("CategoryKey", "int64", True, "0", False),
            ("Category EN", "string", False, None, False),
            ("Category AR", "string", False, None, False),
            ("Strategic Margin Tier", "string", False, None, False),
            ("Commercial Category Lead", "string", False, None, False)
        ]),
        ("dim_subcategory", parsed["07"]["dim_subcategory"], "07_Model", [
            ("SubcategoryKey", "int64", True, "0", False),
            ("CategoryKey", "int64", True, "0", False),
            ("Subcategory EN", "string", False, None, False),
            ("Subcategory AR", "string", False, None, False),
            ("Formulation Type", "string", False, None, False)
        ]),
        ("dim_campaign", parsed["07"]["dim_campaign"], "07_Model", [
            ("CampaignKey", "int64", True, "0", False),
            ("campaign_id", "string", False, None, False),
            ("Campaign Name EN", "string", False, None, False),
            ("Campaign Name AR", "string", False, None, False),
            ("Marketing Platform", "string", False, None, False),
            ("Budget EGP", "double", False, "#,##0.00", False),
            ("Expected Conversion Rate", "double", False, "0.0%", False)
        ]),
        ("dim_channel", parsed["07"]["dim_channel"], "07_Model", [
            ("ChannelKey", "int64", True, "0", False),
            ("RawChannel", "string", True, None, False),
            ("Channel Name EN", "string", False, None, False),
            ("Channel Name AR", "string", False, None, False),
            ("Channel Group", "string", False, None, False)
        ]),
        ("dim_payment_method", parsed["07"]["dim_payment_method"], "07_Model", [
            ("PaymentMethodKey", "int64", True, "0", False),
            ("RawPayment", "string", True, None, False),
            ("Payment Method EN", "string", False, None, False),
            ("Payment Method AR", "string", False, None, False),
            ("Payment Category", "string", False, None, False),
            ("Is Digital Payment", "boolean", False, None, False)
        ]),
        ("dim_order_status", parsed["07"]["dim_order_status"], "07_Model", [
            ("OrderStatusKey", "int64", True, "0", False),
            ("Order Status EN", "string", False, None, False),
            ("Order Status AR", "string", False, None, False),
            ("Is Revenue Recognized", "boolean", False, None, False),
            ("Lifecycle Stage", "string", False, None, False),
            ("Status Sort Order", "int64", False, "0", False)
        ]),

        # --- 05_Validated (Quarantine & DQ) ---
        ("rejected_orders", parsed["05"]["rejected_orders"], "05_Validated", [
            ("order_id", "string", False, None, False),
            ("order_datetime", "dateTime", False, "yyyy-mm-dd hh:nn:ss", False),
            ("customer_id", "string", False, None, False),
            ("product_id", "string", False, None, False),
            ("store_id", "string", False, None, False),
            ("campaign_id", "string", False, None, False),
            ("sales_channel_en", "string", False, None, False),
            ("sales_channel_ar", "string", False, None, False),
            ("payment_method_en", "string", False, None, False),
            ("payment_method_ar", "string", False, None, False),
            ("quantity", "int64", False, "0", False),
            ("unit_price_egp", "double", False, "#,##0.00", False),
            ("discount_pct", "double", False, "0.0%", False),
            ("gross_sales_egp", "double", False, "#,##0.00", False),
            ("discount_egp", "double", False, "#,##0.00", False),
            ("net_sales_egp", "double", False, "#,##0.00", False),
            ("cost_egp", "double", False, "#,##0.00", False),
            ("order_status", "string", False, None, False),
            ("currency", "string", False, None, False),
            ("OrderID_Valid", "boolean", False, None, False),
            ("CustomerID_Valid", "boolean", False, None, False),
            ("ProductID_Valid", "boolean", False, None, False),
            ("StoreID_Valid", "boolean", False, None, False),
            ("Quantity_Valid", "boolean", False, None, False),
            ("Price_Valid", "boolean", False, None, False),
            ("Date_Valid", "boolean", False, None, False),
            ("Currency_Valid", "boolean", False, None, False),
            ("Status_Valid", "boolean", False, None, False),
            ("DataQualityReason", "string", False, None, False),
            ("DataQualityStatus", "string", False, None, False),
            ("QuarantineTimestamp", "dateTime", False, "yyyy-mm-dd hh:nn:ss", False),
            ("SourceSystem", "string", False, None, False)
        ]),
        ("rejected_customers", parsed["05"]["rejected_customers"], "05_Validated", [
            ("customer_id", "string", False, None, False),
            ("customer_name_ar", "string", False, None, False),
            ("customer_name_en", "string", False, None, False),
            ("gender", "string", False, None, False),
            ("birth_year", "int64", False, "0", False),
            ("governorate", "string", False, None, False),
            ("area", "string", False, None, False),
            ("phone", "string", False, None, False),
            ("email", "string", False, None, False),
            ("signup_date", "dateTime", False, "yyyy-mm-dd", False),
            ("customer_segment", "string", False, None, False),
            ("CustomerID_Valid", "boolean", False, None, False),
            ("Contact_Valid", "boolean", False, None, False),
            ("DataQualityReason", "string", False, None, False),
            ("DataQualityStatus", "string", False, None, False),
            ("SourceSystem", "string", False, None, False)
        ]),
        ("rejected_inventory", parsed["05"]["rejected_inventory"], "05_Validated", [
            ("month", "dateTime", False, "yyyy-mm-dd", False),
            ("store_id", "string", False, None, False),
            ("product_id", "string", False, None, False),
            ("opening_stock", "int64", False, "0", False),
            ("received_qty", "int64", False, "0", False),
            ("sold_qty", "int64", False, "0", False),
            ("damaged_qty", "int64", False, "0", False),
            ("closing_stock", "int64", False, "0", False),
            ("ClosingStock_Valid", "boolean", False, None, False),
            ("DamagedQty_Valid", "boolean", False, None, False),
            ("DataQualityReason", "string", False, None, False),
            ("DataQualityStatus", "string", False, None, False),
            ("SourceSystem", "string", False, None, False)
        ]),
        ("rejected_targets", parsed["05"]["rejected_targets"], "05_Validated", [
            ("target_month", "dateTime", False, "yyyy-mm-dd", False),
            ("store_id", "string", False, None, False),
            ("sales_target_egp", "double", False, "#,##0.00", False),
            ("order_target", "int64", False, "0", False),
            ("DataQualityReason", "string", False, None, False)
        ]),
        ("customer_duplicate_analysis", parsed["05"]["customer_duplicate_analysis"], "05_Validated", [
            ("phone", "string", False, None, False),
            ("CustomerCount", "int64", False, "0", False),
            ("CustomerIDs", "string", False, None, False),
            ("Names", "string", False, None, False)
        ]),

        # --- 99_Admin ---
        ("dq_summary", parsed["99"]["dq_summary"], "99_Admin", [
            ("Source Entity", "string", False, None, False),
            ("Raw Rows Ingested", "int64", False, "#,##0", False),
            ("Valid Production Rows", "int64", False, "#,##0", False),
            ("Quarantined Rows", "int64", False, "#,##0", False),
            ("Quality Score %", "double", False, "0.00%", False)
        ]),
        ("refresh_metadata", parsed["99"]["refresh_metadata"], "99_Admin", [
            ("Attribute", "string", False, None, False),
            ("Value", "string", False, None, False),
            ("Category", "string", False, None, False)
        ])
    ]

    for tbl_name, m_code, q_group, cols in tables_meta:
        t_guid = get_guid(f"tbl_{tbl_name}")
        p_guid = get_guid(f"part_{tbl_name}")
        
        lines = [f"table {tbl_name}", f"\tlineageTag: {t_guid}"]
        if tbl_name == "dim_date":
            lines.append("\tdataCategory: Time")
        lines.append("")

        for col_name, dtype, is_hidden, fmt, is_key in cols:
            c_guid = get_guid(f"col_{tbl_name}_{col_name}")
            col_decl = f"\tcolumn '{col_name}'" if " " in col_name or "/" in col_name or "%" in col_name or "-" in col_name else f"\tcolumn {col_name}"
            lines.append(col_decl)
            lines.append(f"\t\tdataType: {dtype}")
            if is_hidden:
                lines.append("\t\tisHidden")
            if is_key:
                lines.append("\t\tisKey")
            if fmt:
                lines.append(f"\t\tformatString: {fmt}")
            lines.append(f"\t\tlineageTag: {c_guid}")
            lines.append("\t\tsummarizeBy: none")
            src_col = f"'{col_name}'" if " " in col_name or "/" in col_name or "%" in col_name or "-" in col_name else col_name
            lines.append(f"\t\tsourceColumn: {src_col}")
            lines.append("")

        # Partition
        lines.append(f"\tpartition {tbl_name} = m")
        lines.append("\t\tmode: import")
        lines.append("\t\tsource = ```")
        lines.append(format_m_code_for_tmdl(m_code.strip(), 3))
        lines.append("\t\t```")
        lines.append("")
        lines.append("\tannotation PBI_NavigationStepName = Navigation")
        lines.append("")
        lines.append("\tannotation PBI_ResultType = Table")
        lines.append("")

        tbl_file = os.path.join(TABLES_DIR, f"{tbl_name}.tmdl")
        with open(tbl_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Generated table file: {tbl_file}")

    # 4. Build _Measures.tmdl
    dax_measures = parse_dax_measures("dax/all_measures.dax")
    m_tbl_guid = get_guid("tbl__Measures")
    m_part_guid = get_guid("part__Measures")
    
    m_lines = [
        "table _Measures",
        f"\tlineageTag: {m_tbl_guid}",
        ""
    ]

    for m in dax_measures:
        m_guid = get_guid(f"meas_{m['name']}")
        meas_name = f"'{m['name']}'" if " " in m['name'] or "%" in m['name'] or "-" in m['name'] else m['name']
        m_code = m['code']
        if "\n" in m_code:
            indented_dax = "\n".join(("\t\t\t" + l) if l.strip() else "" for l in m_code.split("\n"))
            m_lines.append(f"\tmeasure {meas_name} = ```\n{indented_dax}\n\t\t```")
        else:
            m_lines.append(f"\tmeasure {meas_name} = {m_code}")
        
        if m.get('format'):
            m_lines.append(f"\t\tformatString: {m['format']}")
        if m.get('folder'):
            m_lines.append(f"\t\tdisplayFolder: {m['folder']}")
        m_lines.append(f"\t\tlineageTag: {m_guid}")
        m_lines.append("")

    # Empty column placeholder for measures table (hidden)
    m_lines.append("\tcolumn __Placeholder")
    m_lines.append("\t\tdataType: int64")
    m_lines.append("\t\tisHidden")
    m_lines.append(f"\t\tlineageTag: {get_guid('col__Placeholder')}")
    m_lines.append("\t\tsummarizeBy: none")
    m_lines.append("\t\tsourceColumn: __Placeholder")
    m_lines.append("")

    m_lines.append("\tpartition _Measures = m")
    m_lines.append("\t\tmode: import")
    m_lines.append("\t\tsource = ```")
    m_lines.append("\t\t\tlet")
    m_lines.append('\t\t\t    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [#"Column1" = _t]),')
    m_lines.append('\t\t\t    #"Renamed Columns" = Table.RenameColumns(Source,{{"Column1", "__Placeholder"}}),')
    m_lines.append('\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns",{{"__Placeholder", Int64.Type}})')
    m_lines.append("\t\t\tin")
    m_lines.append('\t\t\t    #"Changed Type"')
    m_lines.append("\t\t```")
    m_lines.append("")
    m_lines.append("\tannotation PBI_NavigationStepName = Navigation")
    m_lines.append("")
    m_lines.append("\tannotation PBI_ResultType = Table")
    m_lines.append("")

    measures_file = os.path.join(TABLES_DIR, "_Measures.tmdl")
    with open(measures_file, "w", encoding="utf-8") as f:
        f.write("\n".join(m_lines))
    print(f"Generated {measures_file} with {len(dax_measures)} DAX measures.")

    # 5. Build relationships.tmdl
    # 17 Kimball Galaxy + Snowflake Relationships from Playbook 10
    # Note: dim_customer -> dim_geography is INACTIVE to resolve ambiguous path between fact_sales and dim_geography
    relationships = [
        # (fromTable, fromCol, toTable, toCol, isActive)
        # Galaxy FactSales
        ("fact_sales", "OrderDateKey", "dim_date", "DateKey", True),
        ("fact_sales", "CustomerKey", "dim_customer", "CustomerKey", True),
        ("fact_sales", "ProductKey", "dim_product", "ProductKey", True),
        ("fact_sales", "StoreKey", "dim_store", "StoreKey", True),
        ("fact_sales", "CampaignKey", "dim_campaign", "CampaignKey", True),
        ("fact_sales", "ChannelKey", "dim_channel", "ChannelKey", True),
        ("fact_sales", "PaymentMethodKey", "dim_payment_method", "PaymentMethodKey", True),
        ("fact_sales", "OrderStatusKey", "dim_order_status", "OrderStatusKey", True),
        # Galaxy FactInventory
        ("fact_inventory", "MonthDateKey", "dim_date", "DateKey", True),
        ("fact_inventory", "StoreKey", "dim_store", "StoreKey", True),
        ("fact_inventory", "ProductKey", "dim_product", "ProductKey", True),
        # Galaxy FactTargets
        ("fact_targets", "TargetDateKey", "dim_date", "DateKey", True),
        ("fact_targets", "StoreKey", "dim_store", "StoreKey", True),
        # Snowflake Geography
        ("dim_store", "GeographyKey", "dim_geography", "GeographyKey", True),
        ("dim_customer", "GeographyKey", "dim_geography", "GeographyKey", False),
        # Snowflake Product Hierarchy
        ("dim_subcategory", "CategoryKey", "dim_category", "CategoryKey", True),
        ("dim_product", "SubcategoryKey", "dim_subcategory", "SubcategoryKey", True)
    ]

    rel_lines = []
    for from_tbl, from_col, to_tbl, to_col, is_active in relationships:
        rel_guid = get_guid(f"rel_{from_tbl}_{from_col}_{to_tbl}_{to_col}")
        rel_lines.append(f"relationship {rel_guid}")
        if not is_active:
            rel_lines.append("\tisActive: false")
        rel_lines.append(f"\tfromColumn: {from_tbl}.{from_col}")
        rel_lines.append(f"\ttoColumn: {to_tbl}.{to_col}")
        rel_lines.append("")

    relationships_path = os.path.join(SEMANTIC_MODEL_DIR, "relationships.tmdl")
    with open(relationships_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rel_lines))
    print(f"Generated {relationships_path} with {len(relationships)} relationships.")

    # 6. Build model.tmdl
    # All 22 tables
    all_table_names = [t[0] for t in tables_meta] + ["_Measures"]
    # Sort them: _Measures first, then model tables, then validated, then admin
    order = ["_Measures"] + [t for t in all_table_names if t != "_Measures"]

    model_lines = [
        "model Model",
        "\tculture: en-US",
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        "\tsourceQueryCulture: ar-EG",
        "\tvalueFilterBehavior: independent",
        "\tdataAccessOptions",
        "\t\tlegacyRedirects",
        "\t\treturnErrorValuesAsNull",
        "",
        "queryGroup '00_Parameters & Functions'",
        "\tannotation PBI_QueryGroupOrder = 0",
        "",
        "queryGroup 01_Source",
        "\tannotation PBI_QueryGroupOrder = 1",
        "",
        "queryGroup 02_Staging",
        "\tannotation PBI_QueryGroupOrder = 2",
        "",
        "queryGroup 03_Reference",
        "\tannotation PBI_QueryGroupOrder = 3",
        "",
        "queryGroup 04_Cleansed",
        "\tannotation PBI_QueryGroupOrder = 4",
        "",
        "queryGroup 05_Validated",
        "\tannotation PBI_QueryGroupOrder = 5",
        "",
        "queryGroup 06_Transformations",
        "\tannotation PBI_QueryGroupOrder = 6",
        "",
        "queryGroup 07_Model",
        "\tannotation PBI_QueryGroupOrder = 7",
        "",
        "queryGroup 99_Admin",
        "\tannotation PBI_QueryGroupOrder = 8",
        "",
        "annotation __PBI_TimeIntelligenceEnabled = 0",
        "",
        'annotation PBI_ProTooling = ["DevMode"]',
        ""
    ]

    for tbl in order:
        model_lines.append(f"ref table {tbl}")

    model_lines.append("")
    model_lines.append("ref cultureInfo en-US")
    model_lines.append("")

    model_path = os.path.join(SEMANTIC_MODEL_DIR, "model.tmdl")
    with open(model_path, "w", encoding="utf-8") as f:
        f.write("\n".join(model_lines))
    print(f"Generated {model_path} with {len(order)} table references.")

if __name__ == "__main__":
    run_build()
