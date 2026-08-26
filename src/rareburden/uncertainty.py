"""Transparent uncertainty decomposition for independent multiplicative models."""

from __future__ import annotations

import math
from statistics import fmean
from typing import Any

from rareburden.model import MAX_SIMULATION_ITERATIONS, ModelError, _compile_distribution_sampler
from rareburden.stochastic import StableRandom


def _sample_variance(values: list[float], mean: float) -> float:
    if len(values) < 2:
        return 0.0
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def decompose_independent_product(
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    """Decompose product variance into left, right and interaction components.

    For independent ``X`` and ``Y``::

        Var(XY) = Var(X) E[Y]^2 + Var(Y) E[X]^2 + Var(X) Var(Y)

    The components are calculated from deterministic Monte Carlo moments using the
    project's versioned random stream.  Empirical paired-product variance is reported
    separately so finite-sample closure can be audited rather than silently hidden.
    """
    if iterations < 100 or iterations > MAX_SIMULATION_ITERATIONS:
        raise ModelError(f"iterations must be between 100 and {MAX_SIMULATION_ITERATIONS:,}")
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ModelError("seed must be a non-negative integer")
    rng = StableRandom(seed)
    left_sampler = _compile_distribution_sampler(left)
    right_sampler = _compile_distribution_sampler(right)
    left_draws: list[float] = []
    right_draws: list[float] = []
    products: list[float] = []
    for _ in range(iterations):
        left_value = left_sampler(rng)
        right_value = right_sampler(rng)
        left_draws.append(left_value)
        right_draws.append(right_value)
        products.append(left_value * right_value)

    left_mean = fmean(left_draws)
    right_mean = fmean(right_draws)
    product_mean = fmean(products)
    left_variance = _sample_variance(left_draws, left_mean)
    right_variance = _sample_variance(right_draws, right_mean)
    empirical_variance = _sample_variance(products, product_mean)
    left_component = left_variance * right_mean**2
    right_component = right_variance * left_mean**2
    interaction = left_variance * right_variance
    moment_total = left_component + right_component + interaction

    if not all(
        math.isfinite(value) and value >= 0
        for value in (
            left_component,
            right_component,
            interaction,
            moment_total,
            empirical_variance,
        )
    ):
        raise ModelError("uncertainty decomposition produced invalid variance")
    denominator = moment_total if moment_total > 0 else 1.0
    closure_denominator = max(moment_total, empirical_variance, 1e-300)
    return {
        "schema_version": "1.0.0",
        "method": "independent-product-moment-decomposition",
        "assumption": "independent",
        "iterations": iterations,
        "seed": seed,
        "left_parameter": {
            "variance": left_component,
            "fraction_of_moment_variance": left_component / denominator,
        },
        "right_parameter": {
            "variance": right_component,
            "fraction_of_moment_variance": right_component / denominator,
        },
        "interaction": {
            "variance": interaction,
            "fraction_of_moment_variance": interaction / denominator,
        },
        "moment_derived_total_variance": moment_total,
        "empirical_product_variance": empirical_variance,
        "relative_closure_error": abs(moment_total - empirical_variance) / closure_denominator,
        "limitations": [
            "The decomposition assumes independent inputs and is invalid for "
            "correlated parameters.",
            "Components use finite deterministic Monte Carlo moments rather than "
            "analytic distribution moments.",
            "The interaction term reflects multiplicative uncertainty, not biological interaction.",
        ],
    }


__all__ = ["decompose_independent_product"]
