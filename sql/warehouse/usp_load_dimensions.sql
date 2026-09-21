-- =====================================================================================
-- Stored Procedure: warehouse.usp_load_dimensions
-- Purpose: Populates dimension tables in the Kimball Star Schema, including:
--          - Calendar Date dimension (dim_date)
--          - Unknown member rows (-1) for referential resilience
--          - Type 1 dimensions (dim_product, dim_store, dim_campaign, dim_channel, dim_payment_method)
--          - Slowly Changing Dimension Type 2 (SCD2) for dim_customer
-- =====================================================================================

USE [egyptian_cosmetics_dw];
GO

CREATE OR ALTER PROCEDURE [warehouse].[usp_load_dimensions]
    @BatchId NVARCHAR(100) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @BatchId IS NULL SET @BatchId = CAST(NEWID() AS NVARCHAR(100));
    DECLARE @CurrentTimestamp DATETIME2 = SYSUTCDATETIME();

    -- ============================================================================
    -- 1. POPULATE dim_date (2024-01-01 to 2026-12-31)
    -- ============================================================================
    IF NOT EXISTS (SELECT 1 FROM [warehouse].[dim_date] WHERE [date_key] = 20250101)
    BEGIN
        DECLARE @StartDate DATE = '2024-01-01';
        DECLARE @EndDate DATE = '2026-12-31';

        WITH DateSequence AS (
            SELECT @StartDate AS [CalendarDate]
            UNION ALL
            SELECT DATEADD(DAY, 1, [CalendarDate])
            FROM DateSequence
            WHERE [CalendarDate] < @EndDate
        )
        INSERT INTO [warehouse].[dim_date] (
            [date_key], [full_date], [year], [month_number], [month_name],
            [month_short_name], [month_name_ar], [quarter], [year_month],
            [year_month_number], [week_number], [day], [day_name],
            [day_name_ar], [is_weekend]
        )
        SELECT 
            CAST(CONVERT(VARCHAR(8), [CalendarDate], 112) AS INT) AS [date_key],
            [CalendarDate] AS [full_date],
            YEAR([CalendarDate]) AS [year],
            MONTH([CalendarDate]) AS [month_number],
            DATENAME(MONTH, [CalendarDate]) AS [month_name],
            FORMAT([CalendarDate], 'MMM') AS [month_short_name],
            CASE MONTH([CalendarDate])
                WHEN 1 THEN N'يناير' WHEN 2 THEN N'فبراير' WHEN 3 THEN N'مارس'
                WHEN 4 THEN N'أبريل' WHEN 5 THEN N'مايو' WHEN 6 THEN N'يونيو'
                WHEN 7 THEN N'يوليو' WHEN 8 THEN N'أغسطس' WHEN 9 THEN N'سبتمبر'
                WHEN 10 THEN N'أكتوبر' WHEN 11 THEN N'نوفمبر' WHEN 12 THEN N'ديسمبر'
            END AS [month_name_ar],
            CONCAT('Q', DATEPART(QUARTER, [CalendarDate])) AS [quarter],
            FORMAT([CalendarDate], 'yyyy-MM') AS [year_month],
            (YEAR([CalendarDate]) * 100) + MONTH([CalendarDate]) AS [year_month_number],
            DATEPART(WEEK, [CalendarDate]) AS [week_number],
            DAY([CalendarDate]) AS [day],
            DATENAME(WEEKDAY, [CalendarDate]) AS [day_name],
            CASE DATEPART(WEEKDAY, [CalendarDate])
                WHEN 1 THEN N'الأحد' WHEN 2 THEN N'الإثنين' WHEN 3 THEN N'الثلاثاء'
                WHEN 4 THEN N'الأربعاء' WHEN 5 THEN N'الخميس' WHEN 6 THEN N'الجمعة'
                WHEN 7 THEN N'السبت'
            END AS [day_name_ar],
            -- In Egypt, Friday & Saturday are the weekend
            CASE WHEN DATEPART(WEEKDAY, [CalendarDate]) IN (6, 7) THEN 1 ELSE 0 END AS [is_weekend]
        FROM DateSequence
        OPTION (MAXRECURSION 2000);
    END;

    -- ============================================================================
    -- 2. UNKNOWN / DEFAULT MEMBERS (-1)
    -- ============================================================================
    SET IDENTITY_INSERT [warehouse].[dim_customer] ON;
    IF NOT EXISTS (SELECT 1 FROM [warehouse].[dim_customer] WHERE [customer_key] = -1)
    BEGIN
        INSERT INTO [warehouse].[dim_customer] (
            [customer_key], [customer_id], [customer_name_ar], [customer_name_en],
            [gender], [birth_year], [governorate], [area], [phone], [email],
            [signup_date], [customer_segment], [valid_from], [valid_to], [is_current], [row_hash]
        )
        VALUES (
            -1, 'UNKNOWN', N'عميل غير محدد', 'Unknown Customer',
            'Unknown', NULL, N'غير محدد', N'غير محدد', 'N/A', 'unknown@cleopatra.eg',
            '1900-01-01', 'Standard', '1900-01-01', NULL, 1, 'UNKNOWN_HASH'
        );
    END;
    SET IDENTITY_INSERT [warehouse].[dim_customer] OFF;

    SET IDENTITY_INSERT [warehouse].[dim_product] ON;
    IF NOT EXISTS (SELECT 1 FROM [warehouse].[dim_product] WHERE [product_key] = -1)
    BEGIN
        INSERT INTO [warehouse].[dim_product] (
            [product_key], [product_id], [product_name_en], [product_name_ar],
            [brand_en], [brand_ar], [category], [subcategory], [list_price_egp],
            [standard_cost_egp], [currency], [origin]
        )
        VALUES (
            -1, 'UNKNOWN', 'Unknown Product', N'منتج غير محدد',
            'Cleopatra', N'كليوباترا', 'General', 'General', 0.0, 0.0, 'EGP', 'Local'
        );
    END;
    SET IDENTITY_INSERT [warehouse].[dim_product] OFF;

    SET IDENTITY_INSERT [warehouse].[dim_store] ON;
    IF NOT EXISTS (SELECT 1 FROM [warehouse].[dim_store] WHERE [store_key] = -1)
    BEGIN
        INSERT INTO [warehouse].[dim_store] (
            [store_key], [store_id], [store_name_en], [store_name_ar],
            [governorate], [area], [store_type], [distribution_region]
        )
        VALUES (
            -1, 'UNKNOWN', 'Unknown Store', N'فرع غير محدد',
            N'غير محدد', N'غير محدد', 'Retail', 'Greater Cairo'
        );
    END;
    SET IDENTITY_INSERT [warehouse].[dim_store] OFF;

    SET IDENTITY_INSERT [warehouse].[dim_campaign] ON;
    IF NOT EXISTS (SELECT 1 FROM [warehouse].[dim_campaign] WHERE [campaign_key] = -1)
    BEGIN
        INSERT INTO [warehouse].[dim_campaign] (
            [campaign_key], [campaign_id], [campaign_name_en], [campaign_name_ar],
            [platform], [budget_egp], [expected_conversion_rate]
        )
        VALUES (
            -1, 'UNKNOWN', 'No Campaign / Organic', N'بدون حملة / طبيعي',
            'Organic', 0.0, 0.0
        );
    END;
    SET IDENTITY_INSERT [warehouse].[dim_campaign] OFF;

    SET IDENTITY_INSERT [warehouse].[dim_channel] ON;
    IF NOT EXISTS (SELECT 1 FROM [warehouse].[dim_channel] WHERE [channel_key] = -1)
    BEGIN
        INSERT INTO [warehouse].[dim_channel] (
            [channel_key], [channel_name_en], [channel_name_ar], [channel_group]
        )
        VALUES (-1, 'Unknown', N'غير محدد', 'Direct');
    END;
    SET IDENTITY_INSERT [warehouse].[dim_channel] OFF;

    SET IDENTITY_INSERT [warehouse].[dim_payment_method] ON;
    IF NOT EXISTS (SELECT 1 FROM [warehouse].[dim_payment_method] WHERE [payment_method_key] = -1)
    BEGIN
        INSERT INTO [warehouse].[dim_payment_method] (
            [payment_method_key], [payment_method_name_en], [payment_method_name_ar],
            [payment_category], [is_digital_payment]
        )
        VALUES (-1, 'Unknown', N'غير محدد', 'Cash', 0);
    END;
    SET IDENTITY_INSERT [warehouse].[dim_payment_method] OFF;

    -- ============================================================================
    -- 3. SEED CHANNELS AND PAYMENT METHODS
    -- ============================================================================
    MERGE [warehouse].[dim_channel] AS tgt
    USING (
        SELECT 'Online Store' AS [en], N'المتجر الإلكتروني' AS [ar], 'Digital Direct' AS [grp] UNION ALL
        SELECT 'Mobile App', N'تطبيق الهاتف', 'Digital Direct' UNION ALL
        SELECT 'Retail Store', N'المتجر الفعلي', 'Physical Retail' UNION ALL
        SELECT 'Pharmacy Partner', N'شركاء الصيدليات', 'Physical Retail' UNION ALL
        SELECT 'Wholesale', N'توزيع جملة', 'Physical Retail' UNION ALL
        SELECT 'Amazon Egypt', N'أمازون مصر', 'Marketplace' UNION ALL
        SELECT 'Noon Egypt', N'نون مصر', 'Marketplace' UNION ALL
        SELECT 'TikTok Shop', N'تيك توك شوب', 'Social Commerce' UNION ALL
        SELECT 'Instagram Direct', N'إنستغرام مباشر', 'Social Commerce'
    ) AS src ON tgt.[channel_name_en] = src.[en]
    WHEN NOT MATCHED THEN
        INSERT ([channel_name_en], [channel_name_ar], [channel_group])
        VALUES (src.[en], src.[ar], src.[grp]);

    MERGE [warehouse].[dim_payment_method] AS tgt
    USING (
        SELECT 'Cash on Delivery' AS [en], N'الدفع عند الاستلام' AS [ar], 'Cash' AS [cat], 0 AS [dig] UNION ALL
        SELECT 'Credit Card', N'بطاقة ائتمان', 'Card' AS [cat], 1 AS [dig] UNION ALL
        SELECT 'Debit Card', N'بطاقة خصم مباشر', 'Card' AS [cat], 1 AS [dig] UNION ALL
        SELECT 'Meeza', N'ميزة', 'Card' AS [cat], 1 AS [dig] UNION ALL
        SELECT 'Vodafone Cash', N'فودافون كاش', 'Mobile Wallet' AS [cat], 1 AS [dig] UNION ALL
        SELECT 'InstaPay', N'إنستاباي', 'Instant Transfer' AS [cat], 1 AS [dig] UNION ALL
        SELECT 'Fawry', N'فوري', 'POS Network' AS [cat], 1 AS [dig] UNION ALL
        SELECT 'ValU', N'ڤاليو (تقسيط)', 'BNPL' AS [cat], 1 AS [dig]
    ) AS src ON tgt.[payment_method_name_en] = src.[en]
    WHEN NOT MATCHED THEN
        INSERT ([payment_method_name_en], [payment_method_name_ar], [payment_category], [is_digital_payment])
        VALUES (src.[en], src.[ar], src.[cat], src.[dig]);

    -- ============================================================================
    -- 4. UPSERT dim_product (Type 1)
    -- ============================================================================
    MERGE [warehouse].[dim_product] AS tgt
    USING [staging].[stg_products] AS src
    ON tgt.[product_id] = src.[product_id]
    WHEN MATCHED AND (
        tgt.[product_name_en] <> src.[product_name_en]
        OR tgt.[product_name_ar] <> src.[product_name_ar]
        OR tgt.[category] <> src.[category]
        OR tgt.[list_price_egp] <> src.[list_price_egp]
        OR tgt.[standard_cost_egp] <> src.[standard_cost_egp]
    ) THEN
        UPDATE SET
            tgt.[product_name_en] = src.[product_name_en],
            tgt.[product_name_ar] = src.[product_name_ar],
            tgt.[brand_en] = src.[brand_en],
            tgt.[brand_ar] = src.[brand_ar],
            tgt.[category] = src.[category],
            tgt.[subcategory] = src.[subcategory],
            tgt.[list_price_egp] = src.[list_price_egp],
            tgt.[standard_cost_egp] = src.[standard_cost_egp],
            tgt.[currency] = 'EGP',
            tgt.[origin] = src.[origin]
    WHEN NOT MATCHED THEN
        INSERT (
            [product_id], [product_name_en], [product_name_ar], [brand_en], [brand_ar],
            [category], [subcategory], [list_price_egp], [standard_cost_egp], [currency], [origin]
        )
        VALUES (
            src.[product_id], src.[product_name_en], src.[product_name_ar], src.[brand_en], src.[brand_ar],
            src.[category], src.[subcategory], src.[list_price_egp], src.[standard_cost_egp], 'EGP', src.[origin]
        );

    -- ============================================================================
    -- 5. UPSERT dim_store (Type 1)
    -- ============================================================================
    MERGE [warehouse].[dim_store] AS tgt
    USING [staging].[stg_stores] AS src
    ON tgt.[store_id] = src.[store_id]
    WHEN MATCHED AND (
        tgt.[store_name_en] <> src.[store_name_en]
        OR tgt.[store_name_ar] <> src.[store_name_ar]
        OR tgt.[governorate] <> src.[governorate_clean]
        OR tgt.[area] <> src.[area]
        OR tgt.[store_type] <> src.[store_type]
        OR tgt.[distribution_region] <> src.[distribution_region]
    ) THEN
        UPDATE SET
            tgt.[store_name_en] = src.[store_name_en],
            tgt.[store_name_ar] = src.[store_name_ar],
            tgt.[governorate] = src.[governorate_clean],
            tgt.[area] = src.[area],
            tgt.[store_type] = src.[store_type],
            tgt.[distribution_region] = src.[distribution_region]
    WHEN NOT MATCHED THEN
        INSERT (
            [store_id], [store_name_en], [store_name_ar], [governorate],
            [area], [store_type], [distribution_region]
        )
        VALUES (
            src.[store_id], src.[store_name_en], src.[store_name_ar], src.[governorate_clean],
            src.[area], src.[store_type], src.[distribution_region]
        );

    -- ============================================================================
    -- 6. UPSERT dim_campaign (Type 1)
    -- ============================================================================
    MERGE [warehouse].[dim_campaign] AS tgt
    USING [staging].[stg_campaigns] AS src
    ON tgt.[campaign_id] = src.[campaign_id]
    WHEN MATCHED AND (
        tgt.[campaign_name_en] <> src.[campaign_name_en]
        OR tgt.[campaign_name_ar] <> src.[campaign_name_ar]
        OR tgt.[platform] <> src.[platform]
        OR tgt.[budget_egp] <> src.[budget_egp]
    ) THEN
        UPDATE SET
            tgt.[campaign_name_en] = src.[campaign_name_en],
            tgt.[campaign_name_ar] = src.[campaign_name_ar],
            tgt.[platform] = src.[platform],
            tgt.[budget_egp] = src.[budget_egp],
            tgt.[expected_conversion_rate] = src.[expected_conversion_rate]
    WHEN NOT MATCHED THEN
        INSERT (
            [campaign_id], [campaign_name_en], [campaign_name_ar], [platform],
            [budget_egp], [expected_conversion_rate]
        )
        VALUES (
            src.[campaign_id], src.[campaign_name_en], src.[campaign_name_ar], src.[platform],
            src.[budget_egp], src.[expected_conversion_rate]
        );

    -- ============================================================================
    -- 7. SCD TYPE 2 FOR dim_customer
    -- ============================================================================
    ;WITH DeduplicatedStaging AS (
        SELECT 
            [customer_id], [customer_name_ar], [customer_name_en], [gender], [birth_year],
            [governorate_clean], [area], [phone_clean], [email_clean], [signup_date], [customer_segment],
            ROW_NUMBER() OVER (PARTITION BY [customer_id] ORDER BY [ingestion_timestamp] DESC) AS [rn]
        FROM [staging].[stg_customers]
        WHERE [customer_id] NOT IN (SELECT [customer_id] FROM [dq].[rejected_customers] WHERE [customer_id] IS NOT NULL)
    ),
    ValidStaging AS (
        SELECT * FROM DeduplicatedStaging WHERE [rn] = 1
    )
    -- Step A: Expire historical rows where governorate, area, or segment changed
    UPDATE tgt
    SET 
        tgt.[valid_to] = @CurrentTimestamp,
        tgt.[is_current] = 0
    FROM [warehouse].[dim_customer] tgt
    INNER JOIN ValidStaging src ON tgt.[customer_id] = src.[customer_id]
    WHERE tgt.[is_current] = 1
      AND (
          ISNULL(tgt.[governorate], '') <> ISNULL(src.[governorate_clean], '')
          OR ISNULL(tgt.[area], '') <> ISNULL(src.[area], '')
          OR ISNULL(tgt.[customer_segment], '') <> ISNULL(src.[customer_segment], '')
      );

    -- Step B: Insert active current row for new or changed customers
    ;WITH DeduplicatedStaging AS (
        SELECT 
            [customer_id], [customer_name_ar], [customer_name_en], [gender], [birth_year],
            [governorate_clean], [area], [phone_clean], [email_clean], [signup_date], [customer_segment],
            ROW_NUMBER() OVER (PARTITION BY [customer_id] ORDER BY [ingestion_timestamp] DESC) AS [rn]
        FROM [staging].[stg_customers]
        WHERE [customer_id] NOT IN (SELECT [customer_id] FROM [dq].[rejected_customers] WHERE [customer_id] IS NOT NULL)
    ),
    ValidStaging AS (
        SELECT * FROM DeduplicatedStaging WHERE [rn] = 1
    )
    INSERT INTO [warehouse].[dim_customer] (
        [customer_id], [customer_name_ar], [customer_name_en], [gender], [birth_year],
        [governorate], [area], [phone], [email], [signup_date], [customer_segment],
        [valid_from], [valid_to], [is_current], [row_hash]
    )
    SELECT 
        src.[customer_id],
        src.[customer_name_ar],
        src.[customer_name_en],
        ISNULL(src.[gender], 'Unknown'),
        src.[birth_year],
        src.[governorate_clean],
        src.[area],
        src.[phone_clean],
        src.[email_clean],
        ISNULL(src.[signup_date], CAST(SYSUTCDATETIME() AS DATE)),
        src.[customer_segment],
        @CurrentTimestamp AS [valid_from],
        NULL AS [valid_to],
        1 AS [is_current],
        CONVERT(CHAR(64), HASHBYTES('SHA2_256', CONCAT(src.[customer_id], src.[customer_name_en], src.[governorate_clean], src.[area], src.[customer_segment])), 2) AS [row_hash]
    FROM ValidStaging src
    LEFT JOIN [warehouse].[dim_customer] tgt 
        ON src.[customer_id] = tgt.[customer_id] AND tgt.[is_current] = 1
    WHERE tgt.[customer_id] IS NULL;

END;
GO
