import pytest
import pandas as pd
from src.validation.rules_engine import RulesEngine

def test_uniqueness_check():
    df = pd.DataFrame({"order_id": ["ORD-1", "ORD-2", "ORD-1", "ORD-3"]})
    mask = RulesEngine.check_uniqueness(df, "order_id")
    assert mask.tolist() == [True, False, True, False]

def test_positive_numeric_check():
    df = pd.DataFrame({"quantity": ["5", "0", "-2", "abc", "10"]})
    mask = RulesEngine.check_positive_numeric(df, "quantity")
    assert mask.tolist() == [False, True, True, True, False]

def test_non_negative_check():
    df = pd.DataFrame({"closing_stock": ["10", "0", "-5", "20"]})
    mask = RulesEngine.check_non_negative(df, "closing_stock")
    assert mask.tolist() == [False, False, True, False]

def test_foreign_key_check():
    df = pd.DataFrame({"cust_id": ["C1", "C2", "C999", "C3"]})
    valid_customers = {"C1", "C2", "C3"}
    mask = RulesEngine.check_foreign_key(df, "cust_id", valid_customers)
    assert mask.tolist() == [False, False, True, False]

def test_date_range_check():
    df = pd.DataFrame({"order_date": ["2025-05-15", "1900-01-01", "2027-01-01", "invalid-date"]})
    mask = RulesEngine.check_date_range(df, "order_date", min_date="2020-01-01", max_date="2025-12-31")
    assert mask.tolist() == [False, True, True, True]
