import pytest
from src.utils.hashing import compute_row_hash

def test_compute_row_hash_deterministic():
    vals1 = ["ORD-1001", "CUST-001", 150.50, "Cairo"]
    vals2 = ["ORD-1001", "CUST-001", 150.50, "Cairo"]
    assert compute_row_hash(vals1) == compute_row_hash(vals2)
    assert len(compute_row_hash(vals1)) == 64  # SHA-256 hex length

def test_compute_row_hash_different():
    vals1 = ["ORD-1001", "CUST-001", 150.50, "Cairo"]
    vals2 = ["ORD-1001", "CUST-001", 150.50, "Giza"]
    assert compute_row_hash(vals1) != compute_row_hash(vals2)

def test_compute_row_hash_null_handling():
    vals = ["ORD-1001", None, "   "]
    h = compute_row_hash(vals)
    assert isinstance(h, str) and len(h) == 64
