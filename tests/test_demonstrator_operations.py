"""Tests for Track 016 reference operations demonstrator."""

from __future__ import annotations

from pathlib import Path

from rareburden.demonstrator_operations import (
    execute_operations_reference_analysis,
    generate_operations_reference_package,
)

ROOT = Path(__file__).resolve().parents[1]


def test_execute_operations_reference_analysis() -> None:
    results = execute_operations_reference_analysis(ROOT)
    assert results["status"] == "bounded_operations_verified"
    assert results["governance"]["accountable_human"] == "edithatogo"
    assert results["governance"]["production_authorized"] is False
    assert results["exercise_receipt"]["outcome"] == "pass"


def test_generate_operations_reference_package(tmp_path: Path) -> None:
    output_dir = tmp_path / "reference"
    receipt = generate_operations_reference_package(ROOT, output_dir)
    assert receipt["receipt_id"].startswith("t016ops-")
    assert (output_dir / "reference-results.json").is_file()
    assert (output_dir / "reference-report.md").is_file()
    assert (output_dir / "reference-tables.csv").is_file()
