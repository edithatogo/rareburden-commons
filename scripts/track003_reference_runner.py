"""Pure synthetic reference calculations; no CLI, persistence or execution authority.

Fixture calls test the implementation. Retained governed results require a separate
exact candidate, scenario registration and disposition. No empirical inputs are accepted.
"""

from copy import deepcopy
from math import floor, isfinite
from pathlib import Path
from statistics import fmean, stdev
from typing import Any

from rareburden.model import sample_distribution
from rareburden.stochastic import StableRandom
from scripts.track003_reference_inputs import ASSUMPTIONS, validate_reference_inputs

SCENARIOS = (
    "primary",
    "denominator_low",
    "denominator_high",
    "ascertainment",
    "carrier_penetrance",
    "referral_selection",
    "age_stratified",
    "calendar_2030",
    "model_eligibility",
    "unclassified",
    "strata_independent",
    "strata_shared",
)

METRICS = {
    "modelled_denominator": ("people", "model-covered/classified diabetes scope"),
    "unavailable_denominator": ("people", "diabetes population with unavailable aetiology"),
    "assumed_case_probability": ("proportion", "assumed within modelled diabetes scope"),
    "assumed_detected_probability": ("proportion", "assumed within modelled diabetes scope"),
    "assumed_undetected_given_case_probability": ("proportion", "assumed conditional on case"),
    "expected_people": ("people", "expressed cases in modelled diabetes scope"),
    "detected_people": ("people", "modelled detected cases; not observed diagnoses"),
    "undetected_people": ("people", "modelled undetected expressed cases"),
    "assumed_delay_given_detection_years": ("years", "assumed historical conditional delay"),
    "treatment_change_people": ("people", "hypothetical change among detected cases; no benefit"),
    "complication_people": ("people", "one hypothetical event at most per case over full year"),
    "annual_cost": ("synthetic_currency_units", "one full year, constant fictional 2025 prices"),
    "selected_fraction": ("proportion", "assumed within selected cohort; count unavailable"),
    "young_expected_people": ("people", "expressed cases in disjoint age 0-19 stratum"),
    "adult_expected_people": ("people", "expressed cases in disjoint age 20-100 stratum"),
}


def central_inputs() -> dict[str, float]:
    """Declared central values; nonlinear plug-in outputs are not expected values."""
    values = {}
    for name, (_, _, distribution, _) in ASSUMPTIONS.items():
        kind = distribution["type"]
        if kind == "fixed":
            value = distribution["value"]
        elif kind == "normal":
            value = distribution["mean"]
        elif kind == "uniform":
            value = (distribution["lower"] + distribution["upper"]) / 2
        elif kind == "beta":
            value = distribution["alpha"] / (distribution["alpha"] + distribution["beta"])
        else:
            raise ValueError(f"unsupported central-value distribution: {kind}")
        values[name] = float(value)
    return values


def _finite_nonnegative(name: str, value: float) -> None:
    try:
        valid = not isinstance(value, bool) and isinstance(value, (int, float))
        valid = valid and isfinite(value) and value >= 0
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f"{name} must be a finite nonnegative number")


def _odds_transform(probability: float, ratio: float) -> float:
    return ratio * probability / (1 - probability + ratio * probability)


def evaluate(
    values: dict[str, float], scenario: str, *, second_fraction: float | None = None
) -> dict[str, float]:
    """Evaluate one invented draw in aligned fictional populations.

    Forward referral selection preserves the role of the declared target fraction.
    No selected-cohort count or burden in uncovered subsets is inferred.
    """
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario}")
    if set(values) != set(ASSUMPTIONS):
        raise ValueError("input names must exactly match the reference assumptions")
    for name, value in values.items():
        _finite_nonnegative(name, value)
        if ASSUMPTIONS[name][0] == "fraction" and value > 1:
            raise ValueError(f"{name} must not exceed one")
        if name.endswith("ratio") and value <= 0:
            raise ValueError(f"{name} must be positive")
    n = values["diabetes-denominator"]
    p = values["aetiologic-fraction"]
    d = values["detection"]
    w = values["young-denominator-share"]
    unavailable = 0.0
    extra = {}
    if scenario == "denominator_low":
        n *= values["denominator-low-scale"]
    elif scenario == "denominator_high":
        n *= values["denominator-high-scale"]
    elif scenario == "ascertainment":
        d = 1.0
    elif scenario == "carrier_penetrance":
        p = values["carrier-person-fraction"] * values["penetrance"]
    elif scenario == "referral_selection":
        extra["selected_fraction"] = _odds_transform(p, values["referral-selection-ratio"])
    elif scenario == "age_stratified":
        young = _odds_transform(p, values["young-case-odds-ratio"])
        adult = _odds_transform(p, values["adult-case-odds-ratio"])
        extra = {
            "young_expected_people": n * w * young,
            "adult_expected_people": n * (1 - w) * adult,
        }
        p = w * young + (1 - w) * adult
    elif scenario == "calendar_2030":
        p = _odds_transform(p, values["calendar-case-odds-ratio"])
    elif scenario in {"model_eligibility", "unclassified"}:
        share = (
            values["model-eligible-share"]
            if scenario == "model_eligibility"
            else (1 - values["unclassified-share"])
        )
        unavailable = n * (1 - share)
        n *= share
    elif scenario == "strata_independent":
        second = p if second_fraction is None else second_fraction
        _finite_nonnegative("second_fraction", second)
        if second > 1:
            raise ValueError("second_fraction must not exceed one")
        p = w * p + (1 - w) * second
    # Shared strata are exactly the primary model, without roundoff from recombination.
    cases = n * p
    detected = cases * d
    result = {
        "modelled_denominator": n,
        "unavailable_denominator": unavailable,
        "assumed_case_probability": p,
        "assumed_detected_probability": p * d,
        "assumed_undetected_given_case_probability": 1 - d,
        "expected_people": cases,
        "detected_people": detected,
        "undetected_people": cases - detected,
        "assumed_delay_given_detection_years": values["diagnosis-delay"],
        "treatment_change_people": detected * values["treatment-change"],
        "complication_people": cases * values["annual-complication"],
        "annual_cost": cases * values["annual-person-cost"],
        **extra,
    }
    for name, value in result.items():
        _finite_nonnegative(name, value)
    return result


