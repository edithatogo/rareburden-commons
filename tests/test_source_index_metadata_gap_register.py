from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_source_index_metadata_gap_register_reconciles_union() -> None:
    register = yaml.safe_load(
        (ROOT / "docs/source-index-metadata-gap-register-2026-08-21.yml").read_text()
    )
    reconciliation = register["reconciliation"]
    assert reconciliation == {
        "catalogue_records": 16,
        "archival_matrix_records": 21,
        "overlap_records": 15,
        "union_records": 22,
        "all_sources_indexed": False,
        "all_exact_release_metadata_archived": False,
        "all_raw_bytes_archived": False,
        "all_raw_bytes_publicly_redistributable": False,
    }
    assert {row["source_id"] for row in register["catalogue_only"]} == {
        "who-global-health-expenditure-database"
    }
    assert len(register["archival_matrix_only"]) == 6
    assert register["claims"]["global_completeness"] is False
