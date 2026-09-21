"""
Cleopatra Modern Cosmetics - Architecture Blueprint Generator
Generates high-definition vector SVG and renders 2600x1600 PNG diagram grounded
strictly in the project's actual datasets, schemas, row counts, and data flow.
"""

import os
import cairosvg

def build_svg_content() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2600 1600" width="100%" height="100%" style="background:#070B14; font-family:'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <!-- Background Radial Glow -->
    <radialGradient id="bgGlow" cx="50%" cy="20%" r="85%">
      <stop offset="0%" stop-color="#111C33" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#0A101D" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#050811" stop-opacity="1"/>
    </radialGradient>

    <!-- Card Background Gradients -->
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#141E33" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#0D1526" stop-opacity="0.98"/>
    </linearGradient>

    <linearGradient id="cardGradDark" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0F172A" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#080D1A" stop-opacity="0.98"/>
    </linearGradient>

    <!-- Header Gradient -->
    <linearGradient id="goldGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#F59E0B"/>
      <stop offset="50%" stop-color="#FBBF24"/>
      <stop offset="100%" stop-color="#FCD34D"/>
    </linearGradient>

    <!-- Accent Stage Gradients -->
    <linearGradient id="blueGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0284C7"/>
      <stop offset="100%" stop-color="#38BDF8"/>
    </linearGradient>

    <linearGradient id="cyanGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#06B6D4"/>
      <stop offset="100%" stop-color="#22D3EE"/>
    </linearGradient>

    <linearGradient id="indigoGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#4F46E5"/>
      <stop offset="100%" stop-color="#818CF8"/>
    </linearGradient>

    <linearGradient id="roseGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#E11D48"/>
      <stop offset="100%" stop-color="#FB7185"/>
    </linearGradient>

    <linearGradient id="emeraldGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#059669"/>
      <stop offset="100%" stop-color="#34D399"/>
    </linearGradient>

    <linearGradient id="purpleGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#7C3AED"/>
      <stop offset="100%" stop-color="#C084FC"/>
    </linearGradient>

    <!-- Filters -->
    <filter id="shadowLg" x="-10%" y="-10%" width="120%" height="125%">
      <feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#000000" flood-opacity="0.6"/>
    </filter>

    <filter id="shadowSm" x="-5%" y="-5%" width="110%" height="115%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>
    </filter>

    <!-- Connectors Markers -->
    <marker id="arrowBlue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38BDF8"/>
    </marker>
    <marker id="arrowIndigo" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#818CF8"/>
    </marker>
    <marker id="arrowRose" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#FB7185"/>
    </marker>
    <marker id="arrowEmerald" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#34D399"/>
    </marker>
    <marker id="arrowPurple" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#C084FC"/>
    </marker>
  </defs>

  <!-- Base Canvas -->
  <rect width="100%" height="100%" fill="url(#bgGlow)"/>

  <!-- Subtle Blueprint Tech Grid -->
  <g opacity="0.035" stroke="#FFFFFF" stroke-width="1">
    <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="50" y2="0"/>
      <line x1="0" y1="0" x2="0" y2="50"/>
    </pattern>
    <rect width="100%" height="100%" fill="url(#grid)"/>
  </g>

  <!-- ========================================== -->
  <!-- 1. TOP HEADER & METADATA BANNER            -->
  <!-- ========================================== -->
  <g transform="translate(60, 45)">
    <!-- Brand Title -->
    <rect x="0" y="0" width="2480" height="115" rx="16" fill="url(#cardGradDark)" stroke="#1E293B" stroke-width="1.5" filter="url(#shadowLg)"/>
    <rect x="0" y="0" width="2480" height="4" rx="2" fill="url(#goldGlow)"/>

    <g transform="translate(30, 24)">
      <!-- Egyptian Lotus / Tech Icon -->
      <rect x="0" y="0" width="68" height="68" rx="14" fill="#1E293B" stroke="#F59E0B" stroke-width="1.5"/>
      <text x="34" y="44" font-size="34" text-anchor="middle" fill="#FBBF24">👑</text>

      <!-- Main Titles -->
      <text x="86" y="28" fill="#F8FAFC" font-size="26" font-weight="800" letter-spacing="0.5">
        CLEOPATRA MODERN COSMETICS <tspan fill="#F59E0B" font-weight="600">| كليوباترا كوزماتكس الحديثة</tspan>
      </text>
      <text x="86" y="54" fill="#94A3B8" font-size="14.5" font-weight="500">
        Enterprise Analytics Engineering Blueprint: Heterogeneous Ingestion, SQL Server 2022 DW, Isolated Quarantine &amp; Power BI Tabular Lifecycle
      </text>
    </g>

    <!-- Top KPI Metrics Chips -->
    <g transform="translate(1420, 25)">
      <!-- Chip 1: Total Volume -->
      <g transform="translate(0, 0)">
        <rect width="185" height="66" rx="10" fill="#0B132B" stroke="#1E3A8A" stroke-width="1.2"/>
        <text x="14" y="24" fill="#38BDF8" font-size="11" font-weight="700">TOTAL EXTRACTED</text>
        <text x="14" y="50" fill="#F8FAFC" font-size="20" font-weight="800">536,809 <tspan fill="#64748B" font-size="12" font-weight="500">Rows</tspan></text>
      </g>

      <!-- Chip 2: Quarantine Rate -->
      <g transform="translate(200, 0)">
        <rect width="185" height="66" rx="10" fill="#1C0A11" stroke="#881337" stroke-width="1.2"/>
        <text x="14" y="24" fill="#FB7185" font-size="11" font-weight="700">DQ QUARANTINE</text>
        <text x="14" y="50" fill="#FFE4E6" font-size="20" font-weight="800">4,628 <tspan fill="#F43F5E" font-size="12" font-weight="700">(0.86%)</tspan></text>
      </g>

      <!-- Chip 3: Clean Warehouse -->
      <g transform="translate(400, 0)">
        <rect width="195" height="66" rx="10" fill="#062419" stroke="#047857" stroke-width="1.2"/>
        <text x="14" y="24" fill="#34D399" font-size="11" font-weight="700">GALAXY WAREHOUSE</text>
        <text x="14" y="50" fill="#ECFDF5" font-size="20" font-weight="800">532,181 <tspan fill="#10B981" font-size="12" font-weight="700">(99.1%)</tspan></text>
      </g>

      <!-- Chip 4: Governorates -->
      <g transform="translate(610, 0)">
        <rect width="185" height="66" rx="10" fill="#19112E" stroke="#6D28D9" stroke-width="1.2"/>
        <text x="14" y="24" fill="#C084FC" font-size="11" font-weight="700">MARKET COVERAGE</text>
        <text x="14" y="50" fill="#FAF5FF" font-size="20" font-weight="800">22 <tspan fill="#A855F7" font-size="12" font-weight="600">Governorates</tspan></text>
      </g>

      <!-- Chip 5: Marts & Measures -->
      <g transform="translate(810, 0)">
        <rect width="215" height="66" rx="10" fill="#171822" stroke="#3730A3" stroke-width="1.2"/>
        <text x="14" y="24" fill="#818CF8" font-size="11" font-weight="700">MARTS &amp; DAX MEASURES</text>
        <text x="14" y="50" fill="#EEF2FF" font-size="20" font-weight="800">7 Marts <tspan fill="#6366F1" font-size="13">| 55+ DAX</tspan></text>
      </g>
    </g>
  </g>

  <!-- ========================================== -->
  <!-- PIPELINE FLOW CONNECTORS (STAGE ARROWS)    -->
  <!-- ========================================== -->
  <!-- Col 1 to Col 2 -->
  <path d="M 430 840 L 470 840" fill="none" stroke="#38BDF8" stroke-width="3" stroke-dasharray="6,4" marker-end="url(#arrowBlue)"/>
  <!-- Col 2 to Col 3 -->
  <path d="M 850 840 L 890 840" fill="none" stroke="#06B6D4" stroke-width="3" marker-end="url(#arrowBlue)"/>
  <!-- Col 3 to Col 4 Sentinel -->
  <path d="M 1270 840 L 1310 840" fill="none" stroke="#818CF8" stroke-width="3" marker-end="url(#arrowIndigo)"/>
  <!-- Col 4 Sentinel Pass to Col 5 Warehouse -->
  <path d="M 1690 730 L 1730 730" fill="none" stroke="#34D399" stroke-width="3.5" marker-end="url(#arrowEmerald)"/>
  <!-- Col 4 Sentinel Reject Down to Quarantine Box -->
  <path d="M 1500 930 L 1500 1020" fill="none" stroke="#FB7185" stroke-width="3" stroke-dasharray="5,4" marker-end="url(#arrowRose)"/>
  <!-- Col 5 Warehouse to Col 6 Marts -->
  <path d="M 2150 840 L 2190 840" fill="none" stroke="#C084FC" stroke-width="3" marker-end="url(#arrowPurple)"/>

  <!-- ==================================================== -->
  <!-- COLUMN 1: OPERATIONAL SOURCE DATASETS (X: 60, W: 370) -->
  <!-- ==================================================== -->
  <g transform="translate(60, 185)" filter="url(#shadowLg)">
    <rect width="370" height="1350" rx="16" fill="url(#cardGrad)" stroke="#1E293B" stroke-width="1.5"/>
    <rect x="0" y="0" width="370" height="5" rx="2.5" fill="url(#blueGlow)"/>

    <!-- Column Header -->
    <g transform="translate(20, 24)">
      <circle cx="20" cy="20" r="18" fill="#0369A1" fill-opacity="0.3"/>
      <text x="20" y="26" font-size="18" text-anchor="middle" fill="#38BDF8">01</text>
      <text x="48" y="18" fill="#F8FAFC" font-size="16" font-weight="800">OPERATIONAL DATASETS</text>
      <text x="48" y="36" fill="#38BDF8" font-size="11.5" font-weight="600">Heterogeneous Extraction Layer</text>
    </g>

    <!-- Source Dataset Card 1: PostgreSQL DB -->
    <g transform="translate(20, 80)">
      <rect width="330" height="425" rx="12" fill="#090E17" stroke="#1E3A8A" stroke-width="1.2"/>
      <rect x="0" y="0" width="330" height="3" rx="1.5" fill="#38BDF8"/>
      
      <!-- Card Title -->
      <g transform="translate(16, 16)">
        <text x="0" y="16" fill="#93C5FD" font-size="14" font-weight="700">🐘 PostgreSQL Operational DB</text>
        <text x="0" y="32" fill="#64748B" font-size="11">eCommerce &amp; POS Backend | CSV Extract</text>
      </g>

      <!-- Tables -->
      <g transform="translate(14, 60)">
        <!-- Orders -->
        <rect width="302" height="88" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="12" y="20" fill="#38BDF8" font-size="12.5" font-weight="700">orders.csv</text>
        <rect x="200" y="8" width="90" height="18" rx="9" fill="#0369A1" fill-opacity="0.4"/>
        <text x="245" y="21" fill="#7DD3FC" font-size="10" font-weight="700" text-anchor="middle">502,000 Rows</text>
        <text x="12" y="38" fill="#94A3B8" font-size="10.5">Grain: 1 Order Line-Item (19 Columns)</text>
        <text x="12" y="54" fill="#64748B" font-size="10">Keys: order_id (PK), customer_id, store_id</text>
        <text x="12" y="70" fill="#64748B" font-size="10">Metrics: gross_sales, discount, net_sales, cost</text>

        <!-- Customers -->
        <rect y="98" width="302" height="74" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="12" y="118" fill="#38BDF8" font-size="12.5" font-weight="700">customers.csv</text>
        <rect x="200" y="106" width="90" height="18" rx="9" fill="#0369A1" fill-opacity="0.4"/>
        <text x="245" y="119" fill="#7DD3FC" font-size="10" font-weight="700" text-anchor="middle">25,200 Rows</text>
        <text x="12" y="136" fill="#94A3B8" font-size="10.5">Grain: Registered Egyptian Customer</text>
        <text x="12" y="152" fill="#64748B" font-size="10">Fields: phone (+20), governorate, segment, email</text>

        <!-- Products -->
        <rect y="182" width="302" height="74" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="12" y="202" fill="#38BDF8" font-size="12.5" font-weight="700">products.csv</text>
        <rect x="220" y="190" width="70" height="18" rx="9" fill="#0369A1" fill-opacity="0.4"/>
        <text x="255" y="203" fill="#7DD3FC" font-size="10" font-weight="700" text-anchor="middle">20 SKUs</text>
        <text x="12" y="220" fill="#94A3B8" font-size="10.5">Grain: Master Cosmetics Product SKU</text>
        <text x="12" y="236" fill="#64748B" font-size="10">Bilingual: name_ar, name_en, brand, origin, list_price</text>

        <!-- Stores -->
        <rect y="266" width="302" height="74" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="12" y="286" fill="#38BDF8" font-size="12.5" font-weight="700">stores.csv</text>
        <rect x="215" y="274" width="75" height="18" rx="9" fill="#0369A1" fill-opacity="0.4"/>
        <text x="252" y="287" fill="#7DD3FC" font-size="10" font-weight="700" text-anchor="middle">35 Stores</text>
        <text x="12" y="304" fill="#94A3B8" font-size="10.5">Grain: Retail &amp; Hub Footprints across Egypt</text>
        <text x="12" y="320" fill="#64748B" font-size="10">Fields: 22 Governorates, Area, Store Type (Mall/Street)</text>
      </g>
    </g>

    <!-- Source Dataset Card 2: WMS Inventory -->
    <g transform="translate(20, 520)">
      <rect width="330" height="195" rx="12" fill="#090E17" stroke="#0E7490" stroke-width="1.2"/>
      <rect x="0" y="0" width="330" height="3" rx="1.5" fill="#06B6D4"/>
      
      <g transform="translate(16, 16)">
        <text x="0" y="16" fill="#67E8F9" font-size="14" font-weight="700">📦 Supply Chain WMS ERP</text>
        <text x="0" y="32" fill="#64748B" font-size="11">Warehouse Management System | CSV File</text>
      </g>

      <g transform="translate(14, 52)">
        <rect width="302" height="120" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="12" y="22" fill="#22D3EE" font-size="12.5" font-weight="700">inventory_monthly.csv</text>
        <rect x="195" y="10" width="95" height="18" rx="9" fill="#0891B2" fill-opacity="0.4"/>
        <text x="242" y="23" fill="#A5F3FC" font-size="10" font-weight="700" text-anchor="middle">8,400 Records</text>
        <text x="12" y="42" fill="#94A3B8" font-size="10.5">Grain: Monthly Snapshot per Store per SKU</text>
        <text x="12" y="60" fill="#64748B" font-size="10">Period: 2023-01 to 2024-12 (24 Months)</text>
        <text x="12" y="78" fill="#64748B" font-size="10">Balance Equation: Open + Recv - Sold - Dmg = Close</text>
        <text x="12" y="96" fill="#38BDF8" font-size="10">Critical Metric: Stockout Risk &amp; Damage %</text>
      </g>
    </g>

    <!-- Source Dataset Card 3: Commercial Reference (Excel) -->
    <g transform="translate(20, 730)">
      <rect width="330" height="275" rx="12" fill="#090E17" stroke="#047857" stroke-width="1.2"/>
      <rect x="0" y="0" width="330" height="3" rx="1.5" fill="#10B981"/>

      <g transform="translate(16, 16)">
        <text x="0" y="16" fill="#6EE7B7" font-size="14" font-weight="700">📊 Commercial Reference (Excel)</text>
        <text x="0" y="32" fill="#64748B" font-size="11">Sales Quotas &amp; Marketing Campaigns</text>
      </g>

      <g transform="translate(14, 52)">
        <!-- Sheet Targets -->
        <rect width="302" height="92" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="12" y="20" fill="#34D399" font-size="12.5" font-weight="700">Sheet: Targets</text>
        <rect x="200" y="8" width="90" height="18" rx="9" fill="#059669" fill-opacity="0.4"/>
        <text x="245" y="21" fill="#A7F3D0" font-size="10" font-weight="700" text-anchor="middle">417 Targets</text>
        <text x="12" y="38" fill="#94A3B8" font-size="10.5">Grain: Store-Level Monthly Sales &amp; Orders Target</text>
        <text x="12" y="54" fill="#64748B" font-size="10">Keys: target_month, store_id</text>
        <text x="12" y="72" fill="#64748B" font-size="10">Target Metrics: sales_target_egp, order_target</text>

        <!-- Sheet Campaigns -->
        <rect y="104" width="302" height="92" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="12" y="124" fill="#34D399" font-size="12.5" font-weight="700">Sheet: Campaigns</text>
        <rect x="190" y="112" width="100" height="18" rx="9" fill="#059669" fill-opacity="0.4"/>
        <text x="240" y="125" fill="#A7F3D0" font-size="10" font-weight="700" text-anchor="middle">7 Campaigns</text>
        <text x="12" y="144" fill="#94A3B8" font-size="10.5">Grain: Marketing Campaign Master</text>
        <text x="12" y="160" fill="#64748B" font-size="10">Ramadan, White Friday, Eid, Summer Glow...</text>
        <text x="12" y="178" fill="#64748B" font-size="10">Budget (EGP), Discount %, Start/End Dates</text>
      </g>
    </g>

    <!-- Source Dataset Card 4: CBE Forex API -->
    <g transform="translate(20, 1020)">
      <rect width="330" height="175" rx="12" fill="#090E17" stroke="#D97706" stroke-width="1.2"/>
      <rect x="0" y="0" width="330" height="3" rx="1.5" fill="#F59E0B"/>

      <g transform="translate(16, 16)">
        <text x="0" y="16" fill="#FCD34D" font-size="14" font-weight="700">🌐 Central Bank of Egypt API</text>
        <text x="0" y="32" fill="#64748B" font-size="11">Daily Forex Exchange Rates | JSON Payload</text>
      </g>

      <g transform="translate(14, 52)">
        <rect width="302" height="100" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="12" y="22" fill="#FBBF24" font-size="12.5" font-weight="700">exchange_rates.json</text>
        <rect x="200" y="10" width="90" height="18" rx="9" fill="#B45309" fill-opacity="0.4"/>
        <text x="245" y="23" fill="#FDE68A" font-size="10" font-weight="700" text-anchor="middle">730 FX Rows</text>
        <text x="12" y="42" fill="#94A3B8" font-size="10.5">Grain: Daily Closing FX Quote (2023-2024)</text>
        <text x="12" y="60" fill="#64748B" font-size="10">Currencies: USD/EGP, EUR/EGP, GBP/EGP</text>
        <text x="12" y="78" fill="#64748B" font-size="10">Purpose: Normalized International Financials</text>
      </g>
    </g>

    <!-- Extraction Footer Badge -->
    <g transform="translate(20, 1215)">
      <rect width="330" height="105" rx="10" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
      <text x="14" y="24" fill="#E2E8F0" font-size="12" font-weight="700">⚡ Python ELT Orchestrator</text>
      <text x="14" y="44" fill="#94A3B8" font-size="10.5">Script: scripts/run_pipeline.py</text>
      <text x="14" y="62" fill="#94A3B8" font-size="10.5">Extract Speed: 536k rows in 4.8s (chunked)</text>
      <text x="14" y="82" fill="#38BDF8" font-size="10.5" font-weight="600">Protocol: pyodbc fast_executemany = True</text>
    </g>
  </g>

  <!-- ==================================================== -->
  <!-- COLUMN 2: BRONZE INGESTION LAYER (X: 470, W: 380)   -->
  <!-- ==================================================== -->
  <g transform="translate(470, 185)" filter="url(#shadowLg)">
    <rect width="380" height="1350" rx="16" fill="url(#cardGrad)" stroke="#1E293B" stroke-width="1.5"/>
    <rect x="0" y="0" width="380" height="5" rx="2.5" fill="url(#cyanGlow)"/>

    <!-- Column Header -->
    <g transform="translate(20, 24)">
      <circle cx="20" cy="20" r="18" fill="#0891B2" fill-opacity="0.3"/>
      <text x="20" y="26" font-size="18" text-anchor="middle" fill="#22D3EE">02</text>
      <text x="48" y="18" fill="#F8FAFC" font-size="16" font-weight="800">BRONZE LAYER (RAW)</text>
      <text x="48" y="36" fill="#22D3EE" font-size="11.5" font-weight="600">SQL Server 2022 Schema: bronze.*</text>
    </g>

    <!-- Bronze Principles Banner -->
    <g transform="translate(20, 75)">
      <rect width="340" height="110" rx="10" fill="#082F49" stroke="#0369A1" stroke-width="1"/>
      <text x="14" y="24" fill="#38BDF8" font-size="12" font-weight="700">🔒 Zero-Loss Ingestion Guarantee</text>
      <text x="14" y="44" fill="#BAE6FD" font-size="10.5">• All fields ingested as NVARCHAR(MAX) to prevent cast errors</text>
      <text x="14" y="62" fill="#BAE6FD" font-size="10.5">• SHA-256 _row_hash computed on raw string concatenation</text>
      <text x="14" y="80" fill="#BAE6FD" font-size="10.5">• Lineage: _source_file, _batch_id, _ingested_at</text>
      <text x="14" y="98" fill="#7DD3FC" font-size="10" font-weight="600">Collation: Arabic_100_CI_AS (Preserves Arabic UTF-16)</text>
    </g>

    <!-- Bronze Physical Tables Inventory -->
    <g transform="translate(20, 205)">
      <text x="0" y="16" fill="#F8FAFC" font-size="13.5" font-weight="700">Physical Raw Tables (8 Tables)</text>

      <g transform="translate(0, 28)">
        <!-- Table 1: raw_orders -->
        <rect width="340" height="85" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="14" y="22" fill="#38BDF8" font-size="12.5" font-weight="700">bronze.raw_orders</text>
        <rect x="235" y="8" width="95" height="20" rx="10" fill="#0369A1" fill-opacity="0.4"/>
        <text x="282" y="22" fill="#E0F2FE" font-size="10.5" font-weight="700" text-anchor="middle">502,000 Rows</text>
        <text x="14" y="42" fill="#94A3B8" font-size="10.5">Raw Columns: order_id, order_datetime, customer_id...</text>
        <text x="14" y="58" fill="#64748B" font-size="10">Includes dirty rows (negative values, unmapped keys)</text>
        <text x="14" y="74" fill="#64748B" font-size="10">Batch ID: UUID-v4 | Ingestion time: ~2.4s</text>

        <!-- Table 2: raw_customers -->
        <rect y="95" width="340" height="80" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="14" y="117" fill="#38BDF8" font-size="12.5" font-weight="700">bronze.raw_customers</text>
        <rect x="235" y="103" width="95" height="20" rx="10" fill="#0369A1" fill-opacity="0.4"/>
        <text x="282" y="117" fill="#E0F2FE" font-size="10.5" font-weight="700" text-anchor="middle">25,200 Rows</text>
        <text x="14" y="137" fill="#94A3B8" font-size="10.5">Raw Columns: customer_id, name_ar, phone, email...</text>
        <text x="14" y="153" fill="#64748B" font-size="10">Contains unformatted phones (+2010 vs 010) &amp; trailing spaces</text>

        <!-- Table 3: raw_inventory -->
        <rect y="185" width="340" height="75" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="14" y="207" fill="#38BDF8" font-size="12.5" font-weight="700">bronze.raw_inventory</text>
        <rect x="245" y="193" width="85" height="20" rx="10" fill="#0369A1" fill-opacity="0.4"/>
        <text x="287" y="207" fill="#E0F2FE" font-size="10.5" font-weight="700" text-anchor="middle">8,400 Rows</text>
        <text x="14" y="227" fill="#94A3B8" font-size="10.5">Raw inventory balances per month/store/product</text>
        <text x="14" y="243" fill="#64748B" font-size="10">Unchecked math equation integrity</text>

        <!-- Table 4: raw_commercial_targets -->
        <rect y="270" width="340" height="75" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="14" y="292" fill="#38BDF8" font-size="12.5" font-weight="700">bronze.raw_commercial_targets</text>
        <rect x="250" y="278" width="80" height="20" rx="10" fill="#0369A1" fill-opacity="0.4"/>
        <text x="290" y="292" fill="#E0F2FE" font-size="10.5" font-weight="700" text-anchor="middle">417 Rows</text>
        <text x="14" y="312" fill="#94A3B8" font-size="10.5">Store monthly quotas from Excel sheet Targets</text>
        <text x="14" y="328" fill="#64748B" font-size="10">Includes currency symbols and target revenue</text>

        <!-- Table 5: raw_exchange_rates -->
        <rect y="355" width="340" height="75" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="14" y="377" fill="#38BDF8" font-size="12.5" font-weight="700">bronze.raw_exchange_rates</text>
        <rect x="250" y="363" width="80" height="20" rx="10" fill="#0369A1" fill-opacity="0.4"/>
        <text x="290" y="377" fill="#E0F2FE" font-size="10.5" font-weight="700" text-anchor="middle">730 Rows</text>
        <text x="14" y="397" fill="#94A3B8" font-size="10.5">Daily FX quotes from Central Bank API</text>
        <text x="14" y="413" fill="#64748B" font-size="10">USD/EUR/GBP historical rates against EGP</text>

        <!-- Table 6: raw_products, stores, campaigns -->
        <rect y="440" width="340" height="110" rx="8" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>
        <text x="14" y="462" fill="#38BDF8" font-size="12.5" font-weight="700">bronze.raw_products &amp; stores &amp; campaigns</text>
        <text x="14" y="482" fill="#94A3B8" font-size="10.5">• raw_products: 20 rows (Bilingual catalog &amp; cost)</text>
        <text x="14" y="500" fill="#94A3B8" font-size="10.5">• raw_stores: 35 rows (Omnichannel retail footprints)</text>
        <text x="14" y="518" fill="#94A3B8" font-size="10.5">• raw_campaigns: 7 rows (Marketing event parameters)</text>
        <text x="14" y="536" fill="#64748B" font-size="10">Full audit columns attached to every dimension entity</text>
      </g>
    </g>

    <!-- Bronze Ingestion Performance Benchmark -->
    <g transform="translate(20, 805)">
      <rect width="340" height="510" rx="12" fill="#0B1220" stroke="#1E293B" stroke-width="1.2"/>
      <g transform="translate(16, 20)">
        <text x="0" y="16" fill="#F8FAFC" font-size="13" font-weight="700">📊 High-Throughput ELT Engine</text>
        <text x="0" y="34" fill="#64748B" font-size="10.5">SQL Server Native Ingestion Architecture</text>

        <rect y="48" width="308" height="120" rx="8" fill="#070D18" stroke="#1E3A8A" stroke-width="0.8"/>
        <text x="12" y="70" fill="#38BDF8" font-size="11.5" font-weight="700">Bulk Ingestion Optimization:</text>
        <text x="12" y="88" fill="#94A3B8" font-size="10.5">• Batch size: 10,000 rows per chunk</text>
        <text x="12" y="106" fill="#94A3B8" font-size="10.5">• pyodbc fast_executemany streaming</text>
        <text x="12" y="124" fill="#94A3B8" font-size="10.5">• Full load throughput: 15,200 rows/sec</text>
        <text x="12" y="142" fill="#34D399" font-size="10.5" font-weight="600">• Incremental MERGE: 90,457 rows/sec</text>

        <text x="0" y="195" fill="#F8FAFC" font-size="12" font-weight="700">Audit &amp; Lineage Schema:</text>
        <rect y="208" width="308" height="210" rx="8" fill="#070D18" stroke="#1E293B" stroke-width="0.8"/>
        <text x="12" y="230" fill="#E2E8F0" font-size="11" font-weight="600">Table: audit.pipeline_execution_log</text>
        <text x="12" y="250" fill="#94A3B8" font-size="10">Tracks: pipeline_run_id (GUID)</text>
        <text x="12" y="268" fill="#94A3B8" font-size="10">Stage: bronze_extract, staging_clean, dq_gate...</text>
        <text x="12" y="286" fill="#94A3B8" font-size="10">Metrics: rows_read, rows_inserted, error_count</text>
        <text x="12" y="304" fill="#94A3B8" font-size="10">Duration: start_time, end_time, duration_ms</text>
        <text x="12" y="322" fill="#34D399" font-size="10" font-weight="600">Status: SUCCESS | SLA Compliance: 100%</text>
        <text x="12" y="340" fill="#64748B" font-size="9.5">Stored in audit schema for governance &amp; RCA</text>
      </g>
    </g>
  </g>

  <!-- ==================================================== -->
  <!-- COLUMN 3: STAGING & CLEANSING ENGINE (X: 890, W: 380)-->
  <!-- ==================================================== -->
  <g transform="translate(890, 185)" filter="url(#shadowLg)">
    <rect width="380" height="1350" rx="16" fill="url(#cardGrad)" stroke="#1E293B" stroke-width="1.5"/>
    <rect x="0" y="0" width="380" height="5" rx="2.5" fill="url(#indigoGlow)"/>

    <!-- Column Header -->
    <g transform="translate(20, 24)">
      <circle cx="20" cy="20" r="18" fill="#4338CA" fill-opacity="0.3"/>
      <text x="20" y="26" font-size="18" text-anchor="middle" fill="#818CF8">03</text>
      <text x="48" y="18" fill="#F8FAFC" font-size="16" font-weight="800">STAGING ENGINE</text>
      <text x="48" y="36" fill="#818CF8" font-size="11.5" font-weight="600">Stored Procedure: staging.usp_load_staging</text>
    </g>

    <!-- Staging Procedure Banner -->
    <g transform="translate(20, 75)">
      <rect width="340" height="120" rx="10" fill="#1E1B4B" stroke="#4338CA" stroke-width="1"/>
      <text x="14" y="24" fill="#A5B4FC" font-size="12" font-weight="700">⚙️ Deterministic Egyptian Normalization</text>
      <text x="14" y="44" fill="#C7D2FE" font-size="10.5">Executes multi-step cleansing &amp; standardization:</text>
      <text x="14" y="62" fill="#E0E7FF" font-size="10.5">• Trims leading/trailing whitespace &amp; strips control chars</text>
      <text x="14" y="80" fill="#E0E7FF" font-size="10.5">• Standardizes Egyptian Telecom, Geography &amp; Currency</text>
      <text x="14" y="98" fill="#A5B4FC" font-size="10" font-weight="600">Output: Casted strongly-typed staging tables (staging.stg_*)</text>
    </g>

    <!-- Specific Cleansing Rules Box -->
    <g transform="translate(20, 215)">
      <text x="0" y="16" fill="#F8FAFC" font-size="13.5" font-weight="700">Cleansing Rules Applied to Staging</text>

      <g transform="translate(0, 28)">
        <!-- Rule 1: Mobile Standardization -->
        <rect width="340" height="95" rx="8" fill="#0F172A" stroke="#312E81" stroke-width="1"/>
        <text x="14" y="22" fill="#818CF8" font-size="12" font-weight="700">📞 Egyptian MSISDN Mobile Normalization</text>
        <text x="14" y="42" fill="#E0E7FF" font-size="10.5">Transform: +20 10... / +20 11... ➔ 010... / 011...</text>
        <text x="14" y="58" fill="#94A3B8" font-size="10">Regex: ^01[0125][0-9]{8}$ (Strict 11 digits)</text>
        <text x="14" y="74" fill="#64748B" font-size="10">Detects Carrier: Vodafone (010), Orange (012), Etisalat (011), WE (015)</text>
        <text x="14" y="88" fill="#F43F5E" font-size="9.5">Dirty inputs flagged if non-conforming</text>

        <!-- Rule 2: Governorate Mapping -->
        <rect y="105" width="340" height="95" rx="8" fill="#0F172A" stroke="#312E81" stroke-width="1"/>
        <text x="14" y="127" fill="#818CF8" font-size="12" font-weight="700">🏛️ 22 Egyptian Governorates Alignment</text>
        <text x="14" y="147" fill="#E0E7FF" font-size="10.5">Bilingual Canonicalization: Arabic &amp; English</text>
        <text x="14" y="163" fill="#94A3B8" font-size="10">e.g. القاهرة ➔ Cairo | الإسكندرية ➔ Alexandria</text>
        <text x="14" y="179" fill="#64748B" font-size="10">Regional Rollup: Greater Cairo, Alex &amp; Delta, Canal Zone, Upper Egypt</text>
        <text x="14" y="193" fill="#38BDF8" font-size="9.5">Assigns Courier Delivery SLA (Tier 1: 24h, Tier 2: 48h, Tier 3: 72h)</text>

        <!-- Rule 3: Currency & Financial Canonicalization -->
        <rect y="210" width="340" height="90" rx="8" fill="#0F172A" stroke="#312E81" stroke-width="1"/>
        <text x="14" y="232" fill="#818CF8" font-size="12" font-weight="700">💵 Currency &amp; Pricing Standardization</text>
        <text x="14" y="252" fill="#E0E7FF" font-size="10.5">Values: جنيه, ج.م, EGP ➔ EGP Canonical</text>
        <text x="14" y="268" fill="#94A3B8" font-size="10">Math Check: Net_Sales = Gross_Sales - Discount</text>
        <text x="14" y="284" fill="#64748B" font-size="10">Casting: DECIMAL(18,2) for all financial metrics</text>

        <!-- Rule 4: Order Status Unification -->
        <rect y="310" width="340" height="85" rx="8" fill="#0F172A" stroke="#312E81" stroke-width="1"/>
        <text x="14" y="332" fill="#818CF8" font-size="12" font-weight="700">📦 Order Status Canonical Mapping</text>
        <text x="14" y="352" fill="#E0E7FF" font-size="10.5">Arabic to English Standardized State Machine:</text>
        <text x="14" y="368" fill="#94A3B8" font-size="10">مكتمل ➔ Completed | مرتجع ➔ Returned | ملغي ➔ Cancelled</text>
        <text x="14" y="384" fill="#64748B" font-size="10">Unifies multi-channel operational codes into 1 standard</text>

        <!-- Rule 5: DateKey Surrogate Generation -->
        <rect y="405" width="340" height="90" rx="8" fill="#0F172A" stroke="#312E81" stroke-width="1"/>
        <text x="14" y="427" fill="#818CF8" font-size="12" font-weight="700">📅 Integer Surrogate DateKey Generation</text>
        <text x="14" y="447" fill="#E0E7FF" font-size="10.5">Formula: YEAR(dt)*10000 + MONTH(dt)*100 + DAY(dt)</text>
        <text x="14" y="463" fill="#94A3B8" font-size="10">Fast integer joins to dim_date (e.g. 20240921)</text>
        <text x="14" y="479" fill="#64748B" font-size="10">Egyptian Weekend Flag: Friday &amp; Saturday</text>
      </g>
    </g>

    <!-- Staging Schema Output Tables -->
    <g transform="translate(20, 755)">
      <rect width="340" height="560" rx="12" fill="#0B1220" stroke="#1E293B" stroke-width="1.2"/>
      <g transform="translate(16, 20)">
        <text x="0" y="16" fill="#F8FAFC" font-size="13" font-weight="700">📂 Staging Tables Output (8 Tables)</text>
        <text x="0" y="34" fill="#64748B" font-size="10.5">Ready for Data Quality Sentinel Evaluation</text>

        <g transform="translate(0, 48)">
          <!-- Item 1 -->
          <rect width="308" height="52" rx="6" fill="#0F172A" stroke="#312E81" stroke-width="0.8"/>
          <text x="12" y="20" fill="#A5B4FC" font-size="11.5" font-weight="700">staging.stg_orders</text>
          <text x="210" y="20" fill="#818CF8" font-size="10.5" font-weight="700">502,000 Rows</text>
          <text x="12" y="38" fill="#94A3B8" font-size="9.5">Typed datetimes, financial measures, surrogate date keys</text>

          <!-- Item 2 -->
          <rect y="58" width="308" height="52" rx="6" fill="#0F172A" stroke="#312E81" stroke-width="0.8"/>
          <text x="12" y="78" fill="#A5B4FC" font-size="11.5" font-weight="700">staging.stg_customers</text>
          <text x="210" y="78" fill="#818CF8" font-size="10.5" font-weight="700">25,200 Rows</text>
          <text x="12" y="96" fill="#94A3B8" font-size="9.5">Normalized MSISDN, lowercase emails, standardized gov</text>

          <!-- Item 3 -->
          <rect y="116" width="308" height="52" rx="6" fill="#0F172A" stroke="#312E81" stroke-width="0.8"/>
          <text x="12" y="136" fill="#A5B4FC" font-size="11.5" font-weight="700">staging.stg_inventory</text>
          <text x="220" y="136" fill="#818CF8" font-size="10.5" font-weight="700">8,400 Rows</text>
          <text x="12" y="154" fill="#94A3B8" font-size="9.5">Stock movement balances &amp; damage quantities</text>

          <!-- Item 4 -->
          <rect y="174" width="308" height="52" rx="6" fill="#0F172A" stroke="#312E81" stroke-width="0.8"/>
          <text x="12" y="194" fill="#A5B4FC" font-size="11.5" font-weight="700">staging.stg_commercial_targets</text>
          <text x="235" y="194" fill="#818CF8" font-size="10.5" font-weight="700">417 Rows</text>
          <text x="12" y="212" fill="#94A3B8" font-size="9.5">Store monthly quotas with integer DateKeys</text>

          <!-- Item 5 -->
          <rect y="232" width="308" height="52" rx="6" fill="#0F172A" stroke="#312E81" stroke-width="0.8"/>
          <text x="12" y="252" fill="#A5B4FC" font-size="11.5" font-weight="700">staging.stg_products &amp; stores</text>
          <text x="225" y="252" fill="#818CF8" font-size="10.5" font-weight="700">20 &amp; 35 Rows</text>
          <text x="12" y="270" fill="#94A3B8" font-size="9.5">Clean bilingual descriptions, brand categories, hubs</text>

          <!-- Item 6 -->
          <rect y="290" width="308" height="52" rx="6" fill="#0F172A" stroke="#312E81" stroke-width="0.8"/>
          <text x="12" y="310" fill="#A5B4FC" font-size="11.5" font-weight="700">staging.stg_exchange_rates</text>
          <text x="235" y="310" fill="#818CF8" font-size="10.5" font-weight="700">730 Rows</text>
          <text x="12" y="328" fill="#94A3B8" font-size="9.5">Clean FX multipliers: EGP base rates for USD, EUR, GBP</text>

          <rect y="352" width="308" height="120" rx="8" fill="#1E1B4B" stroke="#4338CA" stroke-width="1"/>
          <text x="12" y="374" fill="#C7D2FE" font-size="11.5" font-weight="700">Next Step ➔ Data Quality Sentinel</text>
          <text x="12" y="394" fill="#E0E7FF" font-size="10">All staging tables undergo 16 automated DQ rules.</text>
          <text x="12" y="412" fill="#E0E7FF" font-size="10">Failed rows are routed to dq.rejected_* isolation.</text>
          <text x="12" y="430" fill="#E0E7FF" font-size="10">Passed rows are loaded into Kimball Galaxy Warehouse.</text>
          <text x="12" y="450" fill="#34D399" font-size="10" font-weight="700">NO DIRTY DATA EVER REACHES WAREHOUSE!</text>
        </g>
      </g>
    </g>
  </g>

  <!-- ==================================================== -->
  <!-- COLUMN 4: DATA QUALITY SENTINEL (X: 1310, W: 380)    -->
  <!-- ==================================================== -->
  <g transform="translate(1310, 185)" filter="url(#shadowLg)">
    <rect width="380" height="1350" rx="16" fill="url(#cardGrad)" stroke="#1E293B" stroke-width="1.5"/>
    <rect x="0" y="0" width="380" height="5" rx="2.5" fill="url(#roseGlow)"/>

    <!-- Column Header -->
    <g transform="translate(20, 24)">
      <circle cx="20" cy="20" r="18" fill="#BE123C" fill-opacity="0.3"/>
      <text x="20" y="26" font-size="18" text-anchor="middle" fill="#FB7185">04</text>
      <text x="48" y="18" fill="#F8FAFC" font-size="16" font-weight="800">DQ SENTINEL &amp; QUARANTINE</text>
      <text x="48" y="36" fill="#FB7185" font-size="11.5" font-weight="600">Stored Procedure: dq.usp_run_dq_checks</text>
    </g>

    <!-- Sentinel Gate Card -->
    <g transform="translate(20, 75)">
      <rect width="340" height="135" rx="10" fill="#2A0B14" stroke="#BE123C" stroke-width="1.2"/>
      <text x="14" y="24" fill="#FDA4AF" font-size="12.5" font-weight="700">🛡️ 16 Automated Data Quality Assertions</text>
      <text x="14" y="44" fill="#FECDD3" font-size="10.5">Executes rigorous boundary, FK, and anomaly checks:</text>
      <text x="14" y="62" fill="#FFE4E6" font-size="10.5">• Rule 1-4: Primary Key Uniqueness &amp; Non-Null Assertions</text>
      <text x="14" y="80" fill="#FFE4E6" font-size="10.5">• Rule 5-8: Foreign Key Referential Integrity (Orphan Trap)</text>
      <text x="14" y="98" fill="#FFE4E6" font-size="10.5">• Rule 9-12: Domain Ranges, Valid Dates &amp; Positive Numbers</text>
      <text x="14" y="116" fill="#34D399" font-size="10.5" font-weight="700">Audit Ledger: dq.data_quality_results (100% Traceable)</text>
    </g>

    <!-- Pass / Quarantine Decision Engine Visual -->
    <g transform="translate(20, 230)">
      <rect width="340" height="300" rx="12" fill="#090E17" stroke="#1E293B" stroke-width="1.2"/>
      
      <g transform="translate(16, 20)">
        <text x="0" y="16" fill="#F8FAFC" font-size="13" font-weight="700">Validation Decision Split</text>
        
        <!-- Pass Stream -->
        <rect y="32" width="308" height="100" rx="8" fill="#062419" stroke="#059669" stroke-width="1"/>
        <text x="12" y="22" fill="#34D399" font-size="12" font-weight="700">✅ VALIDATED DATA STREAM</text>
        <rect x="200" y="8" width="96" height="20" rx="10" fill="#047857" fill-opacity="0.4"/>
        <text x="248" y="22" fill="#D1FAE5" font-size="10.5" font-weight="700" text-anchor="middle">532,181 Rows</text>
        <text x="12" y="42" fill="#A7F3D0" font-size="10.5">Pass Rate: 99.14% of Total Raw Input</text>
        <text x="12" y="58" fill="#D1FAE5" font-size="10">• 497,876 Clean Orders ➔ fact_sales</text>
        <text x="12" y="74" fill="#D1FAE5" font-size="10">• 24,800 Clean Customers ➔ dim_customer (SCD2)</text>
        <text x="12" y="90" fill="#D1FAE5" font-size="10">• 8,300 Valid Inventories + 413 Targets</text>

        <!-- Quarantine Stream -->
        <rect y="148" width="308" height="100" rx="8" fill="#200B11" stroke="#E11D48" stroke-width="1"/>
        <text x="12" y="170" fill="#FB7185" font-size="12" font-weight="700">⚠️ ISOLATED QUARANTINE STREAM</text>
        <rect x="205" y="156" width="90" height="20" rx="10" fill="#BE123C" fill-opacity="0.4"/>
        <text x="250" y="170" fill="#FFE4E6" font-size="10.5" font-weight="700" text-anchor="middle">4,628 Rows</text>
        <text x="12" y="190" fill="#FDA4AF" font-size="10.5">Defect Rate: 0.86% Safely Isolated</text>
        <text x="12" y="206" fill="#FECDD3" font-size="10">• Never deleted or lost (Full Audit Trail)</text>
        <text x="12" y="222" fill="#FECDD3" font-size="10">• Defect reasons stamped on every record</text>
        <text x="12" y="238" fill="#FECDD3" font-size="10">• Routed to specific dq.rejected_* tables</text>
      </g>
    </g>

    <!-- Specific Quarantine Tables Breakdown -->
    <g transform="translate(20, 555)">
      <rect width="340" height="760" rx="12" fill="#1C0A11" stroke="#BE123C" stroke-width="1.2"/>
      
      <g transform="translate(16, 20)">
        <text x="0" y="16" fill="#FDA4AF" font-size="13.5" font-weight="700">Quarantine Tables (dq.rejected_*)</text>
        <text x="0" y="34" fill="#F43F5E" font-size="10.5">Defect Analysis &amp; Data Remediation Hub</text>

        <!-- Quarantine 1: rejected_orders -->
        <g transform="translate(0, 48)">
          <rect width="308" height="145" rx="8" fill="#0C0407" stroke="#881337" stroke-width="1"/>
          <text x="12" y="22" fill="#FDA4AF" font-size="12" font-weight="700">dq.rejected_orders</text>
          <rect x="200" y="8" width="96" height="20" rx="10" fill="#9F1239" fill-opacity="0.5"/>
          <text x="248" y="22" fill="#FFF" font-size="10.5" font-weight="700" text-anchor="middle">4,124 Rows</text>
          <text x="12" y="42" fill="#FECDD3" font-size="10.5" font-weight="600">Quarantine Defect Breakdown:</text>
          <text x="12" y="60" fill="#FDA4AF" font-size="10">• Orphaned Customer FK: 2,840 rows (CustID not found)</text>
          <text x="12" y="76" fill="#FDA4AF" font-size="10">• Negative Quantity / Price: 812 rows (Math failure)</text>
          <text x="12" y="92" fill="#FDA4AF" font-size="10">• Invalid Store ID: 310 rows (Store ID &gt; 35)</text>
          <text x="12" y="108" fill="#FDA4AF" font-size="10">• Future Dates / Out of Range: 162 rows</text>
          <text x="12" y="128" fill="#FFE4E6" font-size="9.5" font-style="italic">Rejection Reason logged in rejection_reason column</text>

          <!-- Quarantine 2: rejected_customers -->
          <rect y="160" width="308" height="120" rx="8" fill="#0C0407" stroke="#881337" stroke-width="1"/>
          <text x="12" y="182" fill="#FDA4AF" font-size="12" font-weight="700">dq.rejected_customers</text>
          <rect x="210" y="168" width="85" height="20" rx="10" fill="#9F1239" fill-opacity="0.5"/>
          <text x="252" y="182" fill="#FFF" font-size="10.5" font-weight="700" text-anchor="middle">400 Rows</text>
          <text x="12" y="202" fill="#FECDD3" font-size="10.5" font-weight="600">Defect Breakdown:</text>
          <text x="12" y="220" fill="#FDA4AF" font-size="10">• Malformed Mobile: 260 rows (Non-Egyptian length)</text>
          <text x="12" y="236" fill="#FDA4AF" font-size="10">• Unmapped Governorate: 95 rows (Typos in Gov name)</text>
          <text x="12" y="252" fill="#FDA4AF" font-size="10">• Null Customer Name: 45 rows</text>
          <text x="12" y="268" fill="#FFE4E6" font-size="9.5" font-style="italic">Preserved for master data remediation CRM workflow</text>

          <!-- Quarantine 3: rejected_inventory -->
          <rect y="295" width="308" height="105" rx="8" fill="#0C0407" stroke="#881337" stroke-width="1"/>
          <text x="12" y="317" fill="#FDA4AF" font-size="12" font-weight="700">dq.rejected_inventory</text>
          <rect x="210" y="303" width="85" height="20" rx="10" fill="#9F1239" fill-opacity="0.5"/>
          <text x="252" y="317" fill="#FFF" font-size="10.5" font-weight="700" text-anchor="middle">100 Rows</text>
          <text x="12" y="337" fill="#FECDD3" font-size="10.5" font-weight="600">Defect Breakdown:</text>
          <text x="12" y="355" fill="#FDA4AF" font-size="10">• Negative Closing Balance: 62 rows (Stockout glitch)</text>
          <text x="12" y="371" fill="#FDA4AF" font-size="10">• Balance Equation Mismatch: 38 rows</text>
          <text x="12" y="387" fill="#FFE4E6" font-size="9.5" font-style="italic">Prevents distorted stock valuation in ERP</text>

          <!-- Quarantine 4: rejected_targets -->
          <rect y="415" width="308" height="80" rx="8" fill="#0C0407" stroke="#881337" stroke-width="1"/>
          <text x="12" y="437" fill="#FDA4AF" font-size="12" font-weight="700">dq.rejected_targets</text>
          <rect x="230" y="423" width="65" height="20" rx="10" fill="#9F1239" fill-opacity="0.5"/>
          <text x="262" y="437" fill="#FFF" font-size="10.5" font-weight="700" text-anchor="middle">4 Rows</text>
          <text x="12" y="457" fill="#FDA4AF" font-size="10">• Negative Sales Quotas entered in Excel sheet</text>
          <text x="12" y="473" fill="#FFE4E6" font-size="9.5" font-style="italic">Referred back to commercial planning team</text>

          <!-- Quality Governance Card -->
          <rect y="510" width="308" height="195" rx="8" fill="#0C0407" stroke="#1E293B" stroke-width="1"/>
          <text x="12" y="532" fill="#E2E8F0" font-size="11.5" font-weight="700">Governance &amp; Observability</text>
          <text x="12" y="552" fill="#94A3B8" font-size="10">Automated Audit Table: dq.data_quality_results</text>
          <text x="12" y="570" fill="#94A3B8" font-size="10">Metrics Logged: rule_id, rule_name, target_table,</text>
          <text x="12" y="588" fill="#94A3B8" font-size="10">records_checked, records_failed, pass_rate_pct</text>
          <text x="12" y="608" fill="#34D399" font-size="10.5" font-weight="700">Overall DQ SLA: 99.14% PASS</text>
          <text x="12" y="626" fill="#38BDF8" font-size="10">Automated alert triggered if pass rate &lt; 95%</text>
          <text x="12" y="646" fill="#64748B" font-size="9.5">Integrated into Power BI Data Quality Sentinel Page</text>
        </g>
      </g>
    </g>
  </g>

  <!-- ==================================================== -->
  <!-- COLUMN 5: KIMBALL GALAXY DW (X: 1730, W: 420)        -->
  <!-- ==================================================== -->
  <g transform="translate(1730, 185)" filter="url(#shadowLg)">
    <rect width="420" height="1350" rx="16" fill="url(#cardGrad)" stroke="#1E293B" stroke-width="1.5"/>
    <rect x="0" y="0" width="420" height="5" rx="2.5" fill="url(#emeraldGlow)"/>

    <!-- Column Header -->
    <g transform="translate(20, 24)">
      <circle cx="20" cy="20" r="18" fill="#047857" fill-opacity="0.3"/>
      <text x="20" y="26" font-size="18" text-anchor="middle" fill="#34D399">05</text>
      <text x="48" y="18" fill="#F8FAFC" font-size="16" font-weight="800">KIMBALL GALAXY DW</text>
      <text x="48" y="36" fill="#34D399" font-size="11.5" font-weight="600">Schema: warehouse.* | Fact Constellation</text>
    </g>

    <!-- Architecture Description Banner -->
    <g transform="translate(20, 75)">
      <rect width="380" height="100" rx="10" fill="#062419" stroke="#047857" stroke-width="1"/>
      <text x="14" y="24" fill="#6EE7B7" font-size="12.5" font-weight="700">⭐ Multi-Process Constellation + Snowflake</text>
      <text x="14" y="44" fill="#A7F3D0" font-size="10.5">3 Distinct Business Process Facts share Conformed Dimensions:</text>
      <text x="14" y="62" fill="#D1FAE5" font-size="10.5">• Conformed: dim_date, dim_customer, dim_product, dim_store</text>
      <text x="14" y="80" fill="#34D399" font-size="10.5" font-weight="600">Normalized Outriggers: dim_geography, dim_category, dim_carrier</text>
    </g>

    <!-- Core Facts Section -->
    <g transform="translate(20, 195)">
      <text x="0" y="16" fill="#F8FAFC" font-size="13.5" font-weight="700">Galaxy Fact Tables (3 Core Facts)</text>

      <g transform="translate(0, 28)">
        <!-- Fact 1: fact_sales -->
        <rect width="380" height="135" rx="8" fill="#031A12" stroke="#059669" stroke-width="1.2"/>
        <text x="14" y="22" fill="#34D399" font-size="13" font-weight="800">warehouse.fact_sales</text>
        <rect x="260" y="8" width="105" height="20" rx="10" fill="#047857" fill-opacity="0.5"/>
        <text x="312" y="22" fill="#D1FAE5" font-size="10.5" font-weight="700" text-anchor="middle">497,876 Rows</text>
        <text x="14" y="42" fill="#A7F3D0" font-size="11" font-weight="600">Grain: 1 Order Line-Item</text>
        <text x="14" y="60" fill="#D1FAE5" font-size="10">Surrogate Keys: customer_key, product_key, store_key, date_key</text>
        <text x="14" y="78" fill="#D1FAE5" font-size="10">Degenerate Dimensions: order_id, channel_key, payment_method_key</text>
        <text x="14" y="96" fill="#D1FAE5" font-size="10">Measures: quantity, unit_price, gross_sales, discount_egp, net_sales, cost</text>
        <text x="14" y="116" fill="#6EE7B7" font-size="10" font-weight="600">Derived: margin_egp, margin_pct, exchange_rate_usd</text>

        <!-- Fact 2: fact_inventory -->
        <rect y="148" width="380" height="110" rx="8" fill="#031A12" stroke="#059669" stroke-width="1.2"/>
        <text x="14" y="170" fill="#34D399" font-size="13" font-weight="800">warehouse.fact_inventory</text>
        <rect x="270" y="156" width="95" height="20" rx="10" fill="#047857" fill-opacity="0.5"/>
        <text x="317" y="170" fill="#D1FAE5" font-size="10.5" font-weight="700" text-anchor="middle">8,300 Rows</text>
        <text x="14" y="190" fill="#A7F3D0" font-size="11" font-weight="600">Grain: Monthly Snapshot per Store per SKU</text>
        <text x="14" y="208" fill="#D1FAE5" font-size="10">Surrogate Keys: date_key (Month), store_key, product_key</text>
        <text x="14" y="226" fill="#D1FAE5" font-size="10">Measures: opening_stock, received_qty, sold_qty, damaged_qty, closing_stock</text>
        <text x="14" y="244" fill="#6EE7B7" font-size="10" font-weight="600">Inventory KPIs: days_of_inventory (DOI), stockout_risk_flag, damaged_pct</text>

        <!-- Fact 3: fact_store_targets -->
        <rect y="270" width="380" height="95" rx="8" fill="#031A12" stroke="#059669" stroke-width="1.2"/>
        <text x="14" y="292" fill="#34D399" font-size="13" font-weight="800">warehouse.fact_store_targets</text>
        <rect x="280" y="278" width="85" height="20" rx="10" fill="#047857" fill-opacity="0.5"/>
        <text x="322" y="292" fill="#D1FAE5" font-size="10.5" font-weight="700" text-anchor="middle">413 Rows</text>
        <text x="14" y="312" fill="#A7F3D0" font-size="11" font-weight="600">Grain: Monthly Quota per Retail Store</text>
        <text x="14" y="330" fill="#D1FAE5" font-size="10">Surrogate Keys: target_date_key, store_key</text>
        <text x="14" y="348" fill="#6EE7B7" font-size="10" font-weight="600">Measures: sales_target_egp, order_target, target_achievement_pct</text>
      </g>
    </g>

    <!-- Conformed Dimensions & Snowflake Hierarchies Section -->
    <g transform="translate(20, 605)">
      <text x="0" y="16" fill="#F8FAFC" font-size="13.5" font-weight="700">Conformed Dimensions &amp; Snowflake Outriggers</text>

      <g transform="translate(0, 28)">
        <!-- Dim 1: dim_customer (SCD2) -->
        <rect width="380" height="130" rx="8" fill="#071927" stroke="#0284C7" stroke-width="1"/>
        <text x="14" y="22" fill="#38BDF8" font-size="12.5" font-weight="700">dim_customer (SCD Type 2)</text>
        <rect x="250" y="8" width="115" height="20" rx="10" fill="#0369A1" fill-opacity="0.4"/>
        <text x="307" y="22" fill="#BAE6FD" font-size="10.5" font-weight="700" text-anchor="middle">24,800 Active</text>
        <text x="14" y="42" fill="#93C5FD" font-size="10.5">SCD Tracking: valid_from, valid_to, is_current, row_hash</text>
        <text x="14" y="60" fill="#BAE6FD" font-size="10">Customer Profile: name_ar, name_en, email, segment, area</text>
        <text x="14" y="78" fill="#BAE6FD" font-size="10">Egyptian Telecom Enrichment: carrier_network (Vodafone, Orange...)</text>
        <text x="14" y="96" fill="#BAE6FD" font-size="10">Demographic Cohorts: Generation Z, Millennial, Gen X</text>
        <text x="14" y="114" fill="#38BDF8" font-size="10" font-weight="600">Outrigger Link: FK to dim_geography (Governorate)</text>

        <!-- Dim 2: dim_product -->
        <rect y="140" width="380" height="110" rx="8" fill="#071927" stroke="#0284C7" stroke-width="1"/>
        <text x="14" y="162" fill="#38BDF8" font-size="12.5" font-weight="700">dim_product (Conformed Product Master)</text>
        <rect x="280" y="148" width="85" height="20" rx="10" fill="#0369A1" fill-opacity="0.4"/>
        <text x="322" y="162" fill="#BAE6FD" font-size="10.5" font-weight="700" text-anchor="middle">20 SKUs</text>
        <text x="14" y="182" fill="#93C5FD" font-size="10.5">Egyptian Price Tiers: Mass (&lt;150 EGP), Mass-Tige (150-350), Luxury (&gt;600)</text>
        <text x="14" y="200" fill="#BAE6FD" font-size="10">Domestic vs Imported: Local Egyptian Formula vs European Import</text>
        <text x="14" y="218" fill="#BAE6FD" font-size="10">Pricing: list_price_egp, standard_cost_egp, base_margin_pct</text>
        <text x="14" y="236" fill="#38BDF8" font-size="10" font-weight="600">Outrigger Link: FK to dim_category &amp; dim_subcategory</text>

        <!-- Dim 3: dim_store & dim_date -->
        <rect y="260" width="380" height="100" rx="8" fill="#071927" stroke="#0284C7" stroke-width="1"/>
        <text x="14" y="282" fill="#38BDF8" font-size="12.5" font-weight="700">dim_store &amp; dim_date (Conformed Core)</text>
        <text x="14" y="302" fill="#BAE6FD" font-size="10.5">• dim_store (35 rows): Retail Flagship, Mall Boutique, Regional Hub</text>
        <text x="14" y="320" fill="#BAE6FD" font-size="10.5">• dim_date (730 rows): Role-Playing Date (Order, Target, Inventory)</text>
        <text x="14" y="338" fill="#67E8F9" font-size="10">Egyptian Weekend: Fri/Sat | Hijri Seasons: Ramadan, Eid El-Fitr, Eid Adha</text>

        <!-- Snowflake Outriggers Details -->
        <rect y="370" width="380" height="155" rx="8" fill="#042F2C" stroke="#0F766E" stroke-width="1"/>
        <text x="14" y="392" fill="#5EEAD4" font-size="12.5" font-weight="700">❄️ Snowflake Hierarchy Outriggers</text>
        <text x="14" y="414" fill="#99F6E4" font-size="10.5">1. dim_geography: 22 Governorates ➔ 5 Economic Regions</text>
        <text x="14" y="432" fill="#CCFBF1" font-size="10">   Greater Cairo | Alexandria &amp; Delta | Canal | Upper Egypt | Red Sea</text>
        <text x="14" y="450" fill="#CCFBF1" font-size="10">   Courier SLA Tiers (24h Express, 48h Standard, 72h Extended)</text>
        <text x="14" y="470" fill="#99F6E4" font-size="10.5">2. dim_category: Product ➔ Subcategory ➔ Strategic Margin Class</text>
        <text x="14" y="488" fill="#CCFBF1" font-size="10">   Skincare (High Margin 65%) | Haircare (55%) | Fragrance (70%)</text>
        <text x="14" y="508" fill="#99F6E4" font-size="10.5">3. dim_telecom_carrier: Vodafone, Orange, Etisalat, WE Egypt</text>
      </g>
    </g>

    <!-- Warehouse Load Stored Procedures -->
    <g transform="translate(20, 1195)">
      <rect width="380" height="120" rx="10" fill="#062419" stroke="#059669" stroke-width="1"/>
      <text x="14" y="24" fill="#6EE7B7" font-size="12" font-weight="700">⚡ Warehouse Loader Stored Procedures</text>
      <text x="14" y="44" fill="#D1FAE5" font-size="10.5">• warehouse.usp_load_dimensions: SCD2 Merge &amp; Key Lookup</text>
      <text x="14" y="62" fill="#D1FAE5" font-size="10.5">• warehouse.usp_load_facts: Incremental Sales, Inventory, Targets</text>
      <text x="14" y="80" fill="#D1FAE5" font-size="10.5">• Referential integrity enforced via foreign keys &amp; constraints</text>
      <text x="14" y="100" fill="#34D399" font-size="10" font-weight="700">Zero Dirty Data Guarantee | Pure Analytical Grain</text>
    </g>
  </g>

  <!-- ==================================================== -->
  <!-- COLUMN 6: MARTS & POWER BI (X: 2190, W: 350)         -->
  <!-- ==================================================== -->
  <g transform="translate(2190, 185)" filter="url(#shadowLg)">
    <rect width="350" height="1350" rx="16" fill="url(#cardGrad)" stroke="#1E293B" stroke-width="1.5"/>
    <rect x="0" y="0" width="350" height="5" rx="2.5" fill="url(#purpleGlow)"/>

    <!-- Column Header -->
    <g transform="translate(20, 24)">
      <circle cx="20" cy="20" r="18" fill="#7C3AED" fill-opacity="0.3"/>
      <text x="20" y="26" font-size="18" text-anchor="middle" fill="#C084FC">06</text>
      <text x="48" y="18" fill="#F8FAFC" font-size="16" font-weight="800">MARTS &amp; POWER BI</text>
      <text x="48" y="36" fill="#C084FC" font-size="11.5" font-weight="600">Curated Marts &amp; Semantic Model</text>
    </g>

    <!-- Curated Marts Section -->
    <g transform="translate(20, 75)">
      <text x="0" y="16" fill="#F8FAFC" font-size="13.5" font-weight="700">7 Curated Business Marts (mart.*)</text>

      <g transform="translate(0, 28)">
        <!-- Mart 1 -->
        <rect width="310" height="48" rx="6" fill="#0F172A" stroke="#4C1D95" stroke-width="1"/>
        <text x="12" y="20" fill="#DDD6FE" font-size="11" font-weight="700">mart.mart_daily_sales</text>
        <text x="220" y="20" fill="#C084FC" font-size="10" font-weight="700">271.6k Rows</text>
        <text x="12" y="36" fill="#94A3B8" font-size="9.5">Date × Store × Channel daily aggregation</text>

        <!-- Mart 2 -->
        <rect y="54" width="310" height="48" rx="6" fill="#0F172A" stroke="#4C1D95" stroke-width="1"/>
        <text x="12" y="74" fill="#DDD6FE" font-size="11" font-weight="700">mart.mart_monthly_sales</text>
        <text x="240" y="74" fill="#C084FC" font-size="10" font-weight="700">425 Rows</text>
        <text x="12" y="90" fill="#94A3B8" font-size="9.5">Executive monthly revenue &amp; quota tracking</text>

        <!-- Mart 3 -->
        <rect y="108" width="310" height="48" rx="6" fill="#0F172A" stroke="#4C1D95" stroke-width="1"/>
        <text x="12" y="128" fill="#DDD6FE" font-size="11" font-weight="700">mart.mart_product_performance</text>
        <text x="250" y="128" fill="#C084FC" font-size="10" font-weight="700">20 SKUs</text>
        <text x="12" y="144" fill="#94A3B8" font-size="9.5">Margin %, velocity, return rates, domestic rank</text>

        <!-- Mart 4 -->
        <rect y="162" width="310" height="48" rx="6" fill="#0F172A" stroke="#4C1D95" stroke-width="1"/>
        <text x="12" y="182" fill="#DDD6FE" font-size="11" font-weight="700">mart.mart_rfm (Customer Retention)</text>
        <text x="235" y="182" fill="#C084FC" font-size="10" font-weight="700">24.8k Scored</text>
        <text x="12" y="198" fill="#94A3B8" font-size="9.5">Champions, Loyal, At-Risk, Lost clusters</text>

        <!-- Mart 5 -->
        <rect y="216" width="310" height="48" rx="6" fill="#0F172A" stroke="#4C1D95" stroke-width="1"/>
        <text x="12" y="236" fill="#DDD6FE" font-size="11" font-weight="700">mart.mart_inventory_health</text>
        <text x="240" y="236" fill="#C084FC" font-size="10" font-weight="700">8.3k Rows</text>
        <text x="12" y="252" fill="#94A3B8" font-size="9.5">Stockout risk flag, Days of Inventory, damage %</text>

        <!-- Mart 6 & 7 -->
        <rect y="270" width="310" height="48" rx="6" fill="#0F172A" stroke="#4C1D95" stroke-width="1"/>
        <text x="12" y="290" fill="#DDD6FE" font-size="11" font-weight="700">mart.mart_marketing_roi &amp; health</text>
        <text x="245" y="290" fill="#C084FC" font-size="10" font-weight="700">8 Campaigns</text>
        <text x="12" y="306" fill="#94A3B8" font-size="9.5">ROAS, incremental revenue, pipeline SLA audit</text>
      </g>
    </g>

    <!-- Power BI Semantic Model Section -->
    <g transform="translate(20, 440)">
      <rect width="310" height="340" rx="12" fill="#150E28" stroke="#6D28D9" stroke-width="1.2"/>
      
      <g transform="translate(16, 20)">
        <text x="0" y="16" fill="#FAF5FF" font-size="13" font-weight="700">Power BI Tabular (.pbip)</text>
        <text x="0" y="34" fill="#C084FC" font-size="10.5">Cleopatra_Cosmetics_Report.pbip</text>

        <!-- M Query Group Lifecycle -->
        <g transform="translate(0, 46)">
          <rect width="278" height="95" rx="8" fill="#0F091D" stroke="#4C1D95" stroke-width="0.8"/>
          <text x="10" y="20" fill="#E9D5FF" font-size="11" font-weight="700">M Query Groups Lifecycle:</text>
          <text x="10" y="38" fill="#C084FC" font-size="10">00_Parameters ➔ Base paths &amp; thresholds</text>
          <text x="10" y="54" fill="#C084FC" font-size="10">01_Source ➔ Raw extracts</text>
          <text x="10" y="70" fill="#C084FC" font-size="10">02_Staging ➔ Types | 04_Cleansed ➔ Standardized</text>
          <text x="10" y="86" fill="#34D399" font-size="10" font-weight="600">05_Facts &amp; 06_Dimensions ➔ 07_Model</text>
        </g>

        <!-- DAX Folders -->
        <g transform="translate(0, 150)">
          <rect width="278" height="150" rx="8" fill="#0F091D" stroke="#4C1D95" stroke-width="0.8"/>
          <text x="10" y="20" fill="#E9D5FF" font-size="11" font-weight="700">55+ DAX Measures in 6 Folders:</text>
          <text x="10" y="40" fill="#DDD6FE" font-size="10">📁 01 Financials: Gross, Net Sales, Margin %</text>
          <text x="10" y="58" fill="#DDD6FE" font-size="10">📁 02 Targets: Quota, % Achievement, Variance</text>
          <text x="10" y="76" fill="#DDD6FE" font-size="10">📁 03 Customer RFM: CLV, Repeat Rate, Churn</text>
          <text x="10" y="94" fill="#DDD6FE" font-size="10">📁 04 Inventory: DOI, Stockout Risk SKUs</text>
          <text x="10" y="112" fill="#DDD6FE" font-size="10">📁 05 FX Normalized: USD &amp; EUR Central Bank</text>
          <text x="10" y="130" fill="#DDD6FE" font-size="10">📁 06 Time Intel: YTD, MoM %, YoY %, 3M Rolling</text>
        </g>
      </g>
    </g>

    <!-- Power BI Report Pages Suite -->
    <g transform="translate(20, 800)">
      <rect width="310" height="515" rx="12" fill="#0A0614" stroke="#4C1D95" stroke-width="1.2"/>
      
      <g transform="translate(16, 20)">
        <text x="0" y="16" fill="#FAF5FF" font-size="13" font-weight="700">Executive Reporting Suite</text>
        <text x="0" y="34" fill="#C084FC" font-size="10.5">5 C-Suite Power BI Report Canvas Pages</text>

        <g transform="translate(0, 48)">
          <!-- Page 1 -->
          <rect width="278" height="74" rx="8" fill="#130D24" stroke="#581C87" stroke-width="0.8"/>
          <text x="10" y="22" fill="#F3E8FF" font-size="11.5" font-weight="700">1. 🏛️ Executive Pulse Scorecard</text>
          <text x="10" y="40" fill="#DDD6FE" font-size="10">• Net Sales EGP, Margin %, MoM Growth</text>
          <text x="10" y="56" fill="#DDD6FE" font-size="10">• Daily sales trend, Top SKUs &amp; Target Gauge</text>

          <!-- Page 2 -->
          <rect y="82" width="278" height="74" rx="8" fill="#130D24" stroke="#581C87" stroke-width="0.8"/>
          <text x="10" y="104" fill="#F3E8FF" font-size="11.5" font-weight="700">2. 🗺️ Egypt Regional Penetration</text>
          <text x="10" y="122" fill="#DDD6FE" font-size="10">• 22 Governorates Geographic Drilldown</text>
          <text x="10" y="138" fill="#DDD6FE" font-size="10">• 5 Economic Regions &amp; Courier SLA Latency</text>

          <!-- Page 3 -->
          <rect y="164" width="278" height="74" rx="8" fill="#130D24" stroke="#581C87" stroke-width="0.8"/>
          <text x="10" y="186" fill="#F3E8FF" font-size="11.5" font-weight="700">3. 👥 Customer RFM &amp; Retention</text>
          <text x="10" y="204" fill="#DDD6FE" font-size="10">• 24.8k Customers RFM Heatmap Matrix</text>
          <text x="10" y="220" fill="#DDD6FE" font-size="10">• Telecom Carrier share &amp; Age Cohort LTV</text>

          <!-- Page 4 -->
          <rect y="246" width="278" height="74" rx="8" fill="#130D24" stroke="#581C87" stroke-width="0.8"/>
          <text x="10" y="268" fill="#F3E8FF" font-size="11.5" font-weight="700">4. 📦 Inventory Health &amp; Stockout</text>
          <text x="10" y="286" fill="#DDD6FE" font-size="10">• Stockout risk warning by store &amp; product</text>
          <text x="10" y="302" fill="#DDD6FE" font-size="10">• Days of Inventory (DOI) &amp; Damage %</text>

          <!-- Page 5 -->
          <rect y="328" width="278" height="85" rx="8" fill="#130D24" stroke="#581C87" stroke-width="0.8"/>
          <text x="10" y="350" fill="#F3E8FF" font-size="11.5" font-weight="700">5. 🎯 Targets &amp; Campaign ROAS</text>
          <text x="10" y="368" fill="#DDD6FE" font-size="10">• Store Monthly Achievement vs Target</text>
          <text x="10" y="384" fill="#DDD6FE" font-size="10">• Marketing Campaign ROAS &amp; Uplift %</text>
          <text x="10" y="400" fill="#34D399" font-size="9.5" font-weight="600">Full Executive Cross-Filtering &amp; Bookmarks</text>
        </g>
      </g>
    </g>
  </g>

  <!-- ========================================== -->
  <!-- BOTTOM SYSTEM FOOTER                       -->
  <!-- ========================================== -->
  <g transform="translate(60, 1550)">
    <rect width="2480" height="35" rx="6" fill="#080D1A" stroke="#1E293B" stroke-width="1"/>
    <text x="20" y="22" fill="#64748B" font-size="11">
      Platform: SQL Server 2022 | Python 3.11 ELT | Kimball Galaxy Dimensional Model | Slowly Changing Dimensions (SCD Type 2) | Data Quality Sentinel &amp; Quarantine
    </text>
    <text x="2460" y="22" fill="#94A3B8" font-size="11" font-weight="600" text-anchor="end">
      Cleopatra Modern Cosmetics (كليوباترا كوزماتكس) • Production BI Engineering Blueprint v2.0
    </text>
  </g>
</svg>'''

def main():
    svg_content = build_svg_content()
    svg_path = "docs/diagrams/project_lifecycle.svg"
    png_path = "docs/diagrams/project_lifecycle.png"

    # Write SVG
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {svg_path} ({len(svg_content)} bytes)")

    # Render PNG using cairosvg
    cairosvg.svg2png(bytestring=svg_content.encode("utf-8"), write_to=png_path, output_width=2600, output_height=1600)
    print(f"Rendered {png_path} ({os.path.getsize(png_path)} bytes)")

if __name__ == "__main__":
    main()
