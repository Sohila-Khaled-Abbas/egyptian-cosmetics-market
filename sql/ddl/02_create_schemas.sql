-- ==============================================================================
-- 02_create_schemas.sql
-- Egyptian Cosmetics Analytics Engineering Platform
-- Create Architectural Schemas (Idempotent)
-- ==============================================================================

USE egyptian_cosmetics_dw;
GO

-- 1. BRONZE: Raw source ingestion layer (preserves source fidelity and metadata)
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = N'bronze')
    EXEC('CREATE SCHEMA bronze');
GO

-- 2. STAGING: Standardized, typed, and cleansed preparation layer
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = N'staging')
    EXEC('CREATE SCHEMA staging');
GO

-- 3. WAREHOUSE: Kimball Star Schema Dimensions and Fact Tables
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = N'warehouse')
    EXEC('CREATE SCHEMA warehouse');
GO

-- 4. MART: Curated, reporting-ready Analytical Marts for Power BI
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = N'mart')
    EXEC('CREATE SCHEMA mart');
GO

-- 5. DQ: Data Quality Rules, Execution Results, and Quarantined Rejects
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = N'dq')
    EXEC('CREATE SCHEMA dq');
GO

-- 6. AUDIT: Pipeline Runs, Execution Steps, and Incremental Watermarks
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = N'audit')
    EXEC('CREATE SCHEMA audit');
GO

PRINT 'All architectural schemas created successfully: bronze, staging, warehouse, mart, dq, audit.';
GO
