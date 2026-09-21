-- =====================================================================================
-- MASTER DEPLOYMENT SCRIPT: scripts/setup.sql
-- Egyptian Cosmetics Analytics Engineering Platform
-- Database: egyptian_cosmetics_dw
-- =====================================================================================
-- Usage in sqlcmd:
--   sqlcmd -S localhost -E -i scripts/setup.sql
-- Or via python:
--   python scripts/setup_database.py
-- =====================================================================================

PRINT '---------------------------------------------------------';
PRINT 'Starting Cleopatra Modern Cosmetics Data Warehouse Setup';
PRINT '---------------------------------------------------------';

-- 1. Create Database
:r sql/ddl/01_create_database.sql
GO

-- 2. Create Schemas
:r sql/ddl/02_create_schemas.sql
GO

-- 3. Create Bronze Tables
:r sql/bronze/03_create_bronze_tables.sql
GO

-- 4. Create Staging Tables
:r sql/staging/04_create_staging_tables.sql
GO

-- 5. Create Data Quality & Quarantine Tables
:r sql/dq/08_create_dq_tables.sql
GO

-- 6. Create Audit & Observability Tables
:r sql/audit/09_create_audit_tables.sql
GO

-- 7. Create Warehouse Dimensions
:r sql/warehouse/05_create_dimensions.sql
GO

-- 8. Create Warehouse Facts
:r sql/warehouse/06_create_facts.sql
GO

-- 9. Create Analytics Marts
:r sql/marts/07_create_marts.sql
GO

-- 10. Create Staging Loader Stored Procedure
:r sql/staging/usp_load_staging.sql
GO

-- 11. Create DQ Validation Stored Procedure
:r sql/dq/usp_run_dq_checks.sql
GO

-- 12. Create Dimension Loader Stored Procedure (with SCD2)
:r sql/warehouse/usp_load_dimensions.sql
GO

-- 13. Create Facts Loader Stored Procedure
:r sql/warehouse/usp_load_facts.sql
GO

PRINT '---------------------------------------------------------';
PRINT 'Setup completed successfully!';
PRINT '---------------------------------------------------------';
