-- ==============================================================================
-- 07_create_marts.sql
-- Egyptian Cosmetics Analytics Engineering Platform
-- Analytics Marts & Observability Views (Optimized for Power BI Direct/Import)
-- ==============================================================================

USE egyptian_cosmetics_dw;
GO

-- 1. MART: DAILY SALES
IF OBJECT_ID('mart.mart_daily_sales', 'V') IS NOT NULL DROP VIEW mart.mart_daily_sales;
GO
CREATE VIEW mart.mart_daily_sales AS
SELECT 
    d.full_date AS order_date,
    d.[year],
    d.month_name,
    d.month_name_ar,
    d.year_month,
    s.store_name_en,
    s.governorate,
    ch.channel_name_en,
    ch.channel_group,
    p.category,
    p.product_name_en,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    SUM(f.gross_sales_egp) AS total_gross_sales,
    SUM(f.discount_egp) AS total_discount,
    SUM(f.net_sales_egp) AS total_net_sales,
    SUM(f.cost_egp) AS total_cost,
    SUM(f.profit_egp) AS total_profit,
    CASE 
        WHEN SUM(f.net_sales_egp) > 0 
        THEN ROUND(SUM(f.profit_egp) / SUM(f.net_sales_egp), 4) 
        ELSE 0 
    END AS gross_margin_pct
FROM warehouse.fact_sales f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_store s ON f.store_key = s.store_key
JOIN warehouse.dim_channel ch ON f.channel_key = ch.channel_key
JOIN warehouse.dim_product p ON f.product_key = p.product_key
WHERE f.order_status = 'Completed'
GROUP BY 
    d.full_date, d.[year], d.month_name, d.month_name_ar, d.year_month,
    s.store_name_en, s.governorate, ch.channel_name_en, ch.channel_group,
    p.category, p.product_name_en;
GO

-- 2. MART: MONTHLY SALES & TARGET ACHIEVEMENT
IF OBJECT_ID('mart.mart_monthly_sales', 'V') IS NOT NULL DROP VIEW mart.mart_monthly_sales;
GO
CREATE VIEW mart.mart_monthly_sales AS
WITH Actuals AS (
    SELECT 
        d.[year],
        d.month_number,
        d.year_month,
        f.store_key,
        COUNT(DISTINCT f.order_id) AS completed_orders,
        SUM(f.quantity) AS units_sold,
        SUM(f.net_sales_egp) AS actual_net_sales,
        SUM(f.profit_egp) AS actual_profit
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_date d ON f.date_key = d.date_key
    WHERE f.order_status = 'Completed'
    GROUP BY d.[year], d.month_number, d.year_month, f.store_key
),
Targets AS (
    SELECT 
        d.[year],
        d.month_number,
        d.year_month,
        t.store_key,
        SUM(t.sales_target_egp) AS target_sales_egp,
        SUM(t.order_target) AS target_orders
    FROM warehouse.fact_store_targets t
    JOIN warehouse.dim_date d ON t.target_date_key = d.date_key
    GROUP BY d.[year], d.month_number, d.year_month, t.store_key
)
SELECT 
    COALESCE(a.[year], t.[year]) AS [year],
    COALESCE(a.month_number, t.month_number) AS month_number,
    COALESCE(a.year_month, t.year_month) AS year_month,
    s.store_id,
    s.store_name_en,
    s.store_name_ar,
    s.governorate,
    s.distribution_region,
    COALESCE(a.completed_orders, 0) AS completed_orders,
    COALESCE(t.target_orders, 0) AS target_orders,
    COALESCE(a.units_sold, 0) AS units_sold,
    COALESCE(a.actual_net_sales, 0) AS actual_net_sales_egp,
    COALESCE(t.target_sales_egp, 0) AS sales_target_egp,
    ROUND(COALESCE(a.actual_net_sales, 0) - COALESCE(t.target_sales_egp, 0), 2) AS sales_variance_egp,
    CASE 
        WHEN COALESCE(t.target_sales_egp, 0) > 0 
        THEN ROUND(COALESCE(a.actual_net_sales, 0) / t.target_sales_egp, 4) 
        ELSE 0 
    END AS target_achievement_pct,
    COALESCE(a.actual_profit, 0) AS gross_profit_egp
