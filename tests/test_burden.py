from __future__ import annotations

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rareburden.burden import (
    BurdenInputError,
    IntervalEstimate,
    expected_affected_population,
    rare_aetiology_cases,
    reject_case_fraction_health_loss_allocation,
    simulate_fraction_product,
)


@given(
    population=st.floats(min_value=0, max_value=1e10, allow_nan=False, allow_infinity=False),
    prevalence=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
)
def test_expected_population_product_is_nonnegative_and_bounded(
    population: float, prevalence: float
) -> None:
    result = expected_affected_population(
        IntervalEstimate(population, None, None, "people", "observed"),
        IntervalEstimate(prevalence, None, None, "proportion", "modelled"),
    )
    assert result.estimate >= 0
    assert math.isclose(result.estimate, population * prevalence)
    assert result.estimate <= population or math.isclose(result.estimate, population)


def test_endpoint_bounds_are_propagated() -> None:
    result = rare_aetiology_cases(
        IntervalEstimate(1000, 900, 1100, "people", "modelled"),
        IntervalEstimate(0.1, 0.05, 0.2, "proportion", "modelled"),
    )
    assert result.estimate == 100
    assert result.lower == 45
    assert result.upper == 220


def test_invalid_fraction_is_rejected() -> None:
    with pytest.raises(BurdenInputError, match="between 0 and 1"):
        expected_affected_population(
            IntervalEstimate(100, None, None, "people", "observed"),
            IntervalEstimate(1.1, None, None, "proportion", "modelled"),
        )


def test_seeded_simulation_is_reproducible_and_contains_expected_mean() -> None:
    first = simulate_fraction_product(
        envelope=1000,
        fraction_mean=0.1,
        fraction_effective_sample_size=100,
        draws=2000,
        seed=42,
    )
    second = simulate_fraction_product(
        envelope=1000,
        fraction_mean=0.1,
        fraction_effective_sample_size=100,
        draws=2000,
        seed=42,
    )
    assert first == second
    assert first.lower < first.median < first.upper
    assert 95 < first.mean < 105


def test_health_loss_allocation_fails_closed() -> None:
    with pytest.raises(BurdenInputError, match="cannot be applied directly"):
        reject_case_fraction_health_loss_allocation()
