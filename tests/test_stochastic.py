from __future__ import annotations

import math

import pytest

from rareburden.stochastic import RandomStreamError, StableRandom


def test_pcg32_golden_vector_is_versioned() -> None:
    stream = StableRandom(42)
    assert stream.engine_id == "rareburden.pcg32-box-muller-marsaglia-tsang.v1"
    assert [stream.uint32() for _ in range(8)] == [
        492690617,
        1919685028,
        3561993920,
        683038915,
        1183706632,
        413921556,
        222559498,
        436142503,
    ]


def test_distribution_streams_are_reproducible() -> None:
    first = StableRandom(20260719)
    second = StableRandom(20260719)
    first_values = [
        first.uniform(-1, 1),
        first.normal(10, 2),
        first.lognormal(0, 0.5),
        first.beta(2, 5),
    ]
    second_values = [
        second.uniform(-1, 1),
        second.normal(10, 2),
        second.lognormal(0, 0.5),
        second.beta(2, 5),
    ]
    assert first_values == second_values
    assert all(math.isfinite(value) for value in first_values)
    assert 0 <= first_values[-1] <= 1


def test_beta_sampler_has_plausible_seeded_mean() -> None:
    stream = StableRandom(7)
    values = [stream.beta(2, 8) for _ in range(20_000)]
    assert sum(values) / len(values) == pytest.approx(0.2, abs=0.01)


@pytest.mark.parametrize(
    ("method", "arguments", "message"),
    [
        ("uniform", (2.0, 1.0), "lower"),
        ("normal", (0.0, 0.0), "positive"),
        ("lognormal", (0.0, -1.0), "positive"),
        ("gamma", (0.0,), "positive"),
        ("beta", (-1.0, 2.0), "alpha"),
    ],
)
def test_invalid_distribution_parameters_fail_closed(
    method: str, arguments: tuple[float, ...], message: str
) -> None:
    stream = StableRandom(1)
    with pytest.raises(RandomStreamError, match=message):
        getattr(stream, method)(*arguments)
