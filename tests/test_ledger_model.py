from __future__ import annotations

import math
from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.ledger import LedgerError, load_ledger, validate_ledger
from rareburden.model import (
    ModelError,
    apply_case_fraction,
    expected_affected_population,
    rare_aetiology_cases,
    run_analysis_spec,
    sample_distribution,
    simulate_product,
)
from rareburden.schema import load_mapping, validate_instance
from rareburden.stochastic import StableRandom

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "examples/ledger/public-foundation-synthetic.yml"
LEDGER_SCHEMA = ROOT / "schemas/parameter-ledger.schema.json"
ANALYSIS_PATH = ROOT / "examples/analyses/expected-population-synthetic.yml"
ANALYSIS_SCHEMA = ROOT / "schemas/analysis-specification.schema.json"
RESULT_SCHEMA = ROOT / "schemas/analysis-result.schema.json"


def _ledger_document() -> dict[str, object]:
    return deepcopy(load_mapping(LEDGER_PATH))


def test_reference_ledger_analysis_is_reproducible_and_schema_valid() -> None:
    ledger = load_ledger(LEDGER_PATH, LEDGER_SCHEMA)
    specification = load_mapping(ANALYSIS_PATH)
    validate_instance(specification, load_mapping(ANALYSIS_SCHEMA), label="analysis")
    first = run_analysis_spec(specification, ledger, created_at="2026-07-19T00:00:00Z")
    second = run_analysis_spec(specification, ledger, created_at="2026-07-19T00:00:00Z")
    assert first == second
    assert first["analysis_result_id"].startswith("ana-")
    assert first["summary"]["lower"] < first["summary"]["median"] < first["summary"]["upper"]
    assert first["summary"]["standard_deviation"] > 0
    validate_instance(first, load_mapping(RESULT_SCHEMA), label="result")
    assert ledger.fingerprint("australia-population-synthetic").startswith("par-")
    assert first["intended_use"] == "synthetic_assurance"
    assert first["activation_state"] == "not_activated"
    assert "not an empirical" in first["interpretation"]
    with pytest.raises(LedgerError, match="Unknown parameter_id"):
        ledger.get("missing")


def test_ledger_rejects_duplicate_assumption_and_provenance_failures() -> None:
    schema = load_mapping(LEDGER_SCHEMA)

    duplicate = _ledger_document()
    duplicate["parameters"].append(deepcopy(duplicate["parameters"][0]))  # type: ignore[index,union-attr]
    with pytest.raises(LedgerError, match="Duplicate parameter_id"):
        validate_ledger(duplicate, schema)

    missing_rationale = _ledger_document()
    assumed = missing_rationale["parameters"][1]  # type: ignore[index]
    assumed.pop("assumption_rationale")
    with pytest.raises(LedgerError, match="assumption_rationale"):
        validate_ledger(missing_rationale, schema)

    missing_source = _ledger_document()
    observed = missing_source["parameters"][0]  # type: ignore[index]
    observed["source_release_ids"] = []
    with pytest.raises(LedgerError, match="source_release_id"):
        validate_ledger(missing_source, schema)


def test_ledger_rejects_revision_without_a_nonempty_supersession_receipt() -> None:
    schema = load_mapping(LEDGER_SCHEMA)
    missing_receipt = _ledger_document()
    record = missing_receipt["parameters"][0]  # type: ignore[index]
    record["parameter_revision"] = 2
    record["supersedes_parameter_fingerprint"] = ""
    with pytest.raises(LedgerError):
        validate_ledger(missing_receipt, schema)


