from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.burden_assurance import (
    assess_analysis_estimability,
    run_structural_scenarios,
)
from rareburden.ledger import load_ledger
from rareburden.model import ModelError
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
LEDGER = load_ledger(
    ROOT / "examples/ledger/public-foundation-synthetic.yml",
    ROOT / "schemas/parameter-ledger.schema.json",
)
SPECIFICATION = load_mapping(ROOT / "examples/analyses/expected-population-synthetic.yml")


def test_estimability_reports_missing_inputs_without_imputation() -> None:
    missing = deepcopy(SPECIFICATION)
    missing["right_parameter_id"] = "missing-parameter"
    result = assess_analysis_estimability(missing, LEDGER)
    assert result == {
        "schema_version": "0.1.0",
        "analysis_id": "expected-population-synthetic",
        "estimable": False,
        "missing_parameter_ids": ["missing-parameter"],
        "reasons": ["parameter is unavailable: missing-parameter"],
        "imputation_performed": False,
    }
    assert assess_analysis_estimability(SPECIFICATION, LEDGER)["estimable"] is True


def test_structural_scenarios_are_reproducible_and_lineage_preserving() -> None:
    alternative = deepcopy(SPECIFICATION)
    alternative["seed"] = 20260720
    scenarios = {"baseline": deepcopy(SPECIFICATION), "alternative-seed": alternative}
    first = run_structural_scenarios(scenarios, LEDGER, created_at="2026-07-31T00:00:00Z")
    second = run_structural_scenarios(scenarios, LEDGER, created_at="2026-07-31T00:00:00Z")
    assert first == second
    assert first["scenario_result_id"].startswith("scn-")
    assert [item["scenario"] for item in first["scenarios"]] == [
        "alternative-seed",
        "baseline",
    ]
    assert all(item["left_parameter_fingerprint"].startswith("par-") for item in first["scenarios"])
    baseline = next(item for item in first["scenarios"] if item["scenario"] == "baseline")
    assert baseline["absolute_change_from_baseline"] == 0


@pytest.mark.parametrize(
    "scenarios, message",
    [
        ({"only": deepcopy(SPECIFICATION)}, "baseline"),
        ({"baseline": deepcopy(SPECIFICATION)}, "between 2 and 20"),
        (
            {
                "baseline": deepcopy(SPECIFICATION),
                "changed": {**deepcopy(SPECIFICATION), "output_unit": "dollars"},
            },
            "invariant field output_unit",
        ),
        (
            {
                "baseline": deepcopy(SPECIFICATION),
                "missing": {
                    **deepcopy(SPECIFICATION),
                    "right_parameter_id": "missing-parameter",
                },
            },
            "non-estimable",
        ),
    ],
)
def test_structural_scenarios_fail_closed(
    scenarios: dict[str, dict[str, object]], message: str
) -> None:
    with pytest.raises(ModelError, match=message):
        run_structural_scenarios(scenarios, LEDGER, created_at="2026-07-31T00:00:00Z")
