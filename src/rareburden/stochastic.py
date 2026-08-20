"""Versioned deterministic pseudo-random primitives for scientific simulations.

The implementation intentionally avoids the standard-library distribution helpers.  Their
algorithms are not part of RareBurden's release contract and could change independently of
this package.  PCG32 supplies the uniform bit stream; Box--Muller and Marsaglia--Tsang supply
normal and gamma variates.  Golden-vector tests make any future stream change explicit.
"""

from __future__ import annotations

import math


class RandomStreamError(ValueError):
    """Raised when a random-stream request has invalid parameters."""


_UINT32_MASK = (1 << 32) - 1
_UINT64_MASK = (1 << 64) - 1
_PCG32_MULTIPLIER = 6364136223846793005
_DEFAULT_STREAM = 1442695040888963407
_TWO_POW_53 = float(1 << 53)


class StableRandom:
    """RareBurden deterministic random stream, version 1.

    The integer generator is PCG-XSH-RR 64/32.  The public stream identifier is recorded in
    every analysis result so that future algorithms can coexist without silent drift.
    """

    engine_id = "rareburden.pcg32-box-muller-marsaglia-tsang.v1"

    def __init__(self, seed: int, *, stream: int = _DEFAULT_STREAM) -> None:
        if not 0 <= seed <= _UINT64_MASK:
            raise RandomStreamError("seed must be an unsigned 64-bit integer")
        if not 0 <= stream <= _UINT64_MASK:
            raise RandomStreamError("stream must be an unsigned 64-bit integer")
        self._state = 0
        self._increment = ((stream << 1) | 1) & _UINT64_MASK
        self._next_uint32()
        self._state = (self._state + seed) & _UINT64_MASK
        self._next_uint32()

    def _next_uint32(self) -> int:
        old_state = self._state
        self._state = (old_state * _PCG32_MULTIPLIER + self._increment) & _UINT64_MASK
        xorshifted = (((old_state >> 18) ^ old_state) >> 27) & _UINT32_MASK
        rotation = (old_state >> 59) & 31
        return ((xorshifted >> rotation) | (xorshifted << ((-rotation) & 31))) & _UINT32_MASK

    def uint32(self) -> int:
        """Return the next unsigned 32-bit integer in the versioned stream."""
        return self._next_uint32()

    def random(self) -> float:
        """Return a 53-bit uniform variate in the half-open interval [0, 1)."""
        high = self._next_uint32() >> 5
        low = self._next_uint32() >> 6
        return (high * (1 << 26) + low) / _TWO_POW_53

    def _positive_random(self) -> float:
        value = self.random()
        while value <= 0.0:
            value = self.random()
        return value

    def uniform(self, lower: float, upper: float) -> float:
        """Return a uniform variate on [lower, upper)."""
        if not math.isfinite(lower) or not math.isfinite(upper):
            raise RandomStreamError("uniform bounds must be finite")
        if lower > upper:
            raise RandomStreamError("uniform lower must not exceed upper")
        if lower == upper:
            return lower
        return lower + (upper - lower) * self.random()

    def normal(self, mean: float = 0.0, standard_deviation: float = 1.0) -> float:
        """Return a normal variate using the polar Box--Muller transform."""
        if not math.isfinite(mean):
            raise RandomStreamError("normal mean must be finite")
        if not math.isfinite(standard_deviation) or standard_deviation <= 0:
            raise RandomStreamError("normal standard_deviation must be finite and positive")
        return self._normal_unchecked(mean, standard_deviation)

    def _normal_unchecked(self, mean: float, standard_deviation: float) -> float:
        """Draw from a normal distribution whose parameters were already validated."""
        while True:
            first = 2.0 * self.random() - 1.0
            second = 2.0 * self.random() - 1.0
            radius_squared = first * first + second * second
            if 0.0 < radius_squared < 1.0:
                multiplier = math.sqrt(-2.0 * math.log(radius_squared) / radius_squared)
                return mean + standard_deviation * first * multiplier

    def lognormal(self, mu: float, sigma: float) -> float:
        """Return a log-normal variate parameterised on the log scale."""
        if not math.isfinite(mu):
            raise RandomStreamError("lognormal mu must be finite")
        if not math.isfinite(sigma) or sigma <= 0:
            raise RandomStreamError("lognormal sigma must be finite and positive")
        return math.exp(mu + sigma * self.normal())

    def gamma(self, shape: float) -> float:
        """Return a unit-scale gamma variate using Marsaglia--Tsang sampling."""
        if not math.isfinite(shape) or shape <= 0:
            raise RandomStreamError("gamma shape must be finite and positive")
        if shape < 1.0:
            # Gamma(a) = Gamma(a+1) * U**(1/a) for 0 < a < 1.
            return self.gamma(shape + 1.0) * math.pow(self._positive_random(), 1.0 / shape)

        adjusted = shape - 1.0 / 3.0
        coefficient = 1.0 / math.sqrt(9.0 * adjusted)
        for _ in range(1_000_000):
            normal = self.normal()
            candidate_root = 1.0 + coefficient * normal
            if candidate_root <= 0:
                continue
            candidate = candidate_root**3
            uniform = self._positive_random()
            if uniform < 1.0 - 0.0331 * normal**4:
                return adjusted * candidate
            if math.log(uniform) < 0.5 * normal**2 + adjusted * (
                1.0 - candidate + math.log(candidate)
            ):
                return adjusted * candidate
        raise RandomStreamError("gamma sampler exceeded its defensive iteration limit")

    def _gamma_unchecked(self, shape: float) -> float:
        """Draw from a gamma distribution whose shape was already validated."""
        if shape < 1.0:
            # Gamma(a) = Gamma(a+1) * U**(1/a) for 0 < a < 1.
            return self._gamma_unchecked(shape + 1.0) * math.pow(
                self._positive_random(), 1.0 / shape
            )

        adjusted = shape - 1.0 / 3.0
        coefficient = 1.0 / math.sqrt(9.0 * adjusted)
        for _ in range(1_000_000):
            normal = self._normal_unchecked(0.0, 1.0)
            candidate_root = 1.0 + coefficient * normal
            if candidate_root <= 0:
                continue
            candidate = candidate_root**3
            uniform = self._positive_random()
            if uniform < 1.0 - 0.0331 * normal**4:
                return adjusted * candidate
            if math.log(uniform) < 0.5 * normal**2 + adjusted * (
                1.0 - candidate + math.log(candidate)
            ):
                return adjusted * candidate
        raise RandomStreamError("gamma sampler exceeded its defensive iteration limit")

    def beta(self, alpha: float, beta: float) -> float:
        """Return a beta variate from independent gamma draws."""
        if not math.isfinite(alpha) or alpha <= 0:
            raise RandomStreamError("beta alpha must be finite and positive")
        if not math.isfinite(beta) or beta <= 0:
            raise RandomStreamError("beta beta must be finite and positive")
        first = self.gamma(alpha)
        second = self.gamma(beta)
        total = first + second
        if not math.isfinite(total) or total <= 0:
            raise RandomStreamError("beta sampler produced an invalid denominator")
        return first / total

    def _beta_unchecked(self, alpha: float, beta: float) -> float:
        """Draw from a beta distribution whose parameters were already validated."""
        first = self._gamma_unchecked(alpha)
        second = self._gamma_unchecked(beta)
        total = first + second
        if not math.isfinite(total) or total <= 0:
            raise RandomStreamError("beta sampler produced an invalid denominator")
        return first / total


__all__ = ["RandomStreamError", "StableRandom"]
