import hashlib
from typing import Any, Sequence

def compute_row_hash(values: Sequence[Any]) -> str:
    """
    Computes a deterministic SHA-256 hash string for a row.
    Nulls are converted to empty strings, and values are stripped of surrounding whitespace.
    """
    normalized = "|".join("" if v is None else str(v).strip() for v in values)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
