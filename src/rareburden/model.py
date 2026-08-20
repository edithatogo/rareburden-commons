"""Auditable population and rare-aetiology burden simulation primitives."""

from __future__ import annotations

import math
import platform
from collections.abc import Callable
from dataclasses import dataclass
from statistics import fmean
from typing import Any

from rareburden import __version__
from rareburden.ledger import ParameterLedger
from rareburden.provenance import content_id, utc_now
from rareburden.stochastic import StableRandom


class ModelError(ValueError):
    """Raised when an estimand is invalid or scientifically unsafe."""


_COUNT_COMPATIBLE_METRICS = {"count", "cases", "prevalence_count", "population"}
_OUTCOME_METRICS = {"daly", "dalys", "yll", "ylls", "yld", "ylds", "deaths", "cost"}
_PERSON_UNITS = {"people", "person", "persons"}


@dataclass(frozen=True)
class SimulationSummary:
    """Compact deterministic summary of a Monte Carlo product distribution."""

    mean: float
    median: float
    lower: float
    upper: float
    standard_deviation: float
    interval_probability: float
    iterations: int
    seed: int

    def as_dict(self) -> dict[str, int | float]:
        """Return the JSON-compatible simulation summary."""
        return {
            "mean": self.mean,
            "median": self.median,
            "lower": self.lower,
            "upper": self.upper,
            "standard_deviation": self.standard_deviation,
            "interval_probability": self.interval_probability,
            "iterations": self.iterations,
            "seed": self.seed,
        }


def _require_nonnegative(name: str, value: float) -> None:
    if not math.isfinite(value) or value < 0:
        raise ModelError(f"{name} must be finite and non-negative")


def _require_fraction(name: str, value: float) -> None:
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ModelError(f"{name} must be a finite fraction between zero and one")


def expected_affected_population(population: float, prevalence: float) -> float:
    """Estimate affected people from a population denominator and prevalence fraction."""
    _require_nonnegative("population", population)
    _require_fraction("prevalence", prevalence)
    return population * prevalence


def rare_aetiology_cases(envelope_cases: float, case_fraction: float) -> float:
    """Estimate rare-aetiology cases within a count-compatible disease envelope."""
    _require_nonnegative("envelope_cases", envelope_cases)
    _require_fraction("case_fraction", case_fraction)
    return envelope_cases * case_fraction


def apply_case_fraction(
    envelope_value: float,
    case_fraction: float,
    *,
    envelope_metric: str,
    explicit_outcome_model: bool = False,
) -> float:
    """Apply a case fraction only to scientifically compatible envelopes."""
    metric = envelope_metric.strip().lower()
    if metric in _OUTCOME_METRICS and not explicit_outcome_model:
        raise ModelError(
            f"Cannot apply a case fraction directly to {envelope_metric!r}; "
            "an explicit outcome model is required"
        )
    if metric not in _COUNT_COMPATIBLE_METRICS and not explicit_outcome_model:
        raise ModelError(f"Unsupported envelope metric for case-fraction application: {metric}")
    return rare_aetiology_cases(envelope_value, case_fraction)


def _bounded_normal(
    rng: StableRandom,
    mean: float,
    standard_deviation: float,
    lower: float | None,
    upper: float | None,
) -> float:
    if standard_deviation <= 0:
        raise ModelError("normal standard_deviation must be positive")
    if lower is not None and upper is not None and lower > upper:
        raise ModelError("normal minimum exceeds maximum")
    for _ in range(10_000):
        value = rng.normal(mean, standard_deviation)
        if (lower is None or value >= lower) and (upper is None or value <= upper):
            return value
    raise ModelError("Unable to sample bounded normal distribution after 10,000 attempts")


