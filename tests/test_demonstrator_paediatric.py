"""Unit tests for the Paediatric Rare-Disease Reference Demonstrator engine (Track 012)."""

from __future__ import annotations

from pathlib import Path

from rareburden.demonstrator_paediatric import (
    REFERENCE_SCENARIOS,
    execute_paediatric_reference_analysis,
    generate_paediatric_reference_package,
    render_paediatric_reference_csv,
    render_paediatric_reference_report,
)
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = load_mapping(ROOT / "examples/paediatric/linked-data-synthetic.yml")
BINDINGS = load_mapping(ROOT / "docs/track-012-dependency-bindings-2026-08-16.yml")


def test_execute_paediatric_reference_analysis() -> None:
    results = execute_paediatric_reference_analysis(FIXTURE, BINDINGS)
    assert results["protocol_id"] == "RBC-P004"
    assert results["claims"]["empirical_activation"] is False
    assert results["claims"]["clinical_interpretation"] is False
    assert results["claims"]["scope_reference_demonstrator_only"] is True

    # Check conservation
    cons = results["conservation_summary"]
    assert cons["conservation_verified"] is True
    assert cons["deduplicated_people"] == 2
    assert cons["total_person_records"] == 2

    # Check scenarios
    scenarios = results["scenarios"]
    assert len(scenarios) == len(REFERENCE_SCENARIOS)
    assert scenarios[0]["scenario_id"] == "baseline-primary-linkage"
    assert scenarios[0]["deduplicated_people"] == 2
    assert scenarios[0]["utilisation_rate"] == 1.5

    # Check node integration
    node = results["node_integration"]
    assert node["manifest_status"] == "completed"
    assert node["synthetic_assurance"] is True


def test_render_report_and_csv() -> None:
    results = execute_paediatric_reference_analysis(FIXTURE, BINDINGS)
    report = render_paediatric_reference_report(results)
    assert "# Track 012: Collective Paediatric Rare-Disease Burden Reference Report" in report
    assert "**Conservation Check Passed:** `True`" in report

    csv_text = render_paediatric_reference_csv(results)
    assert "scenario_id,label,disclosure_threshold" in csv_text
    assert "baseline-primary-linkage" in csv_text


def test_generate_paediatric_reference_package_is_deterministic(tmp_path: Path) -> None:
    import shutil

    shutil.copytree(ROOT / "examples", tmp_path / "examples")
    shutil.copytree(ROOT / "docs", tmp_path / "docs")

    pkg1 = generate_paediatric_reference_package(tmp_path)
    pkg2 = generate_paediatric_reference_package(tmp_path)

    assert pkg1["results"]["receipt_id"] == pkg2["results"]["receipt_id"]
    assert pkg1["paths"]["results_json"].read_text(encoding="utf-8") == pkg2["paths"][
        "results_json"
    ].read_text(encoding="utf-8")
