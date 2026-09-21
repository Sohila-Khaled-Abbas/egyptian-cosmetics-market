-- ==============================================================================
-- 06_create_facts.sql
-- Egyptian Cosmetics Analytics Engineering Platform
-- Warehouse Fact Tables (Transactional, Periodic Snapshot, Quotas)
-- ==============================================================================

USE egyptian_cosmetics_dw;
GO

-- 1. FACT SALES (Grain: One row per order line-item transaction)
IF OBJECT_ID('warehouse.fact_sales', 'U') IS NOT NULL DROP TABLE warehouse.fact_sales;
CREATE TABLE warehouse.fact_sales (
    sales_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    order_id NVARCHAR(50) NOT NULL,
    order_datetime DATETIME2 NOT NULL,
    date_key INT NOT NULL REFERENCES warehouse.dim_date(date_key),
    customer_key BIGINT NOT NULL REFERENCES warehouse.dim_customer(customer_key),
    product_key INT NOT NULL REFERENCES warehouse.dim_product(product_key),
    store_key INT NOT NULL REFERENCES warehouse.dim_store(store_key),
    campaign_key INT NOT NULL REFERENCES warehouse.dim_campaign(campaign_key),
    channel_key INT NOT NULL REFERENCES warehouse.dim_channel(channel_key),
    payment_method_key INT NOT NULL REFERENCES warehouse.dim_payment_method(payment_method_key),
    -- Transactional Measures
    quantity INT NOT NULL,
    unit_price_egp DECIMAL(12,2) NOT NULL,
    discount_pct DECIMAL(5,4) NOT NULL DEFAULT 0,
    gross_sales_egp DECIMAL(12,2) NOT NULL,
    discount_egp DECIMAL(12,2) NOT NULL,
    net_sales_egp DECIMAL(12,2) NOT NULL,
    cost_egp DECIMAL(12,2) NOT NULL,
    profit_egp DECIMAL(12,2) NOT NULL,
    margin_pct DECIMAL(6,4) NOT NULL,
    -- Degenerate Dimensions
    order_status NVARCHAR(50) NOT NULL,
    currency NVARCHAR(10) NOT NULL DEFAULT 'EGP',
    -- Audit Lineage
    batch_id NVARCHAR(100),
    created_at DATETIME2 DEFAULT SYSUTCDATETIME()
);
GO

-- Clustered/Nonclustered Indexes for FactSales
CREATE NONCLUSTERED INDEX IX_fact_sales_date_key ON warehouse.fact_sales(date_key);
CREATE NONCLUSTERED INDEX IX_fact_sales_customer_key ON warehouse.fact_sales(customer_key);
CREATE NONCLUSTERED INDEX IX_fact_sales_product_key ON warehouse.fact_sales(product_key);
CREATE NONCLUSTERED INDEX IX_fact_sales_store_key ON warehouse.fact_sales(store_key);
CREATE NONCLUSTERED INDEX IX_fact_sales_channel_key ON warehouse.fact_sales(channel_key);
CREATE NONCLUSTERED INDEX IX_fact_sales_order_id ON warehouse.fact_sales(order_id);
GO

-- 2. FACT INVENTORY (Grain: One row per store + product + month)
IF OBJECT_ID('warehouse.fact_inventory', 'U') IS NOT NULL DROP TABLE warehouse.fact_inventory;
CREATE TABLE warehouse.fact_inventory (
    inventory_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    month_date_key INT NOT NULL REFERENCES warehouse.dim_date(date_key),
    store_key INT NOT NULL REFERENCES warehouse.dim_store(store_key),
    product_key INT NOT NULL REFERENCES warehouse.dim_product(product_key),
    opening_stock INT NOT NULL,
    received_qty INT NOT NULL,
    sold_qty INT NOT NULL,
    damaged_qty INT NOT NULL,
    closing_stock INT NOT NULL,
    net_stock_flow INT NOT NULL,
    is_low_stock BIT NOT NULL,
    is_stockout BIT NOT NULL,
    -- Audit Lineage
    batch_id NVARCHAR(100),
    created_at DATETIME2 DEFAULT SYSUTCDATETIME()
);
GO

CREATE NONCLUSTERED INDEX IX_fact_inventory_lookup ON warehouse.fact_inventory(month_date_key, store_key, product_key);
GO

-- 3. FACT STORE TARGETS (Grain: One row per store + month)
IF OBJECT_ID('warehouse.fact_store_targets', 'U') IS NOT NULL DROP TABLE warehouse.fact_store_targets;
CREATE TABLE warehouse.fact_store_targets (
    target_key INT IDENTITY(1,1) PRIMARY KEY,
    target_date_key INT NOT NULL REFERENCES warehouse.dim_date(date_key),
    store_key INT NOT NULL REFERENCES warehouse.dim_store(store_key),
    sales_target_egp DECIMAL(14,2) NOT NULL,
    order_target INT NOT NULL,
    -- Audit Lineage
    batch_id NVARCHAR(100),
    created_at DATETIME2 DEFAULT SYSUTCDATETIME()
);
GO

CREATE NONCLUSTERED INDEX IX_fact_targets_lookup ON warehouse.fact_store_targets(target_date_key, store_key);
GO

PRINT 'Warehouse fact tables and indexes created successfully.';
GO
