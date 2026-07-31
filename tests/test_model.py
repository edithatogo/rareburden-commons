from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.ledger import load_ledger
from rareburden.model import (
    ModelError,
    apply_case_fraction,
    run_analysis_spec,
    simulate_product,
)
from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "examples" / "ledger" / "public-foundation-synthetic.yml"
LEDGER_SCHEMA = ROOT / "schemas" / "parameter-ledger.schema.json"
SPEC_PATH = ROOT / "examples" / "analyses" / "expected-population-synthetic.yml"
SPEC_SCHEMA = ROOT / "schemas" / "analysis-specification.schema.json"
RESULT_SCHEMA = ROOT / "schemas" / "analysis-result.schema.json"


def test_reference_analysis_is_seeded_schema_valid_and_content_identified() -> None:
    ledger = load_ledger(LEDGER_PATH, LEDGER_SCHEMA)
    specification = load_mapping(SPEC_PATH)
    validate_instance(specification, load_mapping(SPEC_SCHEMA), label="analysis")
    first = run_analysis_spec(specification, ledger, created_at="2026-07-19T00:00:00Z")
    second = run_analysis_spec(specification, ledger, created_at="2026-07-20T00:00:00Z")
    validate_instance(first, load_mapping(RESULT_SCHEMA), label="result")
    assert first["analysis_result_id"] == second["analysis_result_id"]
    assert first["summary"] == second["summary"]
    assert first["created_at"] != second["created_at"]
    assert first["runtime"]["random_engine"].endswith(".v1")
    assert first["summary"]["lower"] < first["summary"]["median"] < first["summary"]["upper"]


def test_independence_must_be_explicit_and_supported() -> None:
    fixed = {"type": "fixed", "value": 10}
    with pytest.raises(ModelError, match="only explicit independence"):
        simulate_product(fixed, fixed, iterations=100, seed=1, dependence="correlated")


def test_analysis_schema_rejects_missing_dependence_rationale() -> None:
    invalid = deepcopy(load_mapping(SPEC_PATH))
    invalid.pop("dependence_rationale")
    with pytest.raises(ValueError, match="dependence_rationale"):
        validate_instance(invalid, load_mapping(SPEC_SCHEMA), label="analysis")


def test_case_fraction_fails_closed_for_health_loss_and_cost() -> None:
    for metric in ("DALYs", "YLL", "cost"):
        with pytest.raises(ModelError, match="explicit outcome model"):
            apply_case_fraction(100, 0.1, envelope_metric=metric)


def test_run_analysis_rejects_incompatible_units() -> None:
    ledger = load_ledger(LEDGER_PATH, LEDGER_SCHEMA)
    specification = deepcopy(load_mapping(SPEC_PATH))
    specification["output_unit"] = "USD"
    with pytest.raises(ModelError, match="person-count"):
        run_analysis_spec(specification, ledger, created_at="2026-07-19T00:00:00Z")
