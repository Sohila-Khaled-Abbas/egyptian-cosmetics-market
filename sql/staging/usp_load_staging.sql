-- ==============================================================================
-- usp_load_staging.sql
-- Egyptian Cosmetics Analytics Engineering Platform
-- Stored Procedure: Standardize and Load Bronze Data into Staging
-- ==============================================================================

USE egyptian_cosmetics_dw;
GO

IF OBJECT_ID('staging.usp_load_staging', 'P') IS NOT NULL DROP PROCEDURE staging.usp_load_staging;
GO

CREATE PROCEDURE staging.usp_load_staging
    @BatchID NVARCHAR(100) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @BatchID IS NULL
        SET @BatchID = 'BATCH_' + FORMAT(SYSUTCDATETIME(), 'yyyyMMdd_HHmmss');

    PRINT 'Executing staging.usp_load_staging for BatchID: ' + @BatchID;

    -- --------------------------------------------------------------------------
    -- 1. STAGING CUSTOMERS (Phone clean, email lowercase, trim)
    -- --------------------------------------------------------------------------
    TRUNCATE TABLE staging.stg_customers;

    INSERT INTO staging.stg_customers (
        customer_id, customer_name_ar, customer_name_en, gender, birth_year,
        governorate_raw, governorate_clean, area, phone_raw, phone_clean,
        email_raw, email_clean, signup_date, customer_segment,
        source_system, batch_id, ingestion_timestamp, row_hash
    )
    SELECT
        TRIM(customer_id),
        TRIM(customer_name_ar),
        TRIM(customer_name_en),
        TRIM(gender),
        TRY_CAST(birth_year AS INT),
        governorate,
        -- Standardize governorate casing
        CASE 
            WHEN LOWER(TRIM(governorate)) = 'cairo' THEN 'Cairo'
            WHEN LOWER(TRIM(governorate)) = 'giza' THEN 'Giza'
            WHEN LOWER(TRIM(governorate)) = 'alexandria' THEN 'Alexandria'
            WHEN LOWER(TRIM(governorate)) = 'sohag' THEN 'Sohag'
            ELSE TRIM(governorate)
        END,
        NULLIF(TRIM(area), ''),
        phone,
        -- Phone normalization: strip spaces and convert +20 10... to 010...
        CASE 
            WHEN phone IS NULL OR TRIM(phone) = '' THEN NULL
            WHEN REPLACE(REPLACE(phone, ' ', ''), '+20', '0') LIKE '01%' 
            THEN REPLACE(REPLACE(phone, ' ', ''), '+20', '0')
            ELSE REPLACE(phone, ' ', '')
        END,
        email,
        LOWER(NULLIF(TRIM(email), '')),
        TRY_CAST(signup_date AS DATE),
        TRIM(customer_segment),
        source_system,
        @BatchID,
        ingestion_timestamp,
        row_hash
    FROM bronze.raw_customers;

    -- --------------------------------------------------------------------------
    -- 2. STAGING PRODUCTS (Currency normalization)
    -- --------------------------------------------------------------------------
    TRUNCATE TABLE staging.stg_products;

    INSERT INTO staging.stg_products (
        product_id, product_name_en, product_name_ar, brand_en, brand_ar,
        category, subcategory, list_price_egp, standard_cost_egp,
        currency_raw, currency_clean, origin,
        source_system, batch_id, ingestion_timestamp, row_hash
    )
    SELECT
        TRIM(product_id),
        TRIM(product_name_en),
        TRIM(product_name_ar),
        TRIM(brand_en),
        TRIM(brand_ar),
        TRIM(category),
        TRIM(subcategory),
        TRY_CAST(list_price_egp AS DECIMAL(12,2)),
        TRY_CAST(standard_cost_egp AS DECIMAL(12,2)),
        currency,
        -- Standardize currency aliases
        CASE 
            WHEN TRIM(currency) IN ('EGP', 'EGP ', N'جنيه', N'جنيه مصري') THEN 'EGP'
            ELSE TRIM(currency)
        END,
        TRIM(origin),
        source_system,
        @BatchID,
        ingestion_timestamp,
        row_hash
    FROM bronze.raw_products;

    -- --------------------------------------------------------------------------
    -- 3. STAGING STORES
    -- --------------------------------------------------------------------------
    TRUNCATE TABLE staging.stg_stores;

    INSERT INTO staging.stg_stores (
        store_id, store_name_en, store_name_ar, governorate_raw, governorate_clean,
        area, store_type, distribution_region,
        source_system, batch_id, ingestion_timestamp, row_hash
    )
    SELECT
        TRIM(store_id),
        TRIM(store_name_en),
        TRIM(store_name_ar),
        governorate,
        TRIM(governorate),
        TRIM(area),
        TRIM(store_type),
        TRIM(distribution_region),
        source_system,
        @BatchID,
        ingestion_timestamp,
        row_hash
    FROM bronze.raw_stores;

    -- --------------------------------------------------------------------------
    -- 4. STAGING ORDERS (Order date key, status casing, currency clean)
    -- --------------------------------------------------------------------------
    TRUNCATE TABLE staging.stg_orders;

    INSERT INTO staging.stg_orders (
        order_id, order_datetime, order_date, order_date_key, customer_id,
        product_id, store_id, campaign_id, sales_channel_en, sales_channel_ar,
        payment_method_en, payment_method_ar, quantity, unit_price_egp, discount_pct,
        gross_sales_egp, discount_egp, net_sales_egp, cost_egp,
        order_status_raw, order_status_clean, currency_raw, currency_clean,
        source_system, batch_id, ingestion_timestamp, row_hash
    )
    SELECT
        TRIM(order_id),
        TRY_CAST(order_datetime AS DATETIME2),
        TRY_CAST(order_datetime AS DATE),
        CASE 
            WHEN TRY_CAST(order_datetime AS DATE) IS NOT NULL 
            THEN YEAR(TRY_CAST(order_datetime AS DATE)) * 10000 + 
                 MONTH(TRY_CAST(order_datetime AS DATE)) * 100 + 
                 DAY(TRY_CAST(order_datetime AS DATE))
            ELSE 19000101
        END,
        TRIM(customer_id),
        TRIM(product_id),
        TRIM(store_id),
        TRIM(campaign_id),
        TRIM(sales_channel_en),
        TRIM(sales_channel_ar),
        TRIM(payment_method_en),
        TRIM(payment_method_ar),
        TRY_CAST(quantity AS INT),
        TRY_CAST(unit_price_egp AS DECIMAL(12,2)),
        TRY_CAST(discount_pct AS DECIMAL(5,4)),
        TRY_CAST(gross_sales_egp AS DECIMAL(12,2)),
        TRY_CAST(discount_egp AS DECIMAL(12,2)),
        TRY_CAST(net_sales_egp AS DECIMAL(12,2)),
        TRY_CAST(cost_egp AS DECIMAL(12,2)),
        order_status,
        -- Status Normalization
        CASE 
            WHEN LOWER(TRIM(order_status)) IN ('completed', 'complete', N'مكتمل') THEN 'Completed'
            WHEN LOWER(TRIM(order_status)) IN ('cancelled', 'canceled', N'ملغي') THEN 'Cancelled'
            WHEN LOWER(TRIM(order_status)) IN ('returned', N'مرتجع') THEN 'Returned'
            ELSE 'Pending'
        END,
        currency,
        CASE 
            WHEN TRIM(currency) IN ('EGP', 'EGP ', N'جنيه', N'جنيه مصري') THEN 'EGP'
            ELSE TRIM(currency)
        END,
        source_system,
        @BatchID,
        ingestion_timestamp,
        row_hash
    FROM bronze.raw_orders;

    -- --------------------------------------------------------------------------
    -- 5. STAGING INVENTORY
    -- --------------------------------------------------------------------------
    TRUNCATE TABLE staging.stg_inventory;

    INSERT INTO staging.stg_inventory (
        [month], month_date_key, store_id, product_id,
        opening_stock, received_qty, sold_qty, damaged_qty, closing_stock, net_stock_flow,
        source_system, batch_id, ingestion_timestamp, row_hash
    )
    SELECT
        TRY_CAST([month] AS DATE),
        YEAR(TRY_CAST([month] AS DATE)) * 10000 + MONTH(TRY_CAST([month] AS DATE)) * 100 + 1,
        TRIM(store_id),
        TRIM(product_id),
        TRY_CAST(opening_stock AS INT),
        TRY_CAST(received_qty AS INT),
        TRY_CAST(sold_qty AS INT),
        TRY_CAST(damaged_qty AS INT),
        TRY_CAST(closing_stock AS INT),
        TRY_CAST(received_qty AS INT) - TRY_CAST(sold_qty AS INT) - TRY_CAST(damaged_qty AS INT),
        source_system,
        @BatchID,
        ingestion_timestamp,
        row_hash
    FROM bronze.raw_inventory;

    -- --------------------------------------------------------------------------
    -- 6. STAGING TARGETS
    -- --------------------------------------------------------------------------
    TRUNCATE TABLE staging.stg_targets;

    INSERT INTO staging.stg_targets (
        target_month, target_date_key, store_id, sales_target_egp, order_target,
        source_system, batch_id, ingestion_timestamp, row_hash
    )
    SELECT
        TRY_CAST(target_month AS DATE),
        YEAR(TRY_CAST(target_month AS DATE)) * 10000 + MONTH(TRY_CAST(target_month AS DATE)) * 100 + 1,
        TRIM(store_id),
        TRY_CAST(sales_target_egp AS DECIMAL(14,2)),
        TRY_CAST(order_target AS INT),
        source_system,
        @BatchID,
        ingestion_timestamp,
        row_hash
    FROM bronze.raw_targets;

    -- --------------------------------------------------------------------------
    -- 7. STAGING CAMPAIGNS
    -- --------------------------------------------------------------------------
    TRUNCATE TABLE staging.stg_campaigns;

    INSERT INTO staging.stg_campaigns (
        campaign_id, campaign_name_en, campaign_name_ar, platform,
        budget_egp, expected_conversion_rate,
        source_system, batch_id, ingestion_timestamp, row_hash
    )
    SELECT
        TRIM(campaign_id),
        TRIM(campaign_name_en),
        TRIM(campaign_name_ar),
        TRIM(platform),
        TRY_CAST(budget_egp AS DECIMAL(12,2)),
        TRY_CAST(expected_conversion_rate AS DECIMAL(6,4)),
        source_system,
        @BatchID,
        ingestion_timestamp,
        row_hash
    FROM bronze.raw_campaigns;

    PRINT 'staging.usp_load_staging completed successfully.';
END;
GO
