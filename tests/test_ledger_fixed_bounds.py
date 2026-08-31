"""Validate declared fixed bounds without choosing economic valuation rules."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.ledger import LedgerError, validate_ledger
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/ledger/economic-social-synthetic.yml"
SCHEMA = ROOT / "schemas/parameter-ledger.schema.json"


def _validate(distribution: dict[str, object]):
    document = deepcopy(load_mapping(FIXTURE))
    document["parameters"][0]["distribution"] = distribution
    return validate_ledger(document, load_mapping(SCHEMA))


@pytest.mark.parametrize(
    "distribution,bound",
    [
        ({"type": "fixed", "value": 1200, "minimum": 1201}, "minimum"),
        ({"type": "fixed", "value": 1200, "maximum": 1199}, "maximum"),
        ({"type": "fixed", "value": -1, "minimum": 0}, "minimum"),
        ({"type": "fixed", "value": 1, "maximum": 0}, "maximum"),
        ({"type": "fixed", "value": -1, "maximum": -2}, "maximum"),
    ],
)
def test_fixed_values_outside_explicit_bounds_fail_before_sampling(distribution, bound):
    with pytest.raises(LedgerError, match=f"synthetic-health-system-cost: fixed value.*{bound}"):
        _validate(distribution)


@pytest.mark.parametrize(
    "distribution",
    [
        {"type": "fixed", "value": 1200, "minimum": 0},
        {"type": "fixed", "value": 1200, "minimum": 1200},
        {"type": "fixed", "value": 1200, "maximum": 1200},
        {"type": "fixed", "value": 0, "minimum": 0, "maximum": 0},
        {"type": "fixed", "value": -2, "minimum": -3, "maximum": -1},
        {"type": "fixed", "value": -2},
        {"type": "fixed", "value": 0},
    ],
)
def test_fixed_bounds_preserve_equality_zero_and_negative_values(distribution):
    ledger = _validate(distribution)
    assert ledger.records["synthetic-health-system-cost"]["distribution"] == distribution


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_fixed_values_still_raise_ledger_error(value):
    with pytest.raises(LedgerError, match="must be finite"):
        _validate({"type": "fixed", "value": value, "minimum": 0})


def test_missing_fixed_value_keeps_actionable_validation_error():
    with pytest.raises(LedgerError, match="distribution"):
        _validate({"type": "fixed", "minimum": 0})


@pytest.mark.parametrize("value", [True, "1", None])
def test_fixed_values_are_not_coerced(value):
    with pytest.raises(LedgerError):
        _validate({"type": "fixed", "value": value, "minimum": 0})


def test_bounded_normal_mean_is_not_treated_as_a_fixed_realization():
    distribution = {
        "type": "normal",
        "mean": -1,
        "standard_deviation": 1,
        "minimum": 0,
        "maximum": 2,
    }
    assert _validate(distribution).records["synthetic-health-system-cost"]["distribution"] == (
        distribution
    )
