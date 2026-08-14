from __future__ import annotations

from pathlib import Path

import yaml

MATRIX = Path(__file__).parents[1] / "docs/track-002-coverage-matrix.yml"


def test_coverage_matrix_is_candidate_bound_and_complete() -> None:
    document = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert document["status"] == "bounded_registration_only"
    ids = {row["estimand_id"] for row in document["rows"]}
    assert ids == {"E-ORPHA-DESCRIPTIVE-01", "E-WPP-POP-01", "E-WHO-COMP-2000", "E-WB-POP-PROBE"}
    required = {
        "geography_coverage",
        "year_coverage",
        "population_coverage",
        "numerator_coverage",
        "denominator_coverage",
        "missingness",
        "bias_and_uncertainty",
        "transportability",
        "representativeness_claim",
    }
    assert all(required <= row.keys() for row in document["rows"])


def test_coverage_matrix_prohibits_unbounded_representativeness() -> None:
    document = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert all(
        row["representativeness_claim"] == "prohibited"
        or "no global" in row["representativeness_claim"]
        for row in document["rows"]
    )
