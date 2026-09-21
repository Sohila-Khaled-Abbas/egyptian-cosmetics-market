-- ==============================================================================
-- 08_create_dq_tables.sql
-- Egyptian Cosmetics Analytics Engineering Platform
-- Data Quality Rules, Results, and Quarantine Rejection Tables
-- ==============================================================================

USE egyptian_cosmetics_dw;
GO

-- Drop referencing table first
IF OBJECT_ID('dq.data_quality_results', 'U') IS NOT NULL DROP TABLE dq.data_quality_results;
GO

-- 1. DATA QUALITY RULES REPOSITORY
IF OBJECT_ID('dq.data_quality_rules', 'U') IS NOT NULL DROP TABLE dq.data_quality_rules;
CREATE TABLE dq.data_quality_rules (
    rule_id NVARCHAR(50) PRIMARY KEY,
    table_name NVARCHAR(100) NOT NULL,
    column_name NVARCHAR(100) NOT NULL,
    rule_name NVARCHAR(255) NOT NULL,
    rule_type NVARCHAR(50) NOT NULL, -- Uniqueness, Referential, Range, Completeness, AcceptedValues
    severity NVARCHAR(20) NOT NULL,  -- Critical, Warning, Rejected
    threshold DECIMAL(5,4) DEFAULT 0.0, -- Max allowable failure rate
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME()
);
GO

-- 2. DATA QUALITY EXECUTION RESULTS LEDGER
IF OBJECT_ID('dq.data_quality_results', 'U') IS NOT NULL DROP TABLE dq.data_quality_results;
CREATE TABLE dq.data_quality_results (
    result_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    run_id NVARCHAR(100) NOT NULL,
    rule_id NVARCHAR(50) NOT NULL REFERENCES dq.data_quality_rules(rule_id),
    execution_time DATETIME2 DEFAULT SYSUTCDATETIME(),
    total_rows BIGINT NOT NULL,
    failed_rows BIGINT NOT NULL,
    failure_rate DECIMAL(6,4) NOT NULL,
    status NVARCHAR(20) NOT NULL, -- PASS, FAIL, WARNING
    error_sample_reference NVARCHAR(MAX)
);
GO

-- 3. QUARANTINE: REJECTED ORDERS
IF OBJECT_ID('dq.rejected_orders', 'U') IS NOT NULL DROP TABLE dq.rejected_orders;
CREATE TABLE dq.rejected_orders (
    rejection_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    order_id NVARCHAR(100),
    order_datetime NVARCHAR(100),
    customer_id NVARCHAR(100),
    product_id NVARCHAR(100),
    store_id NVARCHAR(100),
    quantity NVARCHAR(50),
    unit_price_egp NVARCHAR(50),
    order_status NVARCHAR(100),
    currency NVARCHAR(50),
    -- Rejection Reason & Traceability
    rejection_reason NVARCHAR(255) NOT NULL,
    rejection_severity NVARCHAR(20) DEFAULT 'Critical',
    quarantine_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    source_file NVARCHAR(255) DEFAULT 'orders.csv',
    batch_id NVARCHAR(100)
);
GO

-- 4. QUARANTINE: REJECTED CUSTOMERS
IF OBJECT_ID('dq.rejected_customers', 'U') IS NOT NULL DROP TABLE dq.rejected_customers;
CREATE TABLE dq.rejected_customers (
    rejection_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    customer_id NVARCHAR(100),
    customer_name_ar NVARCHAR(255),
    customer_name_en NVARCHAR(255),
    phone NVARCHAR(100),
    email NVARCHAR(255),
    governorate NVARCHAR(100),
    rejection_reason NVARCHAR(255) NOT NULL,
    quarantine_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    source_file NVARCHAR(255) DEFAULT 'customers.csv',
    batch_id NVARCHAR(100)
);
GO

-- 5. QUARANTINE: REJECTED INVENTORY
IF OBJECT_ID('dq.rejected_inventory', 'U') IS NOT NULL DROP TABLE dq.rejected_inventory;
CREATE TABLE dq.rejected_inventory (
    rejection_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    [month] NVARCHAR(100),
    store_id NVARCHAR(100),
    product_id NVARCHAR(100),
    opening_stock NVARCHAR(50),
    received_qty NVARCHAR(50),
    sold_qty NVARCHAR(50),
    damaged_qty NVARCHAR(50),
    closing_stock NVARCHAR(50),
    rejection_reason NVARCHAR(255) NOT NULL,
    quarantine_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    source_file NVARCHAR(255) DEFAULT 'inventory_monthly.csv',
    batch_id NVARCHAR(100)
);
GO

-- 6. QUARANTINE: REJECTED TARGETS
IF OBJECT_ID('dq.rejected_targets', 'U') IS NOT NULL DROP TABLE dq.rejected_targets;
CREATE TABLE dq.rejected_targets (
    rejection_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    target_month NVARCHAR(100),
    store_id NVARCHAR(100),
    sales_target_egp NVARCHAR(50),
    order_target NVARCHAR(50),
    rejection_reason NVARCHAR(255) NOT NULL,
    quarantine_timestamp DATETIME2 DEFAULT SYSUTCDATETIME(),
    source_file NVARCHAR(255) DEFAULT 'commercial_reference_data.xlsx::Targets',
    batch_id NVARCHAR(100)
);
GO

-- Seed Standard Quality Rules
INSERT INTO dq.data_quality_rules (rule_id, table_name, column_name, rule_name, rule_type, severity, threshold) VALUES
('DQ_ORD_01', 'staging.stg_orders', 'order_id', 'Order ID Uniqueness', 'Uniqueness', 'Critical', 0.0),
('DQ_ORD_02', 'staging.stg_orders', 'quantity', 'Order Quantity Strictly Positive (>0)', 'Range', 'Critical', 0.0),
('DQ_ORD_03', 'staging.stg_orders', 'unit_price_egp', 'Unit Price Strictly Positive (>0)', 'Range', 'Critical', 0.0),
('DQ_ORD_04', 'staging.stg_orders', 'customer_id', 'Customer FK Referential Integrity', 'Referential', 'Critical', 0.0),
('DQ_ORD_05', 'staging.stg_orders', 'product_id', 'Product FK Referential Integrity', 'Referential', 'Critical', 0.0),
('DQ_ORD_06', 'staging.stg_orders', 'store_id', 'Store FK Referential Integrity', 'Referential', 'Critical', 0.0),
('DQ_ORD_07', 'staging.stg_orders', 'order_datetime', 'Order Timestamp Within Business Window', 'Range', 'Critical', 0.0),
('DQ_CUST_01', 'staging.stg_customers', 'customer_id', 'Customer ID Uniqueness', 'Uniqueness', 'Critical', 0.0),
('DQ_INV_01', 'staging.stg_inventory', 'closing_stock', 'Non-Negative Closing Stock', 'Range', 'Critical', 0.0),
('DQ_INV_02', 'staging.stg_inventory', 'damaged_qty', 'Non-Negative Damaged Units', 'Range', 'Critical', 0.0),
('DQ_TGT_01', 'staging.stg_targets', 'store_id', 'Target Store-Month Compound Uniqueness', 'Uniqueness', 'Critical', 0.0);
GO

PRINT 'Data Quality repository and quarantine tables created successfully.';
GO
