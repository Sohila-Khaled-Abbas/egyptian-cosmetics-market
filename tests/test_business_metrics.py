import pytest
import pandas as pd
from src.transformation.business_metrics import BusinessMetricsCalculator

def test_calculate_sell_through_rate():
    rate = BusinessMetricsCalculator.calculate_sell_through_rate(received_qty=50, sold_qty=30, opening_stock=50)
    assert rate == 0.30  # 30 / 100 = 0.30

    zero_denom = BusinessMetricsCalculator.calculate_sell_through_rate(received_qty=0, sold_qty=0, opening_stock=0)
    assert zero_denom == 0.0

def test_calculate_rfm():
    data = [
        {"customer_id": "C1", "order_datetime": pd.Timestamp("2025-12-30"), "net_sales_egp": 5000.0},
        {"customer_id": "C1", "order_datetime": pd.Timestamp("2025-12-28"), "net_sales_egp": 3000.0},
        {"customer_id": "C2", "order_datetime": pd.Timestamp("2025-06-01"), "net_sales_egp": 200.0},
        {"customer_id": "C3", "order_datetime": pd.Timestamp("2025-12-15"), "net_sales_egp": 1200.0},
        {"customer_id": "C4", "order_datetime": pd.Timestamp("2025-01-10"), "net_sales_egp": 150.0},
        {"customer_id": "C5", "order_datetime": pd.Timestamp("2025-11-20"), "net_sales_egp": 850.0},
    ]
    df = pd.DataFrame(data)
    rfm = BusinessMetricsCalculator.calculate_rfm(df, reference_date=pd.Timestamp("2025-12-31"))

    assert len(rfm) == 5
    assert "r_score" in rfm.columns
    assert "f_score" in rfm.columns
    assert "m_score" in rfm.columns
    assert "rfm_segment" in rfm.columns
