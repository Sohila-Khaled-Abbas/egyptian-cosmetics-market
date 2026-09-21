"""
Automated Verification Suite for Documentation Completeness
Ensures all 20 playbooks and architecture blueprints exist and are fully populated.
"""

from pathlib import Path
import pytest

DOCS_DIR = Path(__file__).parent.parent / "docs" / "powerbi"

EXPECTED_PLAYBOOKS = [
    f"{i:02d}_{name}.md" for i, name in [
        (1, "powerbi_project_setup"),
        (2, "raw_data_ingestion"),
        (3, "data_profiling"),
        (4, "power_query_cleaning"),
        (5, "data_quality"),
        (6, "reference_mapping"),
        (7, "transformations"),
        (8, "merge_append_strategy"),
        (9, "power_query_functions"),
        (10, "data_model"),
        (11, "dax_measures"),
        (12, "time_intelligence"),
        (13, "rfm_analysis"),
        (14, "inventory_analysis"),
        (15, "target_analysis"),
        (16, "data_quality_dashboard"),
        (17, "testing_validation"),
        (18, "performance_optimization"),
        (19, "refresh_checklist"),
        (20, "troubleshooting"),
    ]
]

CORE_DOCS = [
    "data_lifecycle.md",
    "data_lineage.md",
    "report_design_pages.md",
]

def test_all_playbooks_exist():
    """Verify all 20 numbered playbooks are present."""
    assert DOCS_DIR.exists()
    for playbook in EXPECTED_PLAYBOOKS:
        doc_path = DOCS_DIR / playbook
        assert doc_path.exists(), f"Missing playbook: {playbook}"
        assert doc_path.stat().st_size > 1000, f"Playbook {playbook} is suspiciously short"

def test_core_docs_exist():
    """Verify lifecycle, lineage, and report design docs exist."""
    for core_doc in CORE_DOCS:
        doc_path = DOCS_DIR / core_doc
        assert doc_path.exists(), f"Missing core document: {core_doc}"
        assert doc_path.stat().st_size > 1000, f"Core document {core_doc} is suspiciously short"

def test_future_architecture_doc_exists():
    """Verify the future cloud production architecture document exists."""
    doc_path = Path(__file__).parent.parent / "docs" / "future_production_architecture.md"
    assert doc_path.exists()
    assert doc_path.stat().st_size > 2000
