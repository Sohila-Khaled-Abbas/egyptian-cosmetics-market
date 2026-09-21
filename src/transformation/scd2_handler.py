from typing import List, Dict, Any
import pandas as pd
from src.utils.hashing import compute_row_hash
from src.utils.logger import get_logger

logger = get_logger("scd2_handler")

class SCD2Handler:
    """
    Manages Slowly Changing Dimension Type 2 logic for tracked dimensions (e.g. dim_customer).
    Attributes tracked for change: governorate, area/city, customer_segment.
    """
    TRACKED_COLUMNS = ["governorate", "area", "customer_segment"]

    @staticmethod
    def generate_scd2_hash(row: Dict[str, Any]) -> str:
        """Computes deterministic hash over tracked SCD2 columns."""
        values = [row.get(col, "") for col in SCD2Handler.TRACKED_COLUMNS]
        return compute_row_hash(values)

    @staticmethod
    def detect_changes(existing_current_df: pd.DataFrame, incoming_df: pd.DataFrame, key_col: str) -> Dict[str, pd.DataFrame]:
        """
        Compares incoming records against existing current dimension rows.
        Returns:
            - 'new': Completely new business keys
            - 'changed': Existing keys where tracked attributes changed
            - 'unchanged': Existing keys with no change
        """
        incoming_with_hash = incoming_df.copy()
        incoming_with_hash["scd_hash"] = incoming_with_hash.apply(
            lambda r: SCD2Handler.generate_scd2_hash(r.to_dict()), axis=1
        )

        merged = incoming_with_hash.merge(
            existing_current_df[[key_col, "scd_hash"]].rename(columns={"scd_hash": "existing_hash"}),
            on=key_col,
            how="left"
        )

        new_mask = merged["existing_hash"].isna()
        changed_mask = (~new_mask) & (merged["scd_hash"] != merged["existing_hash"])
        unchanged_mask = (~new_mask) & (merged["scd_hash"] == merged["existing_hash"])

        return {
            "new": merged[new_mask],
            "changed": merged[changed_mask],
            "unchanged": merged[unchanged_mask]
        }