def test_ledger_rejects_distribution_and_fraction_invariants() -> None:
    schema = load_mapping(LEDGER_SCHEMA)

    reversed_uniform = _ledger_document()
    distribution = reversed_uniform["parameters"][0]["distribution"]  # type: ignore[index]
    distribution.clear()
    distribution.update({"type": "uniform", "lower": 2, "upper": 1})
    with pytest.raises(LedgerError, match="uniform lower exceeds upper"):
        validate_ledger(reversed_uniform, schema)

    invalid_fraction = _ledger_document()
    distribution = invalid_fraction["parameters"][1]["distribution"]  # type: ignore[index]
    distribution.clear()
    distribution.update({"type": "fixed", "value": 1.2})
    with pytest.raises(LedgerError, match="fixed fraction"):
        validate_ledger(invalid_fraction, schema)

    unbounded_normal_fraction = _ledger_document()
    distribution = unbounded_normal_fraction["parameters"][1]["distribution"]  # type: ignore[index]
    distribution.clear()
    distribution.update({"type": "normal", "mean": 0.1, "standard_deviation": 0.01})
    with pytest.raises(LedgerError, match="explicit minimum and maximum"):
        validate_ledger(unbounded_normal_fraction, schema)

    lognormal_fraction = _ledger_document()
    distribution = lognormal_fraction["parameters"][1]["distribution"]  # type: ignore[index]
    distribution.clear()
    distribution.update({"type": "lognormal", "mu": -2.0, "sigma": 0.5})
    with pytest.raises(LedgerError, match="lognormal is not supported"):
        validate_ledger(lognormal_fraction, schema)


def test_model_scalar_guards_and_metric_safety() -> None:
    assert expected_affected_population(1000, 0.2) == 200
    assert rare_aetiology_cases(500, 0.1) == 50
    assert apply_case_fraction(100, 0.2, envelope_metric="count") == 20
    assert apply_case_fraction(100, 0.2, envelope_metric="cost", explicit_outcome_model=True) == 20
    for value in (-1.0, math.inf, math.nan):
        with pytest.raises(ModelError, match="non-negative"):
            expected_affected_population(value, 0.1)
    for value in (-0.1, 1.1, math.inf, math.nan):
        with pytest.raises(ModelError, match="fraction"):
            expected_affected_population(100, value)
    with pytest.raises(ModelError, match="explicit outcome model"):
        apply_case_fraction(100, 0.2, envelope_metric="DALYs")
    with pytest.raises(ModelError, match="Unsupported envelope metric"):
        apply_case_fraction(100, 0.2, envelope_metric="rate")


def test_all_distribution_types_and_failures() -> None:
    rng = StableRandom(7)
    assert sample_distribution({"type": "fixed", "value": 4}, rng) == 4
    assert 1 <= sample_distribution({"type": "uniform", "lower": 1, "upper": 2}, rng) <= 2
    assert (
        sample_distribution(
            {
                "type": "normal",
                "mean": 5,
                "standard_deviation": 1,
                "minimum": 0,
                "maximum": 10,
            },
            rng,
        )
        >= 0
    )
    assert sample_distribution({"type": "lognormal", "mu": 0, "sigma": 0.5}, rng) > 0
    assert 0 <= sample_distribution({"type": "beta", "alpha": 2, "beta": 3}, rng) <= 1

    invalid_specs = (
        ({"type": "uniform", "lower": 2, "upper": 1}, "uniform lower"),
        ({"type": "normal", "mean": 0, "standard_deviation": 0}, "positive"),
        (
            {
                "type": "normal",
                "mean": 0,
                "standard_deviation": 1,
                "minimum": 2,
                "maximum": 1,
            },
            "minimum exceeds",
        ),
        ({"type": "lognormal", "mu": 0, "sigma": 0}, "positive"),
        ({"type": "beta", "alpha": 0, "beta": 1}, "positive"),
        ({"type": "unknown"}, "Unsupported distribution"),
        ({"type": "fixed", "value": math.inf}, "non-finite"),
        ({"type": "fixed", "value": -1, "minimum": 0}, "below"),
        ({"type": "fixed", "value": 2, "maximum": 1}, "above"),
    )
    for spec, message in invalid_specs:
        with pytest.raises(ModelError, match=message):
            sample_distribution(spec, StableRandom(1))


