"""Tests for Track 017 reference adoption demonstrator."""

from __future__ import annotations

from pathlib import Path

from rareburden.demonstrator_adoption import (
    execute_adoption_reference_analysis,
    generate_adoption_reference_package,
)

ROOT = Path(__file__).resolve().parents[1]


def test_execute_adoption_reference_analysis() -> None:
    results = execute_adoption_reference_analysis(ROOT)
    assert results["status"] == "bounded_adoption_and_release_candidate_verified"
    assert results["governance"]["accountable_human"] == "edithatogo"
    assert results["governance"]["production_authorized"] is False
    assert results["sustainability"]["operating_model"] == "zero_cost_local_static_repository"
    assert results["v1_criteria_summary"]["blocking_criteria_addressed"] == 67


def test_generate_adoption_reference_package(tmp_path: Path) -> None:
    output_dir = tmp_path / "reference"
    receipt = generate_adoption_reference_package(ROOT, output_dir)
    assert receipt["receipt_id"].startswith("t017adopt-")
    assert (output_dir / "reference-results.json").is_file()
    assert (output_dir / "reference-report.md").is_file()
    assert (output_dir / "reference-tables.csv").is_file()
