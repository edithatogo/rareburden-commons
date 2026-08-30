"""Numerical fixtures, not retained governed reference execution."""

from pathlib import Path

import pytest

from scripts.track003_reference_inputs import build_reference_inputs
from scripts.track003_reference_runner import central_inputs, evaluate, simulate

ROOT = Path(__file__).resolve().parents[1]


def test_primary_and_perfect_detection_preserve_noncausal_outcomes():
    values = central_inputs()
    primary = evaluate(values, "primary")
    perfect = evaluate(values, "ascertainment")
    assert primary["expected_people"] == 2000
    assert primary["detected_people"] == 1200
    assert primary["undetected_people"] == 800
    assert perfect["detected_people"] == 2000
    assert perfect["undetected_people"] == 0
    assert primary["annual_cost"] == perfect["annual_cost"] == 4000000
    assert primary["complication_people"] == perfect["complication_people"] == 40
    assert primary["treatment_change_people"] == 480
    assert primary["assumed_delay_given_detection_years"] == 3


def test_referral_does_not_multiply_selected_fraction_into_population():
    result = evaluate(central_inputs(), "referral_selection")
    assert result["selected_fraction"] == pytest.approx(2 * 0.02 / 1.02)
    assert result["expected_people"] == 2000
    assert "referral_people" not in result


@pytest.mark.parametrize(
    "scenario,denominator,unknown",
    [
        ("model_eligibility", 50000, 50000),
        ("unclassified", 90000, 10000),
    ],
)
def test_subset_does_not_impute_missing_burden(scenario, denominator, unknown):
    result = evaluate(central_inputs(), scenario)
    assert result["modelled_denominator"] == denominator
    assert result["unavailable_denominator"] == pytest.approx(unknown)
    assert result["modelled_denominator"] + result["unavailable_denominator"] == pytest.approx(
        100000
    )
    assert result["expected_people"] == denominator * 0.02
    assert "unavailable_cases" not in result


@pytest.mark.parametrize("scenario", build_reference_inputs(ROOT)["required_scenarios"])
def test_all_scenarios_preserve_partitions(scenario):
    result = evaluate(central_inputs(), scenario)
    assert result["expected_people"] == pytest.approx(
        result["detected_people"] + result["undetected_people"]
    )
    assert 0 <= result["assumed_case_probability"] <= 1
    assert result["treatment_change_people"] <= result["detected_people"]
    assert result["complication_people"] <= result["expected_people"]


def test_stratum_dependence_and_age_contrast():
    values = central_inputs()
    assert evaluate(values, "strata_shared") == evaluate(values, "primary")
    assert evaluate(values, "strata_independent", second_fraction=0.04)[
        "assumed_case_probability"
    ] == pytest.approx(0.035)
    age = evaluate(values, "age_stratified")
    assert age["expected_people"] == pytest.approx(
        age["young_expected_people"] + age["adult_expected_people"]
    )


def test_simulation_is_reproducible_and_bounded_summary_only():
    inputs = build_reference_inputs(ROOT)
    first = simulate(inputs, ROOT, iterations=100, seed=17)
    assert first == simulate(inputs, ROOT, iterations=100, seed=17)
    assert first != simulate(inputs, ROOT, iterations=100, seed=18)
    assert len(first["scenarios"]) == 12
    assert "draws" not in first
    primary = first["scenarios"]["primary"]["summaries"]["expected_people"]
    assert primary["lower"] <= primary["median"] <= primary["upper"]
    assert (
        first["scenarios"]["strata_shared"]["summaries"]
        == first["scenarios"]["primary"]["summaries"]
    )
    assert first["scenarios"]["calendar_2030"]["context"]["year"] == 2030
    assert first["claims"]["execution_authorized"] is False
    for scenario in first["scenarios"].values():
        assert set(scenario["summaries"]) == set(scenario["metric_metadata"])
        assert len(scenario["context"]["parameter_ids"]) == 18


@pytest.mark.parametrize("field", ["aetiologic-fraction", "detection", "penetrance"])
@pytest.mark.parametrize("bad", [-1, 1.01, True, float("nan"), float("inf")])
def test_invalid_fraction_inputs(field, bad):
    values = central_inputs()
    values[field] = bad
    with pytest.raises(ValueError):
        evaluate(values, "primary")


@pytest.mark.parametrize("bad", [-1, 0, True, float("nan"), float("inf")])
def test_invalid_selection_ratios(bad):
    values = central_inputs()
    values["referral-selection-ratio"] = bad
    with pytest.raises(ValueError):
        evaluate(values, "referral_selection")


@pytest.mark.parametrize("bad", [-1, 1.01, True, float("nan"), float("inf")])
def test_invalid_second_fraction(bad):
    with pytest.raises(ValueError):
        evaluate(central_inputs(), "strata_independent", second_fraction=bad)


@pytest.mark.parametrize("iterations", [True, 99, 100001, 100.5])
def test_invalid_iterations(iterations):
    with pytest.raises(ValueError, match="iterations"):
        simulate(build_reference_inputs(ROOT), ROOT, iterations=iterations, seed=1)


@pytest.mark.parametrize("seed", [True, -1, 2**64, 1.5])
def test_invalid_seed(seed):
    with pytest.raises(ValueError, match="seed"):
        simulate(build_reference_inputs(ROOT), ROOT, iterations=100, seed=seed)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), True, -1, 10**400])
def test_invalid_numeric_inputs(bad):
    values = central_inputs()
    values["diabetes-denominator"] = bad
    with pytest.raises(ValueError):
        evaluate(values, "primary")


def test_input_drift_and_unknown_scenarios_rejected():
    candidate = build_reference_inputs(ROOT)
    candidate["claims"]["execution_authorized"] = True
    with pytest.raises(ValueError, match="drift"):
        simulate(candidate, ROOT, iterations=100, seed=1)
    with pytest.raises(ValueError, match="scenario"):
        evaluate(central_inputs(), "unknown")


@pytest.mark.parametrize(
    "scenario,zero_field",
    [
        ("primary", "diabetes-denominator"),
        ("primary", "aetiologic-fraction"),
        ("primary", "detection"),
        ("model_eligibility", "model-eligible-share"),
        ("carrier_penetrance", "penetrance"),
    ],
)
def test_empty_conditioning_sets_keep_inputs_labelled_as_assumptions(scenario, zero_field):
    values = central_inputs()
    values[zero_field] = 0
    result = evaluate(values, scenario)
    assert result["detected_people"] == 0
    assert result["treatment_change_people"] == 0
    assert result["assumed_delay_given_detection_years"] == 3
    assert "diagnosis_delay_years" not in result
    assert "undetected_case_share" not in result
