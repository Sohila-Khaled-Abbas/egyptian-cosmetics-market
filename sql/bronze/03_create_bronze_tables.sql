-- ==============================================================================
-- 03_create_bronze_tables.sql
-- Egyptian Cosmetics Analytics Engineering Platform
-- Bronze Layer Tables (Raw, Lossless Ingestion with Lineage Metadata)
-- ==============================================================================

USE egyptian_cosmetics_dw;
GO

-- 1. BRONZE ORDERS (Transactional Fact Source)
IF OBJECT_ID('bronze.raw_orders', 'U') IS NOT NULL DROP TABLE bronze.raw_orders;
CREATE TABLE bronze.raw_orders (
    raw_order_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    order_id NVARCHAR(100),
    order_datetime NVARCHAR(100),
    customer_id NVARCHAR(100),
    product_id NVARCHAR(100),
    store_id NVARCHAR(100),
    campaign_id NVARCHAR(100),
    sales_channel_en NVARCHAR(100),
    sales_channel_ar NVARCHAR(100),
    payment_method_en NVARCHAR(100),
    payment_method_ar NVARCHAR(100),
    quantity NVARCHAR(50),
    unit_price_egp NVARCHAR(50),
    discount_pct NVARCHAR(50),
    gross_sales_egp NVARCHAR(50),
    discount_egp NVARCHAR(50),
    net_sales_egp NVARCHAR(50),
    cost_egp NVARCHAR(50),
    order_status NVARCHAR(100),
    currency NVARCHAR(50),
    -- Audit & Lineage Metadata
    source_system NVARCHAR(100) DEFAULT 'Postgres_Operational',
    source_file NVARCHAR(255) DEFAULT 'orders.csv',
    ingestion_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    batch_id NVARCHAR(100),
    row_hash CHAR(64)
);
GO

-- 2. BRONZE CUSTOMERS
IF OBJECT_ID('bronze.raw_customers', 'U') IS NOT NULL DROP TABLE bronze.raw_customers;
CREATE TABLE bronze.raw_customers (
    raw_customer_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    customer_id NVARCHAR(100),
    customer_name_ar NVARCHAR(255),
    customer_name_en NVARCHAR(255),
    gender NVARCHAR(50),
    birth_year NVARCHAR(50),
    governorate NVARCHAR(100),
    area NVARCHAR(100),
    phone NVARCHAR(100),
    email NVARCHAR(255),
    signup_date NVARCHAR(100),
    customer_segment NVARCHAR(100),
    -- Audit & Lineage Metadata
    source_system NVARCHAR(100) DEFAULT 'Postgres_Operational',
    source_file NVARCHAR(255) DEFAULT 'customers.csv',
    ingestion_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    batch_id NVARCHAR(100),
    row_hash CHAR(64)
);
GO

-- 3. BRONZE PRODUCTS
IF OBJECT_ID('bronze.raw_products', 'U') IS NOT NULL DROP TABLE bronze.raw_products;
CREATE TABLE bronze.raw_products (
    raw_product_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    product_id NVARCHAR(100),
    product_name_en NVARCHAR(255),
    product_name_ar NVARCHAR(255),
    brand_en NVARCHAR(100),
    brand_ar NVARCHAR(100),
    category NVARCHAR(100),
    subcategory NVARCHAR(100),
    list_price_egp NVARCHAR(50),
    standard_cost_egp NVARCHAR(50),
    currency NVARCHAR(50),
    origin NVARCHAR(50),
    -- Audit & Lineage Metadata
    source_system NVARCHAR(100) DEFAULT 'Postgres_Operational',
    source_file NVARCHAR(255) DEFAULT 'products.csv',
    ingestion_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    batch_id NVARCHAR(100),
    row_hash CHAR(64)
);
GO

