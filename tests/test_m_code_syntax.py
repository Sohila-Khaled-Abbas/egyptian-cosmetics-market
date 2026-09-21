"""
Automated Syntax & Bracket Balancing Test Suite for Power Query (M) Code Files
"""

from pathlib import Path
import pytest

M_DIR = Path(__file__).parent.parent / "power_query_m"

EXPECTED_M_FILES = [
    "00_parameters_and_functions.m",
    "01_source_queries.m",
    "02_staging_queries.m",
    "03_reference_queries.m",
    "04_cleansed_queries.m",
    "05_validated_quarantine_queries.m",
    "06_transformation_queries.m",
    "07_model_queries.m",
    "99_admin_queries.m",
]

def test_all_expected_m_files_exist():
    """Verify all 9 query group M scripts are present."""
    assert M_DIR.exists(), f"Directory not found: {M_DIR}"
    present_files = {f.name for f in M_DIR.glob("*.m")}
    for expected in EXPECTED_M_FILES:
        assert expected in present_files, f"Missing required M script: {expected}"

@pytest.mark.parametrize("filename", EXPECTED_M_FILES)
def test_m_file_bracket_balance(filename):
    """Verify that parentheses, square brackets, and curly braces are perfectly balanced."""
    file_path = M_DIR / filename
    assert file_path.exists()
    content = file_path.read_text(encoding="utf-8")
    
    round_open = content.count("(")
    round_close = content.count(")")
    assert round_open == round_close, (
        f"{filename} has unbalanced parentheses: '('={round_open}, ')'={round_close}"
    )

    square_open = content.count("[")
    square_close = content.count("]")
    assert square_open == square_close, (
        f"{filename} has unbalanced square brackets: '['={square_open}, ']'={square_close}"
    )

    curly_open = content.count("{")
    curly_close = content.count("}")
    assert curly_open == curly_close, (
        f"{filename} has unbalanced curly braces: '{{'={curly_open}, '}}'={curly_close}"
    )

@pytest.mark.parametrize("filename", EXPECTED_M_FILES)
def test_m_file_non_empty(filename):
    """Verify M script contains meaningful content."""
    file_path = M_DIR / filename
    assert file_path.stat().st_size > 200, f"{filename} is suspiciously small."
