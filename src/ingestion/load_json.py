import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger("load_json")

def read_exchange_rates_json(file_path: Path) -> pd.DataFrame:
    """
    Parses exchange rates JSON and returns a standardized pandas DataFrame.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    logger.info(f"Loading JSON file: {file_path.name}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = []
    for item in data:
        # Convert timestamp to date string if numeric epoch ms
        rate_date_raw = item.get("rate_date")
        if isinstance(rate_date_raw, (int, float)):
            rate_date_str = datetime.fromtimestamp(rate_date_raw / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
        else:
            rate_date_str = str(rate_date_raw)

        records.append({
            "rate_date": rate_date_str,
            "base_currency": str(item.get("base_currency", "")),
            "quote_currency": str(item.get("quote_currency", "")),
            "exchange_rate": str(item.get("rate", "")),
            "api_endpoint": "https://api.exchangerate.host/timeseries",
            "api_response_code": "200"
        })

    df = pd.DataFrame(records)
    logger.info(f"Loaded {len(df)} exchange rate records from {file_path.name}")
    return df
