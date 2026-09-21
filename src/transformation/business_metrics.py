from typing import Dict, Any
import pandas as pd
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("business_metrics")

class BusinessMetricsCalculator:
    @staticmethod
    def calculate_rfm(sales_df: pd.DataFrame, reference_date: pd.Timestamp = None) -> pd.DataFrame:
        """
        Calculates Recency, Frequency, and Monetary metrics and assigns quintile scores (1-5)
        and customer segments.
        sales_df must contain: customer_id, order_datetime, net_sales_egp.
        """
        if sales_df.empty:
            return pd.DataFrame()

        ref_date = reference_date or sales_df["order_datetime"].max()

        rfm = sales_df.groupby("customer_id").agg(
            recency_days=("order_datetime", lambda x: (ref_date - x.max()).days),
            frequency=("order_datetime", "count"),
            monetary_spend=("net_sales_egp", "sum")
        ).reset_index()

        # Score Recency (Lower days = higher score 5)
        rfm["r_score"] = pd.qcut(rfm["recency_days"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop").astype(int)
        # Score Frequency (Higher count = higher score 5)
        rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        # Score Monetary (Higher spend = higher score 5)
        rfm["m_score"] = pd.qcut(rfm["monetary_spend"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

        rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)

        # Segment assignment
        def assign_segment(r: int, f: int) -> str:
            if r >= 4 and f >= 4:
                return "Champions"
            elif r >= 3 and f >= 3:
                return "Loyal Customers"
            elif r >= 3 and f <= 2:
                return "Potential Loyalists"
            elif r <= 2 and f >= 3:
                return "At Risk"
            elif r <= 2 and f <= 2:
                return "Lost / Inactive"
            return "Standard"

        rfm["rfm_segment"] = rfm.apply(lambda row: assign_segment(row["r_score"], row["f_score"]), axis=1)
        return rfm

    @staticmethod
    def calculate_sell_through_rate(received_qty: int, sold_qty: int, opening_stock: int) -> float:
        """Computes sell-through rate %: sold_qty / (opening_stock + received_qty)."""
        denom = opening_stock + received_qty
        if denom <= 0:
            return 0.0
        return round(float(sold_qty) / denom, 4)
