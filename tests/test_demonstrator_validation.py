"""Unit tests for Track 013 demonstrator validation and uncertainty decomposition."""

from __future__ import annotations

import json
from pathlib import Path

from rareburden.demonstrator_validation import (
    decompose_uncertainty_and_sensitivity,
    execute_bronchiectasis_triangulation,
    execute_monogenic_diabetes_triangulation,
    generate_track013_reference_package,
    render_track013_reference_csv,
    render_track013_reference_report,
    validate_paediatric_and_economic_scope,
)
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]


def test_monogenic_diabetes_triangulation() -> None:
    t003_path = ROOT / "results/track-003-reference-2026-08-31/reference-results.json"
    t003_res = json.loads(t003_path.read_bytes())
    result = execute_monogenic_diabetes_triangulation(t003_res, tolerance=0.15)
    assert result["intended_use"] == "synthetic_assurance"
    assert result["primary"]["source_id"] == "rbc-p002-primary"
    assert result["primary"]["estimate"] == 2000.0
    assert len(result["comparisons"]) >= 2
    assert "not empirical validation" in result["interpretation"]


def test_bronchiectasis_triangulation() -> None:
    t011_path = ROOT / "results/track-011-reference-2026-09-05/reference-results.json"
    t011_res = json.loads(t011_path.read_bytes())
    result = execute_bronchiectasis_triangulation(t011_res, tolerance=0.15)
    assert result["intended_use"] == "synthetic_assurance"
    assert result["primary"]["source_id"] == "rbc-p003-primary"
    assert result["primary"]["estimate"] == 700.0
    assert len(result["comparisons"]) >= 2


def test_paediatric_and_economic_validation() -> None:
    t012_path = ROOT / "results/track-012-reference-2026-09-06/reference-results.json"
    econ_path = ROOT / "examples/economics/component-first-invented.yml"
    t012_res = json.loads(t012_path.read_bytes())
    econ_fix = load_mapping(econ_path)
    result = validate_paediatric_and_economic_scope(t012_res, econ_fix)
    assert result["intended_use"] == "synthetic_assurance"
    assert result["overall_scope_verified"] is True
    assert result["paediatric_validation"]["person_conservation_verified"] is True
    assert result["paediatric_validation"]["deduplicated_people"] == 2
    assert result["economic_validation"]["component_count"] == 3
    assert result["economic_validation"]["synthetic_only"] is True


def test_uncertainty_decomposition() -> None:
    result = decompose_uncertainty_and_sensitivity()
    assert result["intended_use"] == "synthetic_assurance"
    assert "prevalence_per_100k" in result["decision_sensitive_parameters"]
    assert "diagnostic_yield" in result["decision_sensitive_parameters"]
    assert "missingness_fraction" not in result["decision_sensitive_parameters"]


def test_validation_pipeline_and_package_deterministic(tmp_path: Path) -> None:
    import shutil

    shutil.copytree(ROOT / "results", tmp_path / "results")
    shutil.copytree(ROOT / "examples", tmp_path / "examples")

    pkg1 = generate_track013_reference_package(tmp_path)
    pkg2 = generate_track013_reference_package(tmp_path)

    assert pkg1["receipt_id"] == pkg2["receipt_id"]
    report = render_track013_reference_report(pkg1["results"])
    assert "# Track 013: Quality, Validation" in report
    csv_out = render_track013_reference_csv(pkg1["results"])
    assert "triangulation,monogenic_diabetes" in csv_out
