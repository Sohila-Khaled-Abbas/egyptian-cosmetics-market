-- =====================================================================================
-- Stored Procedure: warehouse.usp_load_facts
-- Purpose: Loads Kimball fact tables (fact_sales, fact_inventory, fact_store_targets),
--          resolving surrogate keys, applying point-in-time SCD2 lookups,
--          excluding quarantined records, and computing business measures.
-- =====================================================================================

USE [egyptian_cosmetics_dw];
GO

CREATE OR ALTER PROCEDURE [warehouse].[usp_load_facts]
    @BatchId NVARCHAR(100) = NULL,
    @IsIncremental BIT = 0
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @BatchId IS NULL SET @BatchId = CAST(NEWID() AS NVARCHAR(100));
    DECLARE @LoadTimestamp DATETIME2 = SYSUTCDATETIME();

    -- ============================================================================
    -- 1. LOAD fact_sales
    -- ============================================================================
    IF @IsIncremental = 0
    BEGIN
        TRUNCATE TABLE [warehouse].[fact_sales];
    END;

    INSERT INTO [warehouse].[fact_sales] (
        [order_id], [order_datetime], [date_key], [customer_key], [product_key],
        [store_key], [campaign_key], [channel_key], [payment_method_key],
        [quantity], [unit_price_egp], [discount_pct], [gross_sales_egp],
        [discount_egp], [net_sales_egp], [cost_egp], [profit_egp], [margin_pct],
        [order_status], [currency], [batch_id], [created_at]
    )
    SELECT 
        o.[order_id],
        o.[order_datetime],
        o.[order_date_key],
        -- SCD2 Point-in-time customer lookup with fallback to unknown (-1)
        ISNULL(c.[customer_key], -1) AS [customer_key],
        ISNULL(p.[product_key], -1) AS [product_key],
        ISNULL(s.[store_key], -1) AS [store_key],
        -1 AS [campaign_key],
        ISNULL(ch.[channel_key], -1) AS [channel_key],
        ISNULL(pm.[payment_method_key], -1) AS [payment_method_key],
        o.[quantity],
        o.[unit_price_egp],
        o.[discount_pct],
        o.[gross_sales_egp],
        o.[discount_egp],
        o.[net_sales_egp],
        o.[cost_egp],
        CAST(o.[net_sales_egp] - o.[cost_egp] AS DECIMAL(12, 2)) AS [profit_egp],
        CASE 
            WHEN o.[net_sales_egp] > 0 
            THEN ROUND(((o.[net_sales_egp] - o.[cost_egp]) / o.[net_sales_egp]), 4)
            ELSE 0 
        END AS [margin_pct],
        o.[order_status_clean],
        o.[currency_clean],
        @BatchId AS [batch_id],
        @LoadTimestamp AS [created_at]
    FROM [staging].[stg_orders] o
    -- Left join dim_customer on business key + temporal valid interval
    LEFT JOIN [warehouse].[dim_customer] c 
        ON o.[customer_id] = c.[customer_id]
       AND o.[order_datetime] >= c.[valid_from]
       AND (c.[valid_to] IS NULL OR o.[order_datetime] < c.[valid_to])
    LEFT JOIN [warehouse].[dim_product] p 
        ON o.[product_id] = p.[product_id]
    LEFT JOIN [warehouse].[dim_store] s 
        ON o.[store_id] = s.[store_id]
    LEFT JOIN [warehouse].[dim_channel] ch 
        ON o.[sales_channel_en] = ch.[channel_name_en]
    LEFT JOIN [warehouse].[dim_payment_method] pm 
        ON o.[payment_method_en] = pm.[payment_method_name_en]
    -- Strictly filter out any orders flagged as defective / quarantined
    WHERE o.[order_id] NOT IN (
        SELECT [order_id] FROM [dq].[rejected_orders] WHERE [order_id] IS NOT NULL
    )
    -- If incremental, avoid inserting already existing order IDs
    AND (
        @IsIncremental = 0 
        OR NOT EXISTS (SELECT 1 FROM [warehouse].[fact_sales] fs WHERE fs.[order_id] = o.[order_id])
    );

    -- ============================================================================
    -- 2. LOAD fact_inventory
    -- ============================================================================
    IF @IsIncremental = 0
    BEGIN
        TRUNCATE TABLE [warehouse].[fact_inventory];
    END;

    INSERT INTO [warehouse].[fact_inventory] (
        [month_date_key], [store_key], [product_key], [opening_stock],
        [received_qty], [sold_qty], [damaged_qty], [closing_stock],
        [net_stock_flow], [is_low_stock], [is_stockout], [batch_id], [created_at]
    )
    SELECT 
        i.[month_date_key],
        ISNULL(s.[store_key], -1) AS [store_key],
        ISNULL(p.[product_key], -1) AS [product_key],
        i.[opening_stock],
        i.[received_qty],
        i.[sold_qty],
        i.[damaged_qty],
        i.[closing_stock],
        i.[net_stock_flow],
        CASE WHEN i.[closing_stock] > 0 AND i.[closing_stock] <= 20 THEN 1 ELSE 0 END AS [is_low_stock],
        CASE WHEN i.[closing_stock] <= 0 THEN 1 ELSE 0 END AS [is_stockout],
        @BatchId AS [batch_id],
        @LoadTimestamp AS [created_at]
    FROM [staging].[stg_inventory] i
    LEFT JOIN [warehouse].[dim_store] s ON i.[store_id] = s.[store_id]
    LEFT JOIN [warehouse].[dim_product] p ON i.[product_id] = p.[product_id]
    WHERE NOT EXISTS (
        SELECT 1 FROM [dq].[rejected_inventory] r
        WHERE r.[store_id] = i.[store_id]
          AND r.[product_id] = i.[product_id]
          AND r.[month] = CAST(i.[month] AS NVARCHAR(100))
    );

    -- ============================================================================
    -- 3. LOAD fact_store_targets
    -- ============================================================================
    IF @IsIncremental = 0
    BEGIN
        TRUNCATE TABLE [warehouse].[fact_store_targets];
    END;

    INSERT INTO [warehouse].[fact_store_targets] (
        [target_date_key], [store_key], [sales_target_egp], [order_target], [batch_id], [created_at]
    )
    SELECT 
        t.[target_date_key],
        ISNULL(s.[store_key], -1) AS [store_key],
        t.[sales_target_egp],
        t.[order_target],
        @BatchId AS [batch_id],
        @LoadTimestamp AS [created_at]
    FROM [staging].[stg_targets] t
    LEFT JOIN [warehouse].[dim_store] s ON t.[store_id] = s.[store_id]
    WHERE NOT EXISTS (
        SELECT 1 FROM [dq].[rejected_targets] r
        WHERE r.[store_id] = t.[store_id]
          AND r.[target_month] = CAST(t.[target_month] AS NVARCHAR(100))
    );

END;
GO
