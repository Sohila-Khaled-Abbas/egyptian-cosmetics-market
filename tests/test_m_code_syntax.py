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


def test_tmdl_definitions_and_bracket_balance():
    """Verify TMDL expressions and table partition M queries are valid and balanced."""
    import re
    tmdl_dir = Path(__file__).parent.parent / "powerbi" / "Cleopatra_Cosmetics_Report.SemanticModel" / "definition"
    if not tmdl_dir.exists():
        pytest.skip("TMDL directory not present")

    def check_m_block(name, code):
        parens = curlies = squares = 0
        in_string = in_block_comment = False
        for line_idx, line in enumerate(code.splitlines(), 1):
            i = 0
            while i < len(line):
                ch = line[i]
                if not in_string and not in_block_comment and line[i:i+2] == '//':
                    break
                if not in_string and not in_block_comment and line[i:i+2] == '/*':
                    in_block_comment = True
                    i += 2
                    continue
                if in_block_comment and line[i:i+2] == '*/':
                    in_block_comment = False
                    i += 2
                    continue
                if in_block_comment:
                    i += 1
                    continue
                if ch == '"':
                    if in_string and i + 1 < len(line) and line[i+1] == '"':
                        i += 2
                        continue
                    in_string = not in_string
                    i += 1
                    continue
                if not in_string:
                    if ch == '(': parens += 1
                    elif ch == ')': parens -= 1
                    elif ch == '{': curlies += 1
                    elif ch == '}': curlies -= 1
                    elif ch == '[': squares += 1
                    elif ch == ']': squares -= 1
                    assert parens >= 0, f"Extra ')' in {name} line {line_idx}"
                    assert curlies >= 0, f"Extra '}}' in {name} line {line_idx}"
                    assert squares >= 0, f"Extra ']' in {name} line {line_idx}"
                i += 1
        assert parens == 0, f"Unbalanced '(' in {name}"
        assert curlies == 0, f"Unbalanced '{{' in {name}"
        assert squares == 0, f"Unbalanced '[' in {name}"
        assert not in_string, f"Unclosed string in {name}"
        assert not in_block_comment, f"Unclosed block comment in {name}"

    expr_file = tmdl_dir / "expressions.tmdl"
    assert expr_file.exists(), "expressions.tmdl is missing"
    content = expr_file.read_text(encoding="utf-8")
    blocks = re.findall(r"expression\s+([a-zA-Z0-9_]+)\s*=\s*```(.*?)```", content, re.DOTALL)
    assert len(blocks) >= 45, f"Expected at least 45 multiline expressions, got {len(blocks)}"
    for name, body in blocks:
        check_m_block(f"expr:{name}", body)

    tables_dir = tmdl_dir / "tables"
    assert tables_dir.exists(), "tables directory is missing"
    table_files = list(tables_dir.glob("*.tmdl"))
    assert len(table_files) >= 20, f"Expected at least 20 table TMDL files, got {len(table_files)}"
    for tf in table_files:
        t_content = tf.read_text(encoding="utf-8")
        parts = re.findall(r"partition\s+[^\r\n=]+=\s*m\s*\r?\n\s*mode:\s*import\s*\r?\n\s*source\s*=\s*```(.*?)```", t_content, re.DOTALL)
        for p in parts:
            check_m_block(f"table:{tf.name}", p)

