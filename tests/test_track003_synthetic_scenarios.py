"""Arithmetic assurance only: no empirical inputs or persisted analysis outputs."""

import math

import pytest

from scripts.track003_synthetic_scenarios import (
    SyntheticScenario,
    evaluate_synthetic_scenario,
)


def scenario(**changes):
    fields = {"diabetes_denominator": 100_000.0, "fraction": 0.02}
    fields.update(changes)
    return SyntheticScenario(**fields)


def test_identity_and_labels():
    result = evaluate_synthetic_scenario(scenario())
    assert result.expected_people == 2000
    assert result.detected_people == 2000
    assert result.undetected_people == 0
    assert result.evidence_status == "synthetic_assumption"
    assert result.unit == "people"
    assert result.uncertainty == "not_quantified"


@pytest.mark.parametrize("denominator", [0, 50_000, 100_000, 200_000])
def test_denominator_scaling(denominator):
    result = evaluate_synthetic_scenario(scenario(diabetes_denominator=denominator))
    assert result.expected_people == denominator * 0.02


@pytest.mark.parametrize("detection", [0, 0.25, 0.6, 1])
def test_detection_is_a_forward_latent_partition_not_observation(detection):
    result = evaluate_synthetic_scenario(scenario(detection=detection))
    assert result.detected_people == 2000 * detection
    assert result.undetected_people == pytest.approx(2000 * (1 - detection))
    assert result.detected_people + result.undetected_people == result.expected_people


@pytest.mark.parametrize("penetrance", [0, 0.25, 0.5, 1])
def test_penetrance_requires_person_carriers_in_aligned_diabetes_envelope(penetrance):
    result = evaluate_synthetic_scenario(
        scenario(fraction_kind="carrier_person_fraction", penetrance=penetrance)
    )
    assert result.expected_people == 2000 * penetrance


@pytest.mark.parametrize("ratio", [0.01, 0.5, 1, 2, 100])
@pytest.mark.parametrize("target", [0, 0.02, 0.5, 1])
def test_selection_round_trip(ratio, target):
    selected = ratio * target / (1 - target + ratio * target)
    result = evaluate_synthetic_scenario(scenario(fraction=selected, selection_ratio=ratio))
    assert result.expected_people == pytest.approx(100_000 * target)


@pytest.mark.parametrize(
    "field", ["diabetes_denominator", "fraction", "detection", "selection_ratio"]
)
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), True, "0.5"])
def test_invalid_numeric_values_fail(field, value):
    with pytest.raises(ValueError, match=field):
        evaluate_synthetic_scenario(scenario(**{field: value}))


@pytest.mark.parametrize(
    "changes",
    [
        {"diabetes_denominator": -1},
        {"fraction": -0.1},
        {"fraction": 1.1},
        {"detection": -0.1},
        {"detection": 1.1},
        {"selection_ratio": 0},
        {"selection_ratio": -1},
        {"fraction_kind": "allele_frequency"},
        {"fraction_kind": "carrier_person_fraction"},
        {"penetrance": 0.5},
        {"fraction_kind": "carrier_person_fraction", "penetrance": -1},
        {"fraction_kind": "carrier_person_fraction", "penetrance": 2},
        {"fraction_kind": "carrier_person_fraction", "penetrance": math.nan},
    ],
)
def test_unsupported_or_incomplete_scenarios_fail(changes):
    with pytest.raises(ValueError):
        evaluate_synthetic_scenario(scenario(**changes))


def test_extreme_selection_ratio_stays_finite():
    for ratio in [5e-324, 1e308]:
        result = evaluate_synthetic_scenario(scenario(selection_ratio=ratio))
        assert math.isfinite(result.expected_people)
        assert 0 <= result.expected_people <= 100_000


@pytest.mark.parametrize(
    "field", ["diabetes_denominator", "fraction", "detection", "selection_ratio", "penetrance"]
)
def test_unrepresentable_integer_fails_with_field_name(field):
    changes = {field: 10**309}
    if field == "penetrance":
        changes["fraction_kind"] = "carrier_person_fraction"
    with pytest.raises(ValueError, match=field):
        evaluate_synthetic_scenario(scenario(**changes))


def test_reproducible_immutable_in_memory_result():
    case = scenario(detection=0.6, selection_ratio=2)
    assert evaluate_synthetic_scenario(case) == evaluate_synthetic_scenario(case)
    with pytest.raises(AttributeError):
        evaluate_synthetic_scenario(case).expected_people = 1