def _summary(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)

    def quantile(probability: float) -> float:
        position = (len(ordered) - 1) * probability
        left = floor(position)
        weight = position - left
        return ordered[left] * (1 - weight) + ordered[min(left + 1, len(ordered) - 1)] * weight

    return {
        "mean": fmean(values),
        "median": quantile(0.5),
        "lower": quantile(0.025),
        "upper": quantile(0.975),
        "standard_deviation": stdev(values),
    }


def scenario_context(scenario: str) -> dict[str, Any]:
    """Explicit scenario applicability assumptions, not empirical transport evidence."""
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario}")
    return {
        "geography": "synthetic-rbc-p002",
        "year": 2030 if scenario == "calendar_2030" else 2025,
        "age_range": [0, 100],
        "cost_price_year": 2025,
        "cost_unit": "synthetic_currency_units",
        "denominator_scope": {
            "model_eligibility": "model-covered subset only; uncovered burden unavailable",
            "unclassified": "classified subset only; unclassified burden unavailable",
        }.get(scenario, "full fictional diabetes cohort"),
        "scenario_assumption": {
            "primary": "Independent assumed parameter uncertainty; no event sampling",
            "denominator_low": "Compatible denominator scaled by assumed low factor",
            "denominator_high": "Compatible denominator scaled by assumed high factor",
            "ascertainment": "Perfect detection counterfactual; no causal outcome benefit",
            "carrier_penetrance": "Conditional person-carrier expression within diabetes",
            "referral_selection": "Forward selected fraction only; referral count unavailable",
            "age_stratified": "Disjoint 0-19 and 20-100 strata; assumed odds multipliers",
            "calendar_2030": "2030 odds contrast; denominator held fixed; not a forecast",
            "model_eligibility": "Assumed same fraction in covered subset; no ancestry biology",
            "unclassified": "Assumed same fraction in classified subset; no missing imputation",
            "strata_independent": "Independent fraction draws in unnamed disjoint strata",
            "strata_shared": "Perfectly shared fraction draw in unnamed disjoint strata",
        }[scenario],
        "transport_status": "assumed_scenario_applicability_not_empirical_transfer",
        "total_population_prevalence": "unavailable_no_total_population_denominator",
        "observed_diagnosis": "unavailable_modelled_detection_only",
        "parameter_ids": [f"rbc-p002-reference-{name}" for name in sorted(ASSUMPTIONS)],
        "parameter_binding": "All inputs bound; unused draws retained for stream stability",
        "structural_override": {"detection": 1.0} if scenario == "ascertainment" else {},
    }


def simulate(
    candidate: dict[str, Any], root: Path, *, iterations: int, seed: int
) -> dict[str, Any]:
    """Return aggregate fixture summaries; caller receives no authorization to publish.

    Common random numbers align scenario comparisons. A separate fraction draw is
    used only by the independent-strata scenario. Numeric iteration order is fixed.
    """
    if (
        isinstance(iterations, bool)
        or not isinstance(iterations, int)
        or not 100 <= iterations <= 10000
    ):
        raise ValueError("iterations must be an integer between 100 and 10000")
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**64:
        raise ValueError("seed must be an unsigned 64-bit integer")
    validate_reference_inputs(candidate, root)
    rng = StableRandom(seed)
    distributions = {name: ASSUMPTIONS[name][2] for name in sorted(ASSUMPTIONS)}
    series: dict[str, dict[str, list[float]]] = {scenario: {} for scenario in SCENARIOS}
    for _ in range(iterations):
        values = {name: sample_distribution(spec, rng) for name, spec in distributions.items()}
        second = sample_distribution(distributions["aetiologic-fraction"], rng)
        for scenario in SCENARIOS:
            result = evaluate(values, scenario, second_fraction=second)
            for name, value in result.items():
                series[scenario].setdefault(name, []).append(value)
    return {
        "version": "RBC-P002-REFERENCE-RUNNER-v1",
        "status": "in_memory_synthetic_calculation_not_execution_receipt",
        "random_engine": StableRandom.engine_id,
        "seed": seed,
        "iterations": iterations,
        "interval_probability": 0.95,
        "interval_interpretation": "Invented parameter uncertainty; not empirical confidence",
        "deterministic_interpretation": "Plug-in central values, not nonlinear expectations",
        "claims": deepcopy(candidate["claims"]),
        "scenarios": {
            scenario: {
                "context": scenario_context(scenario),
                "deterministic": evaluate(central_inputs(), scenario),
                "summaries": {name: _summary(values) for name, values in series[scenario].items()},
                "metric_metadata": {
                    name: {
                        "unit": METRICS[name][0],
                        "conditioning_scope": METRICS[name][1],
                        "evidence_status": "synthetic_assumption",
                    }
                    for name in series[scenario]
                },
            }
            for scenario in SCENARIOS
        },
    }
