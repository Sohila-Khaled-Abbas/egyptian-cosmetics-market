-- =====================================================================================
-- Stored Procedure: dq.usp_run_dq_checks
-- Purpose: Executes comprehensive data quality validations across staging tables,
--          records metric evaluation history in dq.data_quality_results,
--          and routes defective rows to dedicated quarantine tables.
-- =====================================================================================

USE [egyptian_cosmetics_dw];
GO

CREATE OR ALTER PROCEDURE [dq].[usp_run_dq_checks]
    @RunId NVARCHAR(100) = NULL,
    @BatchId NVARCHAR(100) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @RunId IS NULL SET @RunId = CAST(NEWID() AS NVARCHAR(100));
    IF @BatchId IS NULL SET @BatchId = @RunId;

    DECLARE @CheckTimestamp DATETIME2 = SYSUTCDATETIME();

    -- Clear previous quarantine data for fresh run
    TRUNCATE TABLE [dq].[rejected_orders];
    TRUNCATE TABLE [dq].[rejected_customers];
    TRUNCATE TABLE [dq].[rejected_inventory];
    TRUNCATE TABLE [dq].[rejected_targets];

    -- ============================================================================
    -- 1. ORDERS DATA QUALITY CHECKS & QUARANTINE
    -- ============================================================================
    INSERT INTO [dq].[rejected_orders] (
        [order_id], [order_datetime], [customer_id], [product_id], [store_id],
        [quantity], [unit_price_egp], [order_status], [currency],
        [rejection_reason], [rejection_severity], [quarantine_timestamp], [source_file], [batch_id]
    )
    SELECT 
        o.[order_id],
        CAST(o.[order_datetime] AS NVARCHAR(100)),
        o.[customer_id],
        o.[product_id],
        o.[store_id],
        CAST(o.[quantity] AS NVARCHAR(50)),
        CAST(o.[unit_price_egp] AS NVARCHAR(50)),
        o.[order_status_clean],
        o.[currency_clean],
        CONCAT_WS('; ',
            CASE WHEN o.[order_id] IS NULL THEN 'Missing Order ID' END,
            CASE WHEN dup.[cnt] > 1 THEN 'Duplicate Order ID' END,
            CASE WHEN c.[customer_id] IS NULL THEN 'Orphan Order - Customer ID not in Customer Master' END,
            CASE WHEN p.[product_id] IS NULL THEN 'Orphan Order - Product ID not in Product Master' END,
            CASE WHEN s.[store_id] IS NULL THEN 'Orphan Order - Store ID not in Store Master' END,
            CASE WHEN o.[quantity] <= 0 THEN 'Invalid Quantity (<= 0)' END,
            CASE WHEN o.[unit_price_egp] < 0 THEN 'Negative Unit Price' END,
            CASE WHEN o.[order_datetime] < '2020-01-01' THEN 'Legacy Date Anomaly (< 2020)' END,
            CASE WHEN o.[order_datetime] > CAST(SYSUTCDATETIME() AS DATE) THEN 'Future Dated Order' END
        ) AS [RejectionReason],
        'Critical',
        @CheckTimestamp,
        'orders.csv',
        @BatchId
    FROM [staging].[stg_orders] o
    LEFT JOIN (
        SELECT [order_id], COUNT(*) AS [cnt] 
        FROM [staging].[stg_orders] 
        GROUP BY [order_id]
    ) dup ON o.[order_id] = dup.[order_id]
    LEFT JOIN [staging].[stg_customers] c ON o.[customer_id] = c.[customer_id]
    LEFT JOIN [staging].[stg_products] p ON o.[product_id] = p.[product_id]
    LEFT JOIN [staging].[stg_stores] s ON o.[store_id] = s.[store_id]
    WHERE o.[order_id] IS NULL
       OR dup.[cnt] > 1
       OR c.[customer_id] IS NULL
       OR p.[product_id] IS NULL
       OR s.[store_id] IS NULL
       OR o.[quantity] <= 0
       OR o.[unit_price_egp] < 0
       OR o.[order_datetime] < '2020-01-01'
       OR o.[order_datetime] > CAST(SYSUTCDATETIME() AS DATE);

    -- ============================================================================
    -- 2. CUSTOMERS DATA QUALITY CHECKS & QUARANTINE
    -- ============================================================================
    INSERT INTO [dq].[rejected_customers] (
        [customer_id], [customer_name_ar], [customer_name_en], [phone], [email],
        [governorate], [rejection_reason], [quarantine_timestamp], [source_file], [batch_id]
    )
    SELECT 
        c.[customer_id],
        c.[customer_name_ar],
        c.[customer_name_en],
        c.[phone_clean],
        c.[email_clean],
        c.[governorate_clean],
        CONCAT_WS('; ',
            CASE WHEN c.[customer_id] IS NULL THEN 'Missing Customer ID' END,
            CASE WHEN dup.[cnt] > 1 THEN 'Duplicate Customer ID' END,
            CASE WHEN (c.[customer_name_ar] IS NULL OR LTRIM(RTRIM(c.[customer_name_ar])) = '')
                  AND (c.[customer_name_en] IS NULL OR LTRIM(RTRIM(c.[customer_name_en])) = '') THEN 'Missing Customer Name' END,
            CASE WHEN c.[phone_clean] IS NULL AND c.[email_clean] IS NULL THEN 'Missing Contact Info' END
        ) AS [RejectionReason],
        @CheckTimestamp,
        'customers.csv',
        @BatchId
    FROM [staging].[stg_customers] c
    LEFT JOIN (
        SELECT [customer_id], COUNT(*) AS [cnt]
        FROM [staging].[stg_customers]
        GROUP BY [customer_id]
    ) dup ON c.[customer_id] = dup.[customer_id]
    WHERE c.[customer_id] IS NULL
       OR dup.[cnt] > 1
       OR ((c.[customer_name_ar] IS NULL OR LTRIM(RTRIM(c.[customer_name_ar])) = '')
           AND (c.[customer_name_en] IS NULL OR LTRIM(RTRIM(c.[customer_name_en])) = ''));

    -- ============================================================================
    -- 3. INVENTORY DATA QUALITY CHECKS & QUARANTINE
    -- ============================================================================
    INSERT INTO [dq].[rejected_inventory] (
        [month], [store_id], [product_id], [opening_stock],
        [received_qty], [sold_qty], [damaged_qty], [closing_stock],
        [rejection_reason], [quarantine_timestamp], [source_file], [batch_id]
    )
    SELECT 
        CAST(i.[month] AS NVARCHAR(100)),
        i.[store_id],
        i.[product_id],
        CAST(i.[opening_stock] AS NVARCHAR(50)),
        CAST(i.[received_qty] AS NVARCHAR(50)),
        CAST(i.[sold_qty] AS NVARCHAR(50)),
        CAST(i.[damaged_qty] AS NVARCHAR(50)),
        CAST(i.[closing_stock] AS NVARCHAR(50)),
        CONCAT_WS('; ',
            CASE WHEN i.[closing_stock] < 0 THEN 'Negative Closing Stock' END,
            CASE WHEN i.[damaged_qty] < 0 THEN 'Negative Damaged Stock' END,
            CASE WHEN i.[sold_qty] > 10000 THEN 'Abnormal Sold Stock (> 10,000 units)' END,
            CASE WHEN s.[store_id] IS NULL THEN 'Orphan Inventory - Invalid Store ID' END,
            CASE WHEN p.[product_id] IS NULL THEN 'Orphan Inventory - Invalid Product ID' END
        ) AS [RejectionReason],
        @CheckTimestamp,
        'inventory_monthly.csv',
        @BatchId
    FROM [staging].[stg_inventory] i
    LEFT JOIN [staging].[stg_stores] s ON i.[store_id] = s.[store_id]
    LEFT JOIN [staging].[stg_products] p ON i.[product_id] = p.[product_id]
    WHERE i.[closing_stock] < 0
       OR i.[damaged_qty] < 0
       OR i.[sold_qty] > 10000
       OR s.[store_id] IS NULL
       OR p.[product_id] IS NULL;

    -- ============================================================================
    -- 4. TARGETS DATA QUALITY CHECKS & QUARANTINE
    -- ============================================================================
    INSERT INTO [dq].[rejected_targets] (
        [target_month], [store_id], [sales_target_egp], [order_target],
        [rejection_reason], [quarantine_timestamp], [source_file], [batch_id]
    )
    SELECT 
        CAST(t.[target_month] AS NVARCHAR(100)),
        t.[store_id],
        CAST(t.[sales_target_egp] AS NVARCHAR(50)),
        CAST(t.[order_target] AS NVARCHAR(50)),
        CONCAT_WS('; ',
            CASE WHEN dup.[cnt] > 1 THEN 'Duplicate Store-Month Target' END,
            CASE WHEN s.[store_id] IS NULL THEN 'Orphan Target - Invalid Store ID' END,
            CASE WHEN t.[sales_target_egp] <= 0 THEN 'Invalid Target Revenue (<= 0)' END
        ) AS [RejectionReason],
        @CheckTimestamp,
        'commercial_reference_data.xlsx::Targets',
        @BatchId
    FROM [staging].[stg_targets] t
    LEFT JOIN (
        SELECT [store_id], [target_month], COUNT(*) AS [cnt]
        FROM [staging].[stg_targets]
        GROUP BY [store_id], [target_month]
    ) dup ON t.[store_id] = dup.[store_id] AND t.[target_month] = dup.[target_month]
    LEFT JOIN [staging].[stg_stores] s ON t.[store_id] = s.[store_id]
    WHERE dup.[cnt] > 1
       OR s.[store_id] IS NULL
       OR t.[sales_target_egp] <= 0;

    -- ============================================================================
    -- 5. LOG DQ RESULTS TO dq.data_quality_results
    -- ============================================================================
    DECLARE @TotalOrders BIGINT, @FailedOrders BIGINT;
    SELECT @TotalOrders = COUNT(*) FROM [staging].[stg_orders];
    SELECT @FailedOrders = COUNT(*) FROM [dq].[rejected_orders];

    INSERT INTO [dq].[data_quality_results] (
        [run_id], [rule_id], [total_rows], [failed_rows], [failure_rate], [status], [error_sample_reference]
    )
    VALUES (
        @RunId, 'DQ_ORD_01', @TotalOrders, @FailedOrders,
        CASE WHEN @TotalOrders > 0 THEN CAST(ROUND(CAST(@FailedOrders AS FLOAT) / @TotalOrders, 4) AS DECIMAL(6,4)) ELSE 0.0000 END,
        CASE WHEN @FailedOrders = 0 THEN 'PASS' ELSE 'WARNING' END,
        'dq.rejected_orders'
    );

    DECLARE @TotalCust BIGINT, @FailedCust BIGINT;
    SELECT @TotalCust = COUNT(*) FROM [staging].[stg_customers];
    SELECT @FailedCust = COUNT(*) FROM [dq].[rejected_customers];

    INSERT INTO [dq].[data_quality_results] (
        [run_id], [rule_id], [total_rows], [failed_rows], [failure_rate], [status], [error_sample_reference]
    )
    VALUES (
        @RunId, 'DQ_CUST_01', @TotalCust, @FailedCust,
        CASE WHEN @TotalCust > 0 THEN CAST(ROUND(CAST(@FailedCust AS FLOAT) / @TotalCust, 4) AS DECIMAL(6,4)) ELSE 0.0000 END,
        CASE WHEN @FailedCust = 0 THEN 'PASS' ELSE 'WARNING' END,
        'dq.rejected_customers'
    );

    DECLARE @TotalInv BIGINT, @FailedInv BIGINT;
    SELECT @TotalInv = COUNT(*) FROM [staging].[stg_inventory];
    SELECT @FailedInv = COUNT(*) FROM [dq].[rejected_inventory];

    INSERT INTO [dq].[data_quality_results] (
        [run_id], [rule_id], [total_rows], [failed_rows], [failure_rate], [status], [error_sample_reference]
    )
    VALUES (
        @RunId, 'DQ_INV_01', @TotalInv, @FailedInv,
        CASE WHEN @TotalInv > 0 THEN CAST(ROUND(CAST(@FailedInv AS FLOAT) / @TotalInv, 4) AS DECIMAL(6,4)) ELSE 0.0000 END,
        CASE WHEN @FailedInv = 0 THEN 'PASS' ELSE 'WARNING' END,
        'dq.rejected_inventory'
    );

    DECLARE @TotalTgt BIGINT, @FailedTgt BIGINT;
    SELECT @TotalTgt = COUNT(*) FROM [staging].[stg_targets];
    SELECT @FailedTgt = COUNT(*) FROM [dq].[rejected_targets];

    INSERT INTO [dq].[data_quality_results] (
        [run_id], [rule_id], [total_rows], [failed_rows], [failure_rate], [status], [error_sample_reference]
    )
    VALUES (
        @RunId, 'DQ_TGT_01', @TotalTgt, @FailedTgt,
        CASE WHEN @TotalTgt > 0 THEN CAST(ROUND(CAST(@FailedTgt AS FLOAT) / @TotalTgt, 4) AS DECIMAL(6,4)) ELSE 0.0000 END,
        CASE WHEN @FailedTgt = 0 THEN 'PASS' ELSE 'WARNING' END,
        'dq.rejected_targets'
    );

    -- Return summary
    SELECT 
        r.[rule_id], r.[total_rows], r.[failed_rows], r.[failure_rate], r.[status], r.[error_sample_reference]
    FROM [dq].[data_quality_results] r
    WHERE r.[run_id] = @RunId;

END;
GO
