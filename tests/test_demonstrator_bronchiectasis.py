"""Tests for Track 011 bronchiectasis reference demonstrator engine."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.demonstrator_bronchiectasis import (
    execute_bronchiectasis_reference_pipeline,
    load_bronchiectasis_reference_inputs,
    render_bronchiectasis_reference_csv,
    render_bronchiectasis_reference_report,
)
from rareburden.demonstrators import DemonstratorError

ROOT = Path(__file__).resolve().parents[1]


def test_load_bronchiectasis_reference_inputs() -> None:
    inputs = load_bronchiectasis_reference_inputs(ROOT)
    assert "profile" in inputs
    assert "hierarchy" in inputs
    assert "bindings" in inputs
    assert len(inputs["scenarios"]) == 6
    assert inputs["profile"]["denominator"] == 1000


def test_execute_bronchiectasis_reference_pipeline_and_conservation() -> None:
    inputs = load_bronchiectasis_reference_inputs(ROOT)
    results = execute_bronchiectasis_reference_pipeline(inputs, created_at="2026-09-05T00:00:00Z")

    assert results["schema_version"] == "1.0.0"
    assert results["demonstrator_id"] == "011-bronchiectasis-demonstrator"
    assert results["protocol_id"] == "RBC-P003"
    assert results["receipt_id"].startswith("demo11-")

    cons = results["conservation_summary"]
    assert cons["denominator"] == 1000.0
    assert cons["exclusive_sum"] == 700.0
    assert cons["multi_aetiology_cases"] == 80.0
    assert cons["unknown_cases"] == 150.0
    assert cons["unaccounted_cases"] == 70.0
    assert cons["conservation_verified"] is True

    assert results["scenarios_evaluated_count"] == 6
    baseline = results["scenarios"][0]
    assert baseline["scenario_id"] == "baseline-primary-exclusive"
    # exclusive primary bronchiectasis is 120
    assert baseline["estimated_attributable_cases"] == 700.0
    assert baseline["proportion_of_denominator"] == 0.70

    ref = results["reference_range"]
    assert ref["minimum_cases"] <= ref["maximum_cases"]
    assert ref["minimum_proportion"] <= ref["maximum_proportion"]
    assert ref["minimum_cases"] > 0


def test_render_report_and_csv() -> None:
    inputs = load_bronchiectasis_reference_inputs(ROOT)
    results = execute_bronchiectasis_reference_pipeline(inputs, created_at="2026-09-05T00:00:00Z")

    report = render_bronchiectasis_reference_report(results)
    assert "# Track 011: Bronchiectasis Rare-Aetiology Demonstrator Reference Report" in report
    assert "**Conservation Check Passed:** `True`" in report
    assert "baseline-primary-exclusive" in report
    assert "Methodological Limitations" in report

    csv_text = render_bronchiectasis_reference_csv(results)
    lines = csv_text.strip().split("\n")
    assert len(lines) == 7  # header + 6 scenarios
    assert lines[0].startswith("scenario_id,label,multi_aetiology_fraction")


def test_deterministic_reproducibility() -> None:
    inputs = load_bronchiectasis_reference_inputs(ROOT)
    run1 = execute_bronchiectasis_reference_pipeline(inputs, created_at="2026-09-05T00:00:00Z")
    run2 = execute_bronchiectasis_reference_pipeline(inputs, created_at="2026-09-05T00:00:00Z")

    assert run1["receipt_id"] == run2["receipt_id"]
    assert json.dumps(run1, sort_keys=True) == json.dumps(run2, sort_keys=True)


def test_fail_closed_on_activation_claims() -> None:
    inputs = load_bronchiectasis_reference_inputs(ROOT)
    bad_inputs = deepcopy(inputs)
    bad_inputs["bindings"]["claims"]["empirical_activation"] = True

    with pytest.raises(DemonstratorError, match="activation"):
        execute_bronchiectasis_reference_pipeline(bad_inputs)
