from __future__ import annotations

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rareburden.model import (
    ModelError,
    SimulationSummary,
    expected_affected_population,
    simulate_product,
)


@given(
    population=st.floats(min_value=0, max_value=1e15, allow_nan=False, allow_infinity=False),
    fraction=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
)
def test_expected_population_property_is_bounded(population: float, fraction: float) -> None:
    result = expected_affected_population(population, fraction)
    assert math.isfinite(result)
    assert 0 <= result <= population


def test_simulation_golden_vector_is_versioned() -> None:
    result = simulate_product(
        {"type": "fixed", "value": 1000},
        {"type": "beta", "alpha": 2, "beta": 8},
        iterations=100,
        seed=42,
    )
    assert result == SimulationSummary(
        mean=221.25557972503648,
        median=196.9286126384928,
        lower=26.79630925828648,
        upper=514.6377723572989,
        standard_deviation=139.81546556889302,
        interval_probability=0.95,
        iterations=100,
        seed=42,
    )


def test_seeded_beta_mean_converges_toward_analytic_expectation() -> None:
    left = {"type": "fixed", "value": 1000}
    right = {"type": "beta", "alpha": 2, "beta": 8}
    small = simulate_product(left, right, iterations=1_000, seed=42)
    large = simulate_product(left, right, iterations=10_000, seed=42)
    expected = 200.0
    assert abs(large.mean - expected) < abs(small.mean - expected)
    assert abs(large.mean - expected) / expected < 0.01


@pytest.mark.parametrize(
    "left,right",
    [
        (
            {"type": "fixed", "value": 1e308},
            {"type": "fixed", "value": 1e308},
        ),
        (
            {"type": "fixed", "value": -1},
            {"type": "fixed", "value": 1},
        ),
    ],
)
def test_simulation_rejects_overflow_and_negative_products(
    left: dict[str, float | str], right: dict[str, float | str]
) -> None:
    with pytest.raises(ModelError, match="non-finite or negative"):
        simulate_product(left, right, iterations=100, seed=1)
