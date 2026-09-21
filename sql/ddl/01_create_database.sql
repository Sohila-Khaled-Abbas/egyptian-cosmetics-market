-- ==============================================================================
-- 01_create_database.sql
-- Egyptian Cosmetics Analytics Engineering Platform
-- Database Creation Script (Idempotent)
-- ==============================================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'egyptian_cosmetics_dw')
BEGIN
    PRINT 'Creating database: egyptian_cosmetics_dw...';
    CREATE DATABASE egyptian_cosmetics_dw
    COLLATE Arabic_100_CI_AS; -- Supports bilingual Arabic and English case-insensitive search
    PRINT 'Database egyptian_cosmetics_dw created successfully.';
END
ELSE
BEGIN
    PRINT 'Database egyptian_cosmetics_dw already exists.';
END
GO

-- Enable Snapshot Isolation for high-concurrency analytical reads
ALTER DATABASE egyptian_cosmetics_dw SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE;
GO
