from __future__ import annotations

from pathlib import Path

from rareburden.schema import load_mapping

ROOT = Path(__file__).parents[1]
MATRIX = ROOT / "docs/downstream-track-status-matrix-2026-08-05.yml"


def test_downstream_matrix_covers_tracks_008_to_017_without_false_closure() -> None:
    matrix = load_mapping(MATRIX)
    assert {row["track"] for row in matrix["tracks"]} == {
        "008",
        "009",
        "010",
        "011",
        "012",
        "013",
        "014",
        "015",
        "016",
        "017",
    }
    assert all(row["state"] == "bounded_preparation" for row in matrix["tracks"])
    assert all(row["remaining_blocks"] for row in matrix["tracks"])
    assert matrix["activation_rule"].startswith("synthetic_public_only")


def test_downstream_matrix_keeps_accountable_gates_open() -> None:
    matrix = load_mapping(MATRIX)
    rules = " ".join(matrix["non_closure_rules"])
    assert "panel outputs do not satisfy independent" in rules
    assert "upstream change" in rules


def test_downstream_matrix_links_exact_repository_evidence_without_claiming_authority() -> None:
    evidence = load_mapping(MATRIX)["repository_evidence"]
    assert evidence["tracked_reports"] == [
        "coverage.json",
        "coverage.xml",
        "junit.xml",
        "rareburden.cdx.json",
    ]
    assert evidence["binding_check"] == "uv run make validation-artifacts-check"
    assert evidence["authority"] == "repository_generated_not_external_or_release_authority"
