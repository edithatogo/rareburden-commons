"""Small, auditable building blocks for aggregate rare-disease burden estimates."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from statistics import fmean


class BurdenInputError(ValueError):
    """Raised when an estimand or input violates a scientific contract."""


@dataclass(frozen=True)
class IntervalEstimate:
    """A non-negative estimate with optional uncertainty and explicit units."""

    estimate: float
    lower: float | None
    upper: float | None
    unit: str
    evidence_status: str

    def __post_init__(self) -> None:
        if not math.isfinite(self.estimate) or self.estimate < 0:
            raise BurdenInputError("estimate must be finite and non-negative")
        if not self.unit.strip():
            raise BurdenInputError("unit must not be empty")
        if self.lower is None and self.upper is not None:
            raise BurdenInputError("lower and upper must be supplied together")
        if self.upper is None and self.lower is not None:
            raise BurdenInputError("lower and upper must be supplied together")
        if self.lower is not None and self.upper is not None:
            if not all(math.isfinite(value) and value >= 0 for value in (self.lower, self.upper)):
                raise BurdenInputError("uncertainty bounds must be finite and non-negative")
            if not self.lower <= self.estimate <= self.upper:
                raise BurdenInputError("uncertainty bounds must contain the estimate")


@dataclass(frozen=True)
class SimulationSummary:
    """Summary of a seeded Monte Carlo product distribution."""

    mean: float
    median: float
    lower: float
    upper: float
    draws: int
    seed: int
    unit: str


def expected_affected_population(
    population: IntervalEstimate,
    prevalence: IntervalEstimate,
) -> IntervalEstimate:
    """Estimate affected people as population multiplied by prevalence.

    Bounds are a conservative endpoint product, not a replacement for joint simulation.
    The function rejects ambiguous units and fractions outside [0, 1].
    """
    if population.unit != "people":
        raise BurdenInputError("population must use unit 'people'")
    if prevalence.unit != "proportion":
        raise BurdenInputError("prevalence must use unit 'proportion'")
    _require_fraction(prevalence)
    lower, upper = _product_bounds(population, prevalence)
    return IntervalEstimate(
        estimate=population.estimate * prevalence.estimate,
        lower=lower,
        upper=upper,
        unit="people",
        evidence_status="derived",
    )


def rare_aetiology_cases(
    envelope_cases: IntervalEstimate,
    aetiology_fraction: IntervalEstimate,
) -> IntervalEstimate:
    """Estimate cases with a defined rare aetiology inside a compatible case envelope."""
    if envelope_cases.unit != "people":
        raise BurdenInputError("case envelope must use unit 'people'")
    if aetiology_fraction.unit != "proportion":
        raise BurdenInputError("aetiology fraction must use unit 'proportion'")
    _require_fraction(aetiology_fraction)
    lower, upper = _product_bounds(envelope_cases, aetiology_fraction)
    return IntervalEstimate(
        estimate=envelope_cases.estimate * aetiology_fraction.estimate,
        lower=lower,
        upper=upper,
        unit="people",
        evidence_status="derived",
    )


def simulate_fraction_product(
    *,
    envelope: float,
    fraction_mean: float,
    fraction_effective_sample_size: float,
    draws: int = 10_000,
    seed: int = 20260719,
    unit: str = "people",
) -> SimulationSummary:
    """Propagate beta-distributed fraction uncertainty through an exact envelope.

    ``fraction_effective_sample_size`` is a modelling input, not necessarily the raw
    participant count. Its interpretation must be recorded in the parameter ledger.
    """
    if not math.isfinite(envelope) or envelope < 0:
        raise BurdenInputError("envelope must be finite and non-negative")
    if not 0 < fraction_mean < 1:
        raise BurdenInputError("fraction_mean must be strictly between 0 and 1")
    if not math.isfinite(fraction_effective_sample_size) or fraction_effective_sample_size <= 2:
        raise BurdenInputError("fraction_effective_sample_size must be greater than 2")
    if draws < 100 or draws > 10_000_000:
        raise BurdenInputError("draws must be between 100 and 10,000,000")
    if not unit.strip():
        raise BurdenInputError("unit must not be empty")

    alpha = fraction_mean * fraction_effective_sample_size
    beta = (1.0 - fraction_mean) * fraction_effective_sample_size
    generator = random.Random(seed)
    samples = sorted(envelope * generator.betavariate(alpha, beta) for _ in range(draws))
    return SimulationSummary(
        mean=fmean(samples),
        median=_quantile(samples, 0.5),
        lower=_quantile(samples, 0.025),
        upper=_quantile(samples, 0.975),
        draws=draws,
        seed=seed,
        unit=unit,
    )


def reject_case_fraction_health_loss_allocation() -> None:
    """Fail closed when code attempts to allocate DALYs by an unvalidated case fraction."""
    raise BurdenInputError(
        "A case fraction cannot be applied directly to DALY, YLD, YLL or cost envelopes. "
        "Model onset, severity, treatment, survival and component-specific costs explicitly."
    )


def _require_fraction(value: IntervalEstimate) -> None:
    points = [value.estimate]
    if value.lower is not None and value.upper is not None:
        points.extend((value.lower, value.upper))
    if any(point < 0 or point > 1 for point in points):
        raise BurdenInputError("proportions and their bounds must be between 0 and 1")


def _product_bounds(
    left: IntervalEstimate,
    right: IntervalEstimate,
) -> tuple[float | None, float | None]:
    if left.lower is None or left.upper is None or right.lower is None or right.upper is None:
        return None, None
    return left.lower * right.lower, left.upper * right.upper


def _quantile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        raise BurdenInputError("cannot calculate a quantile from no values")
    if not 0 <= probability <= 1:
        raise BurdenInputError("probability must be between 0 and 1")
    position = (len(sorted_values) - 1) * probability
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return sorted_values[lower_index]
    weight = position - lower_index
    return sorted_values[lower_index] * (1.0 - weight) + sorted_values[upper_index] * weight
