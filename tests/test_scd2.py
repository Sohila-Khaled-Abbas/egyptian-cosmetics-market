import pytest
import pandas as pd
from src.transformation.scd2_handler import SCD2Handler

def test_scd2_change_detection():
    # Existing active records in dimension
    existing_df = pd.DataFrame([
        {"customer_id": "C-101", "governorate": "Cairo", "area": "Nasr City", "customer_segment": "Standard", "scd_hash": ""},
        {"customer_id": "C-102", "governorate": "Giza", "area": "Dokki", "customer_segment": "VIP", "scd_hash": ""},
    ])
    existing_df["scd_hash"] = existing_df.apply(lambda r: SCD2Handler.generate_scd2_hash(r.to_dict()), axis=1)

    # Incoming batch: C-101 unchanged, C-102 moved from Giza to Alexandria, C-103 is brand new
    incoming_df = pd.DataFrame([
        {"customer_id": "C-101", "governorate": "Cairo", "area": "Nasr City", "customer_segment": "Standard"},
        {"customer_id": "C-102", "governorate": "Alexandria", "area": "Smouha", "customer_segment": "VIP"},
        {"customer_id": "C-103", "governorate": "Sohag", "area": "Akhmim", "customer_segment": "New"},
    ])

    diff = SCD2Handler.detect_changes(existing_df, incoming_df, key_col="customer_id")

    assert len(diff["new"]) == 1
    assert diff["new"].iloc[0]["customer_id"] == "C-103"

    assert len(diff["changed"]) == 1
    assert diff["changed"].iloc[0]["customer_id"] == "C-102"

    assert len(diff["unchanged"]) == 1
    assert diff["unchanged"].iloc[0]["customer_id"] == "C-101"
