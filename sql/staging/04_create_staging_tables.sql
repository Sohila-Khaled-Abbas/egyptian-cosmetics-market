-- ==============================================================================
-- 04_create_staging_tables.sql
-- Egyptian Cosmetics Analytics Engineering Platform
-- Staging Layer Tables (Typed, Standardized, Preserving Lineage)
-- ==============================================================================

USE egyptian_cosmetics_dw;
GO

-- 1. STAGING CUSTOMERS
IF OBJECT_ID('staging.stg_customers', 'U') IS NOT NULL DROP TABLE staging.stg_customers;
CREATE TABLE staging.stg_customers (
    stg_customer_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    customer_id NVARCHAR(50) NOT NULL,
    customer_name_ar NVARCHAR(255),
    customer_name_en NVARCHAR(255),
    gender NVARCHAR(20),
    birth_year INT,
    governorate_raw NVARCHAR(100),
    governorate_clean NVARCHAR(100),
    area NVARCHAR(100),
    phone_raw NVARCHAR(100),
    phone_clean NVARCHAR(50),
    email_raw NVARCHAR(255),
    email_clean NVARCHAR(255),
    signup_date DATE,
    customer_segment NVARCHAR(50),
    -- Lineage
    source_system NVARCHAR(100),
    batch_id NVARCHAR(100),
    ingestion_timestamp DATETIME2,
    transformation_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    row_hash CHAR(64)
);
GO

-- 2. STAGING PRODUCTS
IF OBJECT_ID('staging.stg_products', 'U') IS NOT NULL DROP TABLE staging.stg_products;
CREATE TABLE staging.stg_products (
    stg_product_key INT IDENTITY(1,1) PRIMARY KEY,
    product_id NVARCHAR(50) NOT NULL,
    product_name_en NVARCHAR(255),
    product_name_ar NVARCHAR(255),
    brand_en NVARCHAR(100),
    brand_ar NVARCHAR(100),
    category NVARCHAR(100),
    subcategory NVARCHAR(100),
    list_price_egp DECIMAL(12,2),
    standard_cost_egp DECIMAL(12,2),
    currency_raw NVARCHAR(50),
    currency_clean NVARCHAR(10),
    origin NVARCHAR(50),
    -- Lineage
    source_system NVARCHAR(100),
    batch_id NVARCHAR(100),
    ingestion_timestamp DATETIME2,
    transformation_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    row_hash CHAR(64)
);
GO

-- 3. STAGING STORES
IF OBJECT_ID('staging.stg_stores', 'U') IS NOT NULL DROP TABLE staging.stg_stores;
CREATE TABLE staging.stg_stores (
    stg_store_key INT IDENTITY(1,1) PRIMARY KEY,
    store_id NVARCHAR(50) NOT NULL,
    store_name_en NVARCHAR(255),
    store_name_ar NVARCHAR(255),
    governorate_raw NVARCHAR(100),
    governorate_clean NVARCHAR(100),
    area NVARCHAR(100),
    store_type NVARCHAR(50),
    distribution_region NVARCHAR(100),
    -- Lineage
    source_system NVARCHAR(100),
    batch_id NVARCHAR(100),
    ingestion_timestamp DATETIME2,
    transformation_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    row_hash CHAR(64)
);
GO

-- 4. STAGING ORDERS (502,000 Source Records)
IF OBJECT_ID('staging.stg_orders', 'U') IS NOT NULL DROP TABLE staging.stg_orders;
CREATE TABLE staging.stg_orders (
    stg_order_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    order_id NVARCHAR(50) NOT NULL,
    order_datetime DATETIME2,
    order_date DATE,
    order_date_key INT,
    customer_id NVARCHAR(50),
    product_id NVARCHAR(50),
    store_id NVARCHAR(50),
    campaign_id NVARCHAR(50),
    sales_channel_en NVARCHAR(100),
    sales_channel_ar NVARCHAR(100),
    payment_method_en NVARCHAR(100),
    payment_method_ar NVARCHAR(100),
    quantity INT,
    unit_price_egp DECIMAL(12,2),
    discount_pct DECIMAL(5,4),
    gross_sales_egp DECIMAL(12,2),
    discount_egp DECIMAL(12,2),
    net_sales_egp DECIMAL(12,2),
    cost_egp DECIMAL(12,2),
    order_status_raw NVARCHAR(100),
    order_status_clean NVARCHAR(50),
    currency_raw NVARCHAR(50),
    currency_clean NVARCHAR(10),
    -- Lineage
    source_system NVARCHAR(100),
    batch_id NVARCHAR(100),
    ingestion_timestamp DATETIME2,
    transformation_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    row_hash CHAR(64)
);
GO

-- Index staging orders for fast DQ evaluation and warehouse joins
CREATE NONCLUSTERED INDEX IX_stg_orders_order_id ON staging.stg_orders(order_id);
CREATE NONCLUSTERED INDEX IX_stg_orders_customer_id ON staging.stg_orders(customer_id);
CREATE NONCLUSTERED INDEX IX_stg_orders_product_id ON staging.stg_orders(product_id);
CREATE NONCLUSTERED INDEX IX_stg_orders_store_id ON staging.stg_orders(store_id);
GO

-- 5. STAGING INVENTORY
IF OBJECT_ID('staging.stg_inventory', 'U') IS NOT NULL DROP TABLE staging.stg_inventory;
CREATE TABLE staging.stg_inventory (
    stg_inventory_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    [month] DATE,
    month_date_key INT,
    store_id NVARCHAR(50),
    product_id NVARCHAR(50),
    opening_stock INT,
    received_qty INT,
    sold_qty INT,
    damaged_qty INT,
    closing_stock INT,
    net_stock_flow INT,
    -- Lineage
    source_system NVARCHAR(100),
    batch_id NVARCHAR(100),
    ingestion_timestamp DATETIME2,
    transformation_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    row_hash CHAR(64)
);
GO

-- 6. STAGING TARGETS
IF OBJECT_ID('staging.stg_targets', 'U') IS NOT NULL DROP TABLE staging.stg_targets;
CREATE TABLE staging.stg_targets (
    stg_target_key INT IDENTITY(1,1) PRIMARY KEY,
    target_month DATE,
    target_date_key INT,
    store_id NVARCHAR(50),
    sales_target_egp DECIMAL(14,2),
    order_target INT,
    -- Lineage
    source_system NVARCHAR(100),
    batch_id NVARCHAR(100),
    ingestion_timestamp DATETIME2,
    transformation_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    row_hash CHAR(64)
);
GO

-- 7. STAGING CAMPAIGNS
IF OBJECT_ID('staging.stg_campaigns', 'U') IS NOT NULL DROP TABLE staging.stg_campaigns;
CREATE TABLE staging.stg_campaigns (
    stg_campaign_key INT IDENTITY(1,1) PRIMARY KEY,
    campaign_id NVARCHAR(50) NOT NULL,
    campaign_name_en NVARCHAR(255),
    campaign_name_ar NVARCHAR(255),
    platform NVARCHAR(100),
    budget_egp DECIMAL(12,2),
    expected_conversion_rate DECIMAL(6,4),
    -- Lineage
    source_system NVARCHAR(100),
    batch_id NVARCHAR(100),
    ingestion_timestamp DATETIME2,
    transformation_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    row_hash CHAR(64)
);
GO

PRINT 'Staging layer tables and indexes created successfully.';
GO
