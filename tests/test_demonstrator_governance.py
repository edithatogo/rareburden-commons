"""Tests for Track 021 reference governance demonstrator."""

from __future__ import annotations

from pathlib import Path

from rareburden.demonstrator_governance import (
    execute_governance_reference_analysis,
    generate_governance_reference_package,
)

ROOT = Path(__file__).resolve().parents[1]


def test_execute_governance_reference_analysis() -> None:
    results = execute_governance_reference_analysis(ROOT)
    assert results["status"] == "bounded_external_governance_framework_verified"
    assert results["governance"]["accountable_human"] == "edithatogo"
    assert results["governance"]["production_authorized"] is False
    assert results["governance"]["external_partnership_confirmed"] is False
    assert len(results["activation_conditions"]) == 5


def test_generate_governance_reference_package(tmp_path: Path) -> None:
    output_dir = tmp_path / "reference"
    receipt = generate_governance_reference_package(ROOT, output_dir)
    assert receipt["receipt_id"].startswith("t021gov-")
    assert (output_dir / "reference-results.json").is_file()
    assert (output_dir / "reference-report.md").is_file()
    assert (output_dir / "reference-tables.csv").is_file()
