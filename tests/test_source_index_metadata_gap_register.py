from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_source_index_metadata_gap_register_reconciles_union() -> None:
    register = yaml.safe_load(
        (ROOT / "docs/source-index-metadata-gap-register-2026-08-21.yml").read_text()
    )
    reconciliation = register["reconciliation"]
    assert reconciliation == {
        "catalogue_records": 22,
        "archival_matrix_records": 22,
        "overlap_records": 22,
        "union_records": 22,
        "declared_catalogue_matrix_id_parity": True,
        "all_sources_indexed": False,
        "all_exact_release_metadata_archived": False,
        "all_raw_bytes_archived": False,
        "all_raw_bytes_publicly_redistributable": False,
    }
    assert register["catalogue_only"] == []
    assert register["archival_matrix_only"] == []
    assert register["claims"]["global_completeness"] is False


def test_catalogue_and_archival_matrix_have_exact_source_id_parity() -> None:
    catalogue = yaml.safe_load((ROOT / "catalog/data_sources.yml").read_text())
    matrix = yaml.safe_load(
        (ROOT / "docs/source-archive-decision-matrix-2026-08-15.yml").read_text()
    )
    assert {row["source_id"] for row in catalogue["sources"]} == {
        row["source_id"] for row in matrix["decisions"]
    }
