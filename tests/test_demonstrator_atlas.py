"""Unit tests for Track 014 atlas release demonstrator engine."""

from __future__ import annotations

from pathlib import Path

from rareburden.demonstrator_atlas import (
    execute_atlas_reference_analysis,
    generate_track014_reference_package,
    render_track014_reference_csv,
    render_track014_reference_report,
)

ROOT = Path(__file__).resolve().parents[1]


def test_execute_atlas_reference_analysis() -> None:
    results = execute_atlas_reference_analysis(ROOT)
    assert results["protocol_id"] == "RBC-R001"
    assert results["claims"]["synthetic_projection_executable"] is True
    assert results["claims"]["public_release"] is False
    assert results["claims"]["stable_release"] is False
    assert results["claims"]["real_source_activation"] is False

    assert results["product_count"] == 3
    assert results["api_row_count"] > 0
    assert results["consistency_validation"]["status"] == "repository_accessibility_contract_valid"


def test_render_atlas_report_and_csv() -> None:
    results = execute_atlas_reference_analysis(ROOT)
    report = render_track014_reference_report(results)
    assert "# Track 014: Atlas, API and Reproducible Release Reference Report" in report
    assert results["package_fingerprint"] in report

    csv_out = render_track014_reference_csv(results)
    assert "surface,package,fingerprint" in csv_out


def test_generate_atlas_reference_package_is_deterministic(tmp_path: Path) -> None:
    import shutil

    shutil.copytree(ROOT / "catalog", tmp_path / "catalog")
    shutil.copytree(ROOT / "examples", tmp_path / "examples")

    pkg1 = generate_track014_reference_package(tmp_path)
    pkg2 = generate_track014_reference_package(tmp_path)

    assert pkg1["receipt_id"] == pkg2["receipt_id"]
    assert pkg1["paths"]["results_json"].read_text(encoding="utf-8") == pkg2["paths"][
        "results_json"
    ].read_text(encoding="utf-8")
