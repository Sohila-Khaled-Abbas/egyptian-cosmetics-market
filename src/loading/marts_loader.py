from typing import Dict, Any
import pandas as pd
from sqlalchemy import text
from src.config.database import get_sqlalchemy_engine
from src.utils.logger import get_logger

logger = get_logger("marts_loader")

class MartsLoader:
    def __init__(self):
        self.engine = get_sqlalchemy_engine()

    def validate_marts(self) -> Dict[str, int]:
        """
        Validates and queries all 7 curated business marts.
        Returns the row count of each mart.
        """
        marts = [
            ("daily_sales", "mart.mart_daily_sales"),
            ("monthly_sales", "mart.mart_monthly_sales"),
            ("product_performance", "mart.mart_product_performance"),
            ("rfm_segmentation", "mart.mart_rfm"),
            ("inventory_health", "mart.mart_inventory_health"),
            ("campaign_performance", "mart.mart_campaign_performance"),
            ("pipeline_health", "mart.v_pipeline_health")
        ]
        
        counts = {}
        with self.engine.connect() as conn:
            for key, view_name in marts:
                cnt = conn.execute(text(f"SELECT COUNT(*) FROM {view_name}")).scalar()
                counts[key] = cnt
                logger.info(f"Verified mart [{view_name}]: {cnt:,} rows")
                
        return counts

    def get_executive_kpis(self) -> Dict[str, Any]:
        """Fetches top-line executive KPIs from the analytics marts."""
        query = text("""
            SELECT 
                CAST(SUM(actual_net_sales_egp) AS DECIMAL(18,2)) AS total_revenue_egp,
                SUM(completed_orders) AS total_orders,
                CAST(SUM(gross_profit_egp) AS DECIMAL(18,2)) AS total_profit_egp,
                ROUND(CASE WHEN SUM(actual_net_sales_egp) > 0 THEN CAST(SUM(gross_profit_egp) AS FLOAT) / SUM(actual_net_sales_egp) ELSE 0 END, 4) AS avg_margin_pct
            FROM mart.mart_monthly_sales
        """)
        with self.engine.connect() as conn:
            res = conn.execute(query).mappings().first()
            return dict(res) if res else {}
