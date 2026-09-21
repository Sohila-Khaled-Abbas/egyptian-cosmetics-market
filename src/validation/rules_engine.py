from dataclasses import dataclass
from typing import List, Callable, Any, Optional
import pandas as pd

@dataclass
class DQRule:
    rule_id: str
    table_name: str
    column_name: str
    rule_name: str
    rule_type: str  # Uniqueness, Range, Referential, Completeness, AcceptedValues
    severity: str   # Critical, Warning
    description: str

class RulesEngine:
    @staticmethod
    def check_uniqueness(df: pd.DataFrame, column: str) -> pd.Series:
        """Returns boolean mask where True = Defective (duplicate)."""
        return df.duplicated(subset=[column], keep=False)

    @staticmethod
    def check_not_null(df: pd.DataFrame, column: str) -> pd.Series:
        """Returns boolean mask where True = Defective (is null or empty string)."""
        if column not in df.columns:
            return pd.Series(True, index=df.index)
        return df[column].isna() | (df[column].astype(str).str.strip() == "")

    @staticmethod
    def check_positive_numeric(df: pd.DataFrame, column: str) -> pd.Series:
        """Returns boolean mask where True = Defective (non-numeric or <= 0)."""
        numeric_series = pd.to_numeric(df[column], errors="coerce")
        return numeric_series.isna() | (numeric_series <= 0)

    @staticmethod
    def check_non_negative(df: pd.DataFrame, column: str) -> pd.Series:
        """Returns boolean mask where True = Defective (non-numeric or < 0)."""
        numeric_series = pd.to_numeric(df[column], errors="coerce")
        return numeric_series.isna() | (numeric_series < 0)

    @staticmethod
    def check_foreign_key(df_child: pd.DataFrame, child_col: str, valid_keys: set) -> pd.Series:
        """Returns boolean mask where True = Defective (orphan key)."""
        return ~df_child[child_col].astype(str).isin(valid_keys)

    @staticmethod
    def check_date_range(df: pd.DataFrame, date_col: str, min_date: str = "2020-01-01", max_date: Optional[str] = None) -> pd.Series:
        """Returns boolean mask where True = Defective (invalid date or out of bounds)."""
        dt_series = pd.to_datetime(df[date_col], errors="coerce")
        mask = dt_series.isna() | (dt_series < pd.to_datetime(min_date))
        if max_date:
            mask = mask | (dt_series > pd.to_datetime(max_date))
        return mask