def _compile_distribution_sampler(
    spec: dict[str, Any],
) -> Callable[[StableRandom], float]:
    """Validate a distribution specification and return its reusable sampler."""
    distribution_type = spec.get("type")
    raw_sampler: Callable[[StableRandom], float]
    if distribution_type == "fixed":
        fixed_value = float(spec["value"])

        def fixed_sampler(_rng: StableRandom) -> float:
            return fixed_value

        raw_sampler = fixed_sampler
    elif distribution_type == "uniform":
        uniform_lower = float(spec["lower"])
        uniform_upper = float(spec["upper"])
        if uniform_lower > uniform_upper:
            raise ModelError("uniform lower must not exceed upper")

        def uniform_sampler(rng: StableRandom) -> float:
            return rng.uniform(uniform_lower, uniform_upper)

        raw_sampler = uniform_sampler
    elif distribution_type == "normal":
        mean = float(spec["mean"])
        standard_deviation = float(spec["standard_deviation"])
        normal_lower = float(spec["minimum"]) if spec.get("minimum") is not None else None
        normal_upper = float(spec["maximum"]) if spec.get("maximum") is not None else None
        if standard_deviation <= 0:
            raise ModelError("normal standard_deviation must be positive")
        if normal_lower is not None and normal_upper is not None and normal_lower > normal_upper:
            raise ModelError("normal minimum exceeds maximum")

        def normal_sampler(rng: StableRandom) -> float:
            return _bounded_normal(rng, mean, standard_deviation, normal_lower, normal_upper)

        raw_sampler = normal_sampler
    elif distribution_type == "lognormal":
        mu = float(spec["mu"])
        sigma = float(spec["sigma"])
        if sigma <= 0:
            raise ModelError("lognormal sigma must be positive")

        def lognormal_sampler(rng: StableRandom) -> float:
            return rng.lognormal(mu, sigma)

        raw_sampler = lognormal_sampler
    elif distribution_type == "beta":
        alpha = float(spec["alpha"])
        beta = float(spec["beta"])
        if alpha <= 0 or beta <= 0:
            raise ModelError("beta alpha and beta must be positive")

        def beta_sampler(rng: StableRandom) -> float:
            return rng._beta_unchecked(alpha, beta)

        raw_sampler = beta_sampler
    else:
        raise ModelError(f"Unsupported distribution type: {distribution_type!r}")

    declared_minimum = float(spec["minimum"]) if spec.get("minimum") is not None else None
    declared_maximum = float(spec["maximum"]) if spec.get("maximum") is not None else None

    def sampler(rng: StableRandom) -> float:
        value = raw_sampler(rng)
        if not math.isfinite(value):
            raise ModelError("Distribution produced a non-finite value")
        if declared_minimum is not None and value < declared_minimum:
            raise ModelError("Distribution produced a value below its declared minimum")
        if declared_maximum is not None and value > declared_maximum:
            raise ModelError("Distribution produced a value above its declared maximum")
        return value

    return sampler


def sample_distribution(spec: dict[str, Any], rng: StableRandom) -> float:
    """Sample a supported distribution specification using a supplied RNG."""
    return _compile_distribution_sampler(spec)(rng)


def _quantile(values: list[float], probability: float) -> float:
    if not 0 <= probability <= 1:
        raise ModelError("quantile probability must be between zero and one")
    if not values:
        raise ModelError("cannot compute a quantile of no values")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return ordered[lower_index]
    weight = position - lower_index
    return ordered[lower_index] * (1 - weight) + ordered[upper_index] * weight


def _standard_deviation(values: list[float], mean: float) -> float:
    if len(values) < 2:
        return 0.0
    return math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))


def simulate_product(
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    iterations: int,
    seed: int,
    interval_probability: float = 0.95,
    dependence: str = "independent",
) -> SimulationSummary:
    """Simulate a product under an explicit supported dependence assumption."""
    if iterations < 100:
        raise ModelError("iterations must be at least 100")
    if iterations > 10_000_000:
        raise ModelError("iterations must not exceed 10,000,000")
    if not 0 < interval_probability < 1:
        raise ModelError("interval_probability must be between zero and one")
    if dependence != "independent":
        raise ModelError(
            f"Unsupported dependence model {dependence!r}; "
            "only explicit independence is implemented"
        )
    rng = StableRandom(seed)
    left_sampler = _compile_distribution_sampler(left)
    right_sampler = _compile_distribution_sampler(right)
    values: list[float] = []
    for _ in range(iterations):
        left_value = left_sampler(rng)
        right_value = right_sampler(rng)
        value = left_value * right_value
        if not math.isfinite(value) or value < 0:
            raise ModelError("product simulation produced a non-finite or negative value")
        values.append(value)
    mean = fmean(values)
    tail = (1 - interval_probability) / 2
    return SimulationSummary(
        mean=mean,
        median=_quantile(values, 0.5),
        lower=_quantile(values, tail),
        upper=_quantile(values, 1 - tail),
        standard_deviation=_standard_deviation(values, mean),
        interval_probability=interval_probability,
        iterations=iterations,
        seed=seed,
    )


