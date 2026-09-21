from pathlib import Path
from typing import Dict
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger("load_excel")

def read_excel_sheets(file_path: Path) -> Dict[str, pd.DataFrame]:
    """
    Reads all sheets from an Excel workbook into a dictionary of DataFrames.
    Preserves raw lossless string representations.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")
    
    logger.info(f"Loading Excel workbook: {file_path.name}")
    xl = pd.ExcelFile(file_path)
    sheets_data = {}
    
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet_name, dtype=str, keep_default_na=False)
        sheets_data[sheet_name] = df
        logger.info(f"Loaded sheet [{sheet_name}] with {len(df)} rows")
        
    return sheets_data
