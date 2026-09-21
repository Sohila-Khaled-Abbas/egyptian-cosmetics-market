-- ==============================================================================
-- 05_create_dimensions.sql
-- Egyptian Cosmetics Analytics Engineering Platform
-- Warehouse Dimension Tables (Kimball Star Schema + SCD Type 2)
-- ==============================================================================

USE egyptian_cosmetics_dw;
GO

-- Drop referencing fact tables first to avoid foreign key violations on re-run
IF OBJECT_ID('warehouse.fact_sales', 'U') IS NOT NULL DROP TABLE warehouse.fact_sales;
IF OBJECT_ID('warehouse.fact_inventory', 'U') IS NOT NULL DROP TABLE warehouse.fact_inventory;
IF OBJECT_ID('warehouse.fact_store_targets', 'U') IS NOT NULL DROP TABLE warehouse.fact_store_targets;
GO

-- 1. DIM DATE (Calendar Dimension)
IF OBJECT_ID('warehouse.dim_date', 'U') IS NOT NULL DROP TABLE warehouse.dim_date;
CREATE TABLE warehouse.dim_date (
    date_key INT PRIMARY KEY, -- Format: YYYYMMDD
    full_date DATE NOT NULL UNIQUE,
    [year] INT NOT NULL,
    month_number INT NOT NULL,
    month_name NVARCHAR(30) NOT NULL,
    month_short_name NVARCHAR(10) NOT NULL,
    month_name_ar NVARCHAR(30) NOT NULL,
    quarter NVARCHAR(5) NOT NULL,
    year_month NVARCHAR(10) NOT NULL,
    year_month_number INT NOT NULL,
    week_number INT NOT NULL,
    [day] INT NOT NULL,
    day_name NVARCHAR(30) NOT NULL,
    day_name_ar NVARCHAR(30) NOT NULL,
    is_weekend BIT NOT NULL -- Friday / Saturday in Egypt
);
GO

-- 2. DIM CUSTOMER (Slowly Changing Dimension Type 2)
IF OBJECT_ID('warehouse.dim_customer', 'U') IS NOT NULL DROP TABLE warehouse.dim_customer;
CREATE TABLE warehouse.dim_customer (
    customer_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    customer_id NVARCHAR(50) NOT NULL, -- Natural Business Key
    customer_name_ar NVARCHAR(255),
    customer_name_en NVARCHAR(255),
    gender NVARCHAR(20),
    birth_year INT,
    governorate NVARCHAR(100),
    area NVARCHAR(100),
    phone NVARCHAR(50),
    email NVARCHAR(255),
    signup_date DATE,
    customer_segment NVARCHAR(50),
    -- SCD Type 2 Tracking Fields
    valid_from DATETIME2 NOT NULL,
    valid_to DATETIME2 NULL, -- NULL = current active version
    is_current BIT NOT NULL DEFAULT 1,
    row_hash CHAR(64)
);
GO

CREATE NONCLUSTERED INDEX IX_dim_customer_lookup ON warehouse.dim_customer(customer_id, is_current);
GO

-- 3. DIM PRODUCT
IF OBJECT_ID('warehouse.dim_product', 'U') IS NOT NULL DROP TABLE warehouse.dim_product;
CREATE TABLE warehouse.dim_product (
    product_key INT IDENTITY(1,1) PRIMARY KEY,
    product_id NVARCHAR(50) NOT NULL UNIQUE, -- Natural Business Key
    product_name_en NVARCHAR(255) NOT NULL,
    product_name_ar NVARCHAR(255) NOT NULL,
    brand_en NVARCHAR(100),
    brand_ar NVARCHAR(100),
    category NVARCHAR(100) NOT NULL,
    subcategory NVARCHAR(100) NOT NULL,
    list_price_egp DECIMAL(12,2) NOT NULL,
    standard_cost_egp DECIMAL(12,2) NOT NULL,
    currency NVARCHAR(10) DEFAULT 'EGP',
    origin NVARCHAR(50)
);
GO

-- 4. DIM STORE
IF OBJECT_ID('warehouse.dim_store', 'U') IS NOT NULL DROP TABLE warehouse.dim_store;
CREATE TABLE warehouse.dim_store (
    store_key INT IDENTITY(1,1) PRIMARY KEY,
    store_id NVARCHAR(50) NOT NULL UNIQUE, -- Natural Business Key
    store_name_en NVARCHAR(255) NOT NULL,
    store_name_ar NVARCHAR(255) NOT NULL,
    governorate NVARCHAR(100) NOT NULL,
    area NVARCHAR(100),
    store_type NVARCHAR(50),
    distribution_region NVARCHAR(100)
);
GO

-- 5. DIM CAMPAIGN
IF OBJECT_ID('warehouse.dim_campaign', 'U') IS NOT NULL DROP TABLE warehouse.dim_campaign;
CREATE TABLE warehouse.dim_campaign (
    campaign_key INT IDENTITY(1,1) PRIMARY KEY,
    campaign_id NVARCHAR(50) NOT NULL UNIQUE,
    campaign_name_en NVARCHAR(255) NOT NULL,
    campaign_name_ar NVARCHAR(255) NOT NULL,
    platform NVARCHAR(100),
    budget_egp DECIMAL(12,2),
    expected_conversion_rate DECIMAL(6,4)
);
GO

-- 6. DIM CHANNEL
IF OBJECT_ID('warehouse.dim_channel', 'U') IS NOT NULL DROP TABLE warehouse.dim_channel;
CREATE TABLE warehouse.dim_channel (
    channel_key INT IDENTITY(1,1) PRIMARY KEY,
    channel_name_en NVARCHAR(100) NOT NULL UNIQUE,
    channel_name_ar NVARCHAR(100) NOT NULL,
    channel_group NVARCHAR(100) NOT NULL -- Digital Direct, Social Commerce, Marketplace, Physical Retail
);
GO

-- 7. DIM PAYMENT METHOD
IF OBJECT_ID('warehouse.dim_payment_method', 'U') IS NOT NULL DROP TABLE warehouse.dim_payment_method;
CREATE TABLE warehouse.dim_payment_method (
    payment_method_key INT IDENTITY(1,1) PRIMARY KEY,
    payment_method_name_en NVARCHAR(100) NOT NULL UNIQUE,
    payment_method_name_ar NVARCHAR(100) NOT NULL,
    payment_category NVARCHAR(100) NOT NULL,
    is_digital_payment BIT NOT NULL
);
GO

PRINT 'Warehouse dimension tables created successfully.';
GO
