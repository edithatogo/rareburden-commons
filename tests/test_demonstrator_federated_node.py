"""Tests for Track 004 reference federated node demonstrator."""

from __future__ import annotations

from pathlib import Path

from rareburden.demonstrator_federated_node import (
    execute_federated_node_reference_analysis,
    generate_federated_node_reference_package,
)

ROOT = Path(__file__).resolve().parents[1]


def test_execute_federated_node_reference_analysis() -> None:
    results = execute_federated_node_reference_analysis(ROOT)
    assert results["status"] == "bounded_federated_node_package_verified"
    assert results["protocol"] == "RBC-F001"
    assert results["governance"]["accountable_human"] == "edithatogo"
    assert results["governance"]["controlled_data_activation"] is False
    assert results["governance"]["live_custodian_linkage"] is False
    assert len(results["gates_evaluated"]) == 6


def test_generate_federated_node_reference_package(tmp_path: Path) -> None:
    output_dir = tmp_path / "reference"
    receipt = generate_federated_node_reference_package(ROOT, output_dir)
    assert receipt["receipt_id"].startswith("t004node-")
    assert (output_dir / "reference-results.json").is_file()
    assert (output_dir / "reference-report.md").is_file()
    assert (output_dir / "reference-tables.csv").is_file()