FROM Actuals a
FULL OUTER JOIN Targets t 
    ON a.year_month = t.year_month AND a.store_key = t.store_key
JOIN warehouse.dim_store s 
    ON COALESCE(a.store_key, t.store_key) = s.store_key;
GO

-- 3. MART: PRODUCT PERFORMANCE & PROFITABILITY
IF OBJECT_ID('mart.mart_product_performance', 'V') IS NOT NULL DROP VIEW mart.mart_product_performance;
GO
CREATE VIEW mart.mart_product_performance AS
SELECT 
    p.product_id,
    p.product_name_en,
    p.product_name_ar,
    p.brand_en,
    p.brand_ar,
    p.category,
    p.subcategory,
    p.origin,
    p.list_price_egp,
    p.standard_cost_egp,
    COUNT(DISTINCT f.order_id) AS orders_count,
    SUM(f.quantity) AS total_units_sold,
    SUM(f.gross_sales_egp) AS total_gross_sales,
    SUM(f.discount_egp) AS total_discount,
    SUM(f.net_sales_egp) AS total_net_sales,
    SUM(f.cost_egp) AS total_cogs,
    SUM(f.profit_egp) AS total_gross_profit,
    ROUND(AVG(f.discount_pct), 4) AS avg_discount_pct,
    CASE 
        WHEN SUM(f.net_sales_egp) > 0 
        THEN ROUND(SUM(f.profit_egp) / SUM(f.net_sales_egp), 4) 
        ELSE 0 
    END AS gross_margin_pct
FROM warehouse.fact_sales f
JOIN warehouse.dim_product p ON f.product_key = p.product_key
WHERE f.order_status = 'Completed'
GROUP BY 
    p.product_id, p.product_name_en, p.product_name_ar, p.brand_en, p.brand_ar,
    p.category, p.subcategory, p.origin, p.list_price_egp, p.standard_cost_egp;
GO

-- 4. MART: CUSTOMER RFM & SEGMENTATION
IF OBJECT_ID('mart.mart_rfm', 'V') IS NOT NULL DROP VIEW mart.mart_rfm;
GO
CREATE VIEW mart.mart_rfm AS
WITH CustomerStats AS (
    SELECT 
        c.customer_key,
        c.customer_id,
        c.customer_name_en,
        c.customer_name_ar,
        c.governorate,
        c.customer_segment,
        MAX(f.order_datetime) AS last_order_date,
        DATEDIFF(DAY, MAX(f.order_datetime), '2025-12-31') AS recency_days,
        COUNT(DISTINCT f.order_id) AS frequency_orders,
        SUM(f.net_sales_egp) AS monetary_spend
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_customer c ON f.customer_key = c.customer_key
    WHERE f.order_status = 'Completed' AND c.is_current = 1
    GROUP BY 
        c.customer_key, c.customer_id, c.customer_name_en, c.customer_name_ar,
        c.governorate, c.customer_segment
),
Scored AS (
    SELECT 
        *,
        CASE 
            WHEN recency_days <= 45 THEN 5
            WHEN recency_days <= 90 THEN 4
            WHEN recency_days <= 150 THEN 3
            WHEN recency_days <= 240 THEN 2
            ELSE 1
        END AS r_score,
        CASE 
            WHEN frequency_orders >= 28 THEN 5
            WHEN frequency_orders >= 20 THEN 4
            WHEN frequency_orders >= 14 THEN 3
            WHEN frequency_orders >= 8 THEN 2
            ELSE 1
        END AS f_score,
        CASE 
            WHEN monetary_spend >= 24000 THEN 5
            WHEN monetary_spend >= 17000 THEN 4
            WHEN monetary_spend >= 11500 THEN 3
            WHEN monetary_spend >= 6000 THEN 2
            ELSE 1
        END AS m_score
    FROM CustomerStats
)
SELECT 
    customer_key,
    customer_id,
    customer_name_en,
    customer_name_ar,
    governorate,
    customer_segment,
    last_order_date,
    recency_days,
    frequency_orders,
    monetary_spend,
    r_score,
    f_score,
    m_score,
    CAST(CONCAT(r_score, f_score, m_score) AS INT) AS rfm_score,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Potential Loyalists'
        WHEN r_score <= 3 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk'
        WHEN r_score = 1 AND f_score <= 2 THEN 'Lost Customers'
        ELSE 'Hibernating'
    END AS rfm_segment
