from pathlib import Path
from typing import Iterator, Optional
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger("load_csv")

def read_csv_in_chunks(
    file_path: Path,
    chunk_size: int = 50000,
    dtype: Optional[dict] = None
) -> Iterator[pd.DataFrame]:
    """
    Reads a CSV file in chunks for memory-efficient processing of large datasets.
    Yields dataframes chunk by chunk as strings/raw types to prevent data loss.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    logger.info(f"Streaming CSV file: {file_path.name} in chunks of {chunk_size} rows")
    # Read everything as string by default to preserve raw lossless fidelity
    for chunk in pd.read_csv(file_path, chunksize=chunk_size, dtype=str, keep_default_na=False):
        yield chunk

def read_csv_full(file_path: Path) -> pd.DataFrame:
    """Reads a CSV file entirely into a DataFrame as string types."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    logger.info(f"Reading CSV file: {file_path.name}")
    return pd.read_csv(file_path, dtype=str, keep_default_na=False)
