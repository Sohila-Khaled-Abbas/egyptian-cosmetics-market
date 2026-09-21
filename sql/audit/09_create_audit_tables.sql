-- ==============================================================================
-- 09_create_audit_tables.sql
-- Egyptian Cosmetics Analytics Engineering Platform
-- Audit Logging, Execution Traces, and Incremental Watermarks
-- ==============================================================================

USE egyptian_cosmetics_dw;
GO

-- Drop referencing table first
IF OBJECT_ID('audit.pipeline_steps', 'U') IS NOT NULL DROP TABLE audit.pipeline_steps;
GO

-- 1. PIPELINE RUNS (High-level execution log)
IF OBJECT_ID('audit.pipeline_runs', 'U') IS NOT NULL DROP TABLE audit.pipeline_runs;
CREATE TABLE audit.pipeline_runs (
    run_id NVARCHAR(100) PRIMARY KEY,
    pipeline_name NVARCHAR(100) NOT NULL,
    start_time DATETIME2 NOT NULL,
    end_time DATETIME2 NULL,
    duration_seconds DECIMAL(10,2) NULL,
    status NVARCHAR(20) NOT NULL, -- RUNNING, SUCCESS, FAILED, WARNING
    rows_read BIGINT DEFAULT 0,
    rows_inserted BIGINT DEFAULT 0,
    rows_updated BIGINT DEFAULT 0,
    rows_rejected BIGINT DEFAULT 0,
    error_message NVARCHAR(MAX) NULL,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME()
);
GO

-- 2. PIPELINE STEPS (Granular stage-level timing & row counts)
IF OBJECT_ID('audit.pipeline_steps', 'U') IS NOT NULL DROP TABLE audit.pipeline_steps;
CREATE TABLE audit.pipeline_steps (
    step_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    run_id NVARCHAR(100) NOT NULL REFERENCES audit.pipeline_runs(run_id),
    step_name NVARCHAR(100) NOT NULL, -- Extract, Bronze, Staging, DQ, Dimensions, Facts, Marts
    start_time DATETIME2 NOT NULL,
    end_time DATETIME2 NULL,
    duration_seconds DECIMAL(10,2) NULL,
    status NVARCHAR(20) NOT NULL,
    rows_processed BIGINT DEFAULT 0,
    error_message NVARCHAR(MAX) NULL
);
GO

-- 3. INCREMENTAL WATERMARKS (Tracks delta state for idempotent reruns)
IF OBJECT_ID('audit.watermarks', 'U') IS NOT NULL DROP TABLE audit.watermarks;
CREATE TABLE audit.watermarks (
    watermark_id INT IDENTITY(1,1) PRIMARY KEY,
    pipeline_name NVARCHAR(100) NOT NULL,
    source_name NVARCHAR(100) NOT NULL,
    table_name NVARCHAR(100) NOT NULL,
    last_successful_value NVARCHAR(100) NOT NULL, -- High-watermark timestamp, ID, or date
    updated_at DATETIME2 DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_audit_watermarks UNIQUE (pipeline_name, source_name, table_name)
);
GO

-- Seed Baseline Watermarks
INSERT INTO audit.watermarks (pipeline_name, source_name, table_name, last_successful_value) VALUES
('Cosmetics_ETL', 'Postgres_Operational', 'warehouse.fact_sales', '1900-01-01 00:00:00'),
('Cosmetics_ETL', 'Postgres_Operational', 'warehouse.dim_customer', '1900-01-01 00:00:00'),
('Cosmetics_ETL', 'WMS_Inventory_Logs', 'warehouse.fact_inventory', '1900-01-01');
GO

PRINT 'Audit logging and watermark tables created successfully.';
GO