FROM Scored;
GO

-- 5. MART: INVENTORY HEALTH & STOCKOUT RISK
IF OBJECT_ID('mart.mart_inventory_health', 'V') IS NOT NULL DROP VIEW mart.mart_inventory_health;
GO
CREATE VIEW mart.mart_inventory_health AS
SELECT 
    d.year_month,
    s.store_name_en,
    s.governorate,
    p.category,
    p.product_name_en,
    inv.opening_stock,
    inv.received_qty,
    inv.sold_qty,
    inv.damaged_qty,
    inv.closing_stock,
    ROUND(inv.closing_stock * p.standard_cost_egp, 2) AS closing_stock_valuation_egp,
    ROUND(inv.damaged_qty * p.standard_cost_egp, 2) AS damaged_stock_loss_egp,
    inv.is_low_stock,
    inv.is_stockout,
    CASE 
        WHEN (inv.opening_stock + inv.received_qty) > 0 
        THEN ROUND(CAST(inv.sold_qty AS FLOAT) / (inv.opening_stock + inv.received_qty), 4)
        ELSE 0 
    END AS sell_through_rate_pct
FROM warehouse.fact_inventory inv
JOIN warehouse.dim_date d ON inv.month_date_key = d.date_key
JOIN warehouse.dim_store s ON inv.store_key = s.store_key
JOIN warehouse.dim_product p ON inv.product_key = p.product_key;
GO

-- 6. MART: CAMPAIGN PERFORMANCE
IF OBJECT_ID('mart.mart_campaign_performance', 'V') IS NOT NULL DROP VIEW mart.mart_campaign_performance;
GO
CREATE VIEW mart.mart_campaign_performance AS
SELECT 
    c.campaign_id,
    c.campaign_name_en,
    c.campaign_name_ar,
    c.platform,
    c.budget_egp,
    c.expected_conversion_rate,
    COUNT(DISTINCT f.order_id) AS attributed_orders,
    SUM(f.quantity) AS attributed_units,
    SUM(f.net_sales_egp) AS attributed_net_sales,
    SUM(f.profit_egp) AS attributed_profit,
    CASE 
        WHEN c.budget_egp > 0 
        THEN ROUND(SUM(f.net_sales_egp) / c.budget_egp, 2) 
        ELSE 0 
    END AS roas_ratio -- Return on Ad Spend
FROM warehouse.dim_campaign c
LEFT JOIN warehouse.fact_sales f 
    ON c.campaign_key = f.campaign_key AND f.order_status = 'Completed'
GROUP BY 
    c.campaign_id, c.campaign_name_en, c.campaign_name_ar, c.platform,
    c.budget_egp, c.expected_conversion_rate;
GO

-- 7. OBSERVABILITY VIEW: PIPELINE HEALTH & OBSERVABILITY
IF OBJECT_ID('mart.v_pipeline_health', 'V') IS NOT NULL DROP VIEW mart.v_pipeline_health;
GO
CREATE VIEW mart.v_pipeline_health AS
SELECT 
    pr.run_id,
    pr.pipeline_name,
    pr.start_time,
    pr.end_time,
    pr.duration_seconds,
    pr.status AS pipeline_status,
    pr.rows_read,
    pr.rows_inserted,
    pr.rows_rejected,
    CASE 
        WHEN pr.rows_read > 0 
        THEN ROUND(100.0 * (pr.rows_read - pr.rows_rejected) / pr.rows_read, 2)
        ELSE 100.0 
    END AS data_quality_health_score,
    pr.error_message
FROM audit.pipeline_runs pr;
GO

PRINT 'Analytics Marts and Observability Views created successfully.';
GO