-- 4. BRONZE STORES
IF OBJECT_ID('bronze.raw_stores', 'U') IS NOT NULL DROP TABLE bronze.raw_stores;
CREATE TABLE bronze.raw_stores (
    raw_store_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    store_id NVARCHAR(100),
    store_name_en NVARCHAR(255),
    store_name_ar NVARCHAR(255),
    governorate NVARCHAR(100),
    area NVARCHAR(100),
    store_type NVARCHAR(100),
    distribution_region NVARCHAR(100),
    -- Audit & Lineage Metadata
    source_system NVARCHAR(100) DEFAULT 'Postgres_Operational',
    source_file NVARCHAR(255) DEFAULT 'stores.csv',
    ingestion_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    batch_id NVARCHAR(100),
    row_hash CHAR(64)
);
GO

-- 5. BRONZE INVENTORY
IF OBJECT_ID('bronze.raw_inventory', 'U') IS NOT NULL DROP TABLE bronze.raw_inventory;
CREATE TABLE bronze.raw_inventory (
    raw_inventory_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    [month] NVARCHAR(100),
    store_id NVARCHAR(100),
    product_id NVARCHAR(100),
    opening_stock NVARCHAR(50),
    received_qty NVARCHAR(50),
    sold_qty NVARCHAR(50),
    damaged_qty NVARCHAR(50),
    closing_stock NVARCHAR(50),
    -- Audit & Lineage Metadata
    source_system NVARCHAR(100) DEFAULT 'WMS_Inventory_Logs',
    source_file NVARCHAR(255) DEFAULT 'inventory_monthly.csv',
    ingestion_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    batch_id NVARCHAR(100),
    row_hash CHAR(64)
);
GO

-- 6. BRONZE TARGETS (Excel Commercial Data)
IF OBJECT_ID('bronze.raw_targets', 'U') IS NOT NULL DROP TABLE bronze.raw_targets;
CREATE TABLE bronze.raw_targets (
    raw_target_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    target_month NVARCHAR(100),
    store_id NVARCHAR(100),
    sales_target_egp NVARCHAR(50),
    order_target NVARCHAR(50),
    -- Audit & Lineage Metadata
    source_system NVARCHAR(100) DEFAULT 'Commercial_Excel',
    source_file NVARCHAR(255) DEFAULT 'commercial_reference_data.xlsx::Targets',
    ingestion_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    batch_id NVARCHAR(100),
    row_hash CHAR(64)
);
GO

-- 7. BRONZE CAMPAIGNS (Excel Commercial Data)
IF OBJECT_ID('bronze.raw_campaigns', 'U') IS NOT NULL DROP TABLE bronze.raw_campaigns;
CREATE TABLE bronze.raw_campaigns (
    raw_campaign_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    campaign_id NVARCHAR(100),
    campaign_name_en NVARCHAR(255),
    campaign_name_ar NVARCHAR(255),
    platform NVARCHAR(100),
    budget_egp NVARCHAR(50),
    expected_conversion_rate NVARCHAR(50),
    -- Audit & Lineage Metadata
    source_system NVARCHAR(100) DEFAULT 'Commercial_Excel',
    source_file NVARCHAR(255) DEFAULT 'commercial_reference_data.xlsx::Campaigns',
    ingestion_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    batch_id NVARCHAR(100),
    row_hash CHAR(64)
);
GO

-- 8. BRONZE EXCHANGE RATES (JSON API Data)
IF OBJECT_ID('bronze.raw_exchange_rates', 'U') IS NOT NULL DROP TABLE bronze.raw_exchange_rates;
CREATE TABLE bronze.raw_exchange_rates (
    raw_rate_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    rate_date NVARCHAR(100),
    base_currency NVARCHAR(50),
    quote_currency NVARCHAR(50),
    exchange_rate NVARCHAR(50),
    api_endpoint NVARCHAR(255),
    api_response_code NVARCHAR(50),
    -- Audit & Lineage Metadata
    source_system NVARCHAR(100) DEFAULT 'CentralBank_FX_API',
    source_file NVARCHAR(255) DEFAULT 'exchange_rates.json',
    ingestion_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    batch_id NVARCHAR(100),
    row_hash CHAR(64)
);
GO

PRINT 'Bronze layer tables created successfully with metadata and row_hash columns.';
GO