def test_simulation_limits_and_analysis_type_checks() -> None:
    fixed = {"type": "fixed", "value": 2}
    summary = simulate_product(fixed, fixed, iterations=100, seed=1)
    assert summary.mean == 4
    assert summary.standard_deviation == 0
    for kwargs, message in (
        ({"iterations": 99, "seed": 1}, "at least 100"),
        ({"iterations": 100_001, "seed": 1}, "must not exceed"),
        ({"iterations": 100, "seed": 1, "interval_probability": 1.0}, "between"),
        ({"iterations": 100, "seed": 1, "dependence": "correlated"}, "dependence"),
    ):
        with pytest.raises(ModelError, match=message):
            simulate_product(fixed, fixed, **kwargs)

    for seed in (-1, True, 1.5):
        with pytest.raises(ModelError, match="seed must be a non-negative integer"):
            simulate_product(fixed, fixed, iterations=100, seed=seed)  # type: ignore[arg-type]

    ledger = load_ledger(LEDGER_PATH, LEDGER_SCHEMA)
    spec = load_mapping(ANALYSIS_PATH)
    wrong = deepcopy(spec)
    wrong["output_unit"] = "dollars"
    with pytest.raises(ModelError, match="person-count"):
        run_analysis_spec(wrong, ledger)
    wrong = deepcopy(spec)
    wrong["estimand"] = "rare_aetiology_cases"
    with pytest.raises(ModelError, match="case_count"):
        run_analysis_spec(wrong, ledger)
    wrong = deepcopy(spec)
    wrong["estimand"] = "not-supported"
    with pytest.raises(ModelError, match="Unsupported estimand"):
        run_analysis_spec(wrong, ledger)


def test_public_analysis_execution_remains_fail_closed_with_a_disposition() -> None:
    ledger = load_ledger(LEDGER_PATH, LEDGER_SCHEMA)
    specification = deepcopy(load_mapping(ANALYSIS_PATH))
    specification["intended_use"] = "policy_decision"
    with pytest.raises(ModelError, match="public analysis execution is not activated"):
        run_analysis_spec(specification, ledger)

    disposition = {
        "disposition_id": "qdp-0123456789abcdef01234567",
        "analysis_id": specification["analysis_id"],
        "intended_use": "policy_decision",
        "eligible_for_primary_analysis": True,
        "eligible_for_synthetic_assurance": False,
    }
    with pytest.raises(ModelError, match="public analysis execution is not activated"):
        run_analysis_spec(specification, ledger, quality_disposition=disposition)


@pytest.mark.parametrize(
    "mutation,message",
    [
        ({"analysis_id": "different-analysis"}, "analysis_id differs"),
        ({"intended_use": "policy_decision"}, "intended_use differs"),
        ({"eligible_for_synthetic_assurance": False}, "does not permit synthetic assurance"),
    ],
)
def test_synthetic_quality_disposition_must_match_and_remain_eligible(
    mutation: dict[str, object], message: str
) -> None:
    ledger = load_ledger(LEDGER_PATH, LEDGER_SCHEMA)
    specification = deepcopy(load_mapping(ANALYSIS_PATH))
    disposition: dict[str, object] = {
        "disposition_id": "qdp-757f1136634049b87de6ee07",
        "analysis_id": specification["analysis_id"],
        "intended_use": "synthetic_assurance",
        "eligible_for_synthetic_assurance": True,
    }
    disposition.update(mutation)
    with pytest.raises(ModelError, match=message):
        run_analysis_spec(specification, ledger, quality_disposition=disposition)


@pytest.mark.parametrize(
    "field,value", [("iterations", True), ("iterations", 100.5), ("seed", True), ("seed", 1.5)]
)
def test_analysis_rejects_non_integer_iterations_and_seed(field: str, value: object) -> None:
    ledger = load_ledger(LEDGER_PATH, LEDGER_SCHEMA)
    specification = deepcopy(load_mapping(ANALYSIS_PATH))
    specification[field] = value
    with pytest.raises(ModelError, match=f"{field} must be"):
        run_analysis_spec(specification, ledger)


def test_analysis_rejects_incompatible_population_and_period_contexts() -> None:
    document = _ledger_document()
    fraction = document["parameters"][1]  # type: ignore[index]
    fraction["period"] = {"start": "2020-01-01", "end": "2020-12-31"}
    ledger = validate_ledger(document, load_mapping(LEDGER_SCHEMA))
    with pytest.raises(ModelError, match="incompatible parameter period contexts"):
        run_analysis_spec(load_mapping(ANALYSIS_PATH), ledger)


def test_synthetic_assurance_rejects_relabelled_non_synthetic_provenance() -> None:
    document = _ledger_document()
    parameter = document["parameters"][0]  # type: ignore[index]
    parameter["semantic_entity_ids"] = ["population-au"]
    parameter["source_release_ids"] = ["official-public-aggregate"]
    ledger = validate_ledger(document, load_mapping(LEDGER_SCHEMA))
    with pytest.raises(ModelError, match="explicitly synthetic parameter provenance"):
        run_analysis_spec(load_mapping(ANALYSIS_PATH), ledger)