def _validate_analysis_units(
    estimand: str,
    left: dict[str, Any],
    right: dict[str, Any],
    output_unit: str,
) -> None:
    if right["unit"] != "proportion":
        raise ModelError(f"{estimand} requires a right-hand parameter in unit 'proportion'")
    if left["unit"] not in _PERSON_UNITS or output_unit not in _PERSON_UNITS:
        raise ModelError(f"{estimand} requires person-count input and output units")


def run_analysis_spec(
    spec: dict[str, Any],
    ledger: ParameterLedger,
    *,
    created_at: str | None = None,
    quality_disposition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a bounded, machine-readable two-parameter reference analysis.

    A supplied fitness-for-use disposition becomes an explicit scientific input.
    It must identify this analysis and permit the declared intended use.
    """
    if quality_disposition is not None:
        if quality_disposition.get("analysis_id") != spec.get("analysis_id"):
            raise ModelError("quality disposition analysis_id differs from analysis specification")
        if quality_disposition.get("intended_use") != spec.get("intended_use"):
            raise ModelError("quality disposition intended_use differs from analysis specification")
        intended_use = str(spec.get("intended_use", ""))
        if intended_use == "synthetic_assurance" and not quality_disposition.get(
            "eligible_for_synthetic_assurance"
        ):
            raise ModelError("quality disposition does not permit synthetic assurance")
        if intended_use in {"primary_estimate", "policy_decision"} and not quality_disposition.get(
            "eligible_for_primary_analysis"
        ):
            raise ModelError("quality disposition does not permit primary analysis")

    estimand = str(spec["estimand"])
    left = ledger.get(str(spec["left_parameter_id"]))
    right = ledger.get(str(spec["right_parameter_id"]))
    if estimand == "expected_affected_population":
        if left["quantity_type"] != "population" or right["quantity_type"] != "fraction":
            raise ModelError(
                "expected affected population requires population multiplied by fraction"
            )
    elif estimand == "rare_aetiology_cases":
        if left["quantity_type"] != "case_count" or right["quantity_type"] != "fraction":
            raise ModelError("rare-aetiology cases require case_count multiplied by fraction")
        apply_case_fraction(
            1.0,
            1.0,
            envelope_metric=str(left["metric"]),
            explicit_outcome_model=False,
        )
    else:
        raise ModelError(f"Unsupported estimand: {estimand}")

    output_unit = str(spec["output_unit"])
    _validate_analysis_units(estimand, left, right, output_unit)
    dependence = str(spec["dependence"])
    summary = simulate_product(
        left["distribution"],
        right["distribution"],
        iterations=int(spec["iterations"]),
        seed=int(spec["seed"]),
        interval_probability=float(spec.get("interval_probability", 0.95)),
        dependence=dependence,
    )
    core = {
        "analysis_specification": spec,
        "ledger_id": ledger.document["ledger_id"],
        "left_parameter_fingerprint": ledger.fingerprint(left["parameter_id"]),
        "right_parameter_fingerprint": ledger.fingerprint(right["parameter_id"]),
        "software_version": __version__,
        "quality_disposition_id": (
            quality_disposition.get("disposition_id") if quality_disposition is not None else None
        ),
    }
    result = {
        "schema_version": "1.0.0",
        "created_at": created_at or utc_now(),
        "analysis_result_id": content_id("ana", core),
        "analysis_id": spec["analysis_id"],
        "estimand": estimand,
        "ledger_id": ledger.document["ledger_id"],
        "left_parameter_id": left["parameter_id"],
        "left_parameter_fingerprint": core["left_parameter_fingerprint"],
        "right_parameter_id": right["parameter_id"],
        "right_parameter_fingerprint": core["right_parameter_fingerprint"],
        "output_unit": output_unit,
        "dependence": dependence,
        "dependence_rationale": spec["dependence_rationale"],
        "summary": summary.as_dict(),
        "evidence_statuses": [left["evidence_status"], right["evidence_status"]],
        "limitations": spec["limitations"],
        "runtime": {
            "software_version": __version__,
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "random_engine": StableRandom.engine_id,
        },
    }
    if quality_disposition is not None:
        result["quality_disposition_id"] = quality_disposition["disposition_id"]
    return result


__all__ = [
    "ModelError",
    "SimulationSummary",
    "apply_case_fraction",
    "expected_affected_population",
    "rare_aetiology_cases",
    "run_analysis_spec",
    "sample_distribution",
    "simulate_product",
]
