#!/usr/bin/env python3
"""Run the bounded Track 010 synthetic reference workload benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections.abc import Callable, Sequence
from typing import Any

from rareburden.model import MAX_SIMULATION_ITERATIONS, simulate_product
from rareburden.uncertainty import decompose_independent_product


class BurdenBenchmarkError(RuntimeError):
    """Raised when the bounded reference workload fails its performance envelope."""


LEFT = {
    "type": "normal",
    "mean": 1_000_000.0,
    "standard_deviation": 10_000.0,
    "minimum": 0.0,
}
RIGHT = {
    "type": "beta",
    "alpha": 2.0,
    "beta": 98.0,
    "minimum": 0.0,
    "maximum": 1.0,
}


def run_benchmark(
    *,
    iterations: int,
    seed: int,
    max_seconds: float,
    clock: Callable[[], float] = time.process_time,
) -> dict[str, Any]:
    """Execute the CPU-only workload and return a process-time-bounded receipt."""
    if iterations < 100 or iterations > MAX_SIMULATION_ITERATIONS:
        raise BurdenBenchmarkError(
            f"iterations must be between 100 and {MAX_SIMULATION_ITERATIONS:,}"
        )
    if max_seconds <= 0:
        raise BurdenBenchmarkError("max_seconds must be positive")
    started = clock()
    simulation = simulate_product(LEFT, RIGHT, iterations=iterations, seed=seed)
    decomposition = decompose_independent_product(LEFT, RIGHT, iterations=iterations, seed=seed)
    elapsed = clock() - started
    if elapsed < 0 or elapsed > max_seconds:
        raise BurdenBenchmarkError(
            f"reference workload took {elapsed:.6f}s; limit is {max_seconds:.6f}s"
        )
    scientific_output = {
        "simulation": simulation.as_dict(),
        "decomposition": decomposition,
    }
    digest = hashlib.sha256(
        json.dumps(scientific_output, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "schema_version": "0.1.0",
        "workload": "synthetic-independent-product",
        "iterations": iterations,
        "seed": seed,
        "timing_basis": "process_cpu",
        "elapsed_seconds": elapsed,
        "maximum_seconds": max_seconds,
        "scientific_output_sha256": digest,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260731)
    parser.add_argument("--max-seconds", type=float, default=15.0)
    args = parser.parse_args(argv)
    try:
        receipt = run_benchmark(
            iterations=args.iterations,
            seed=args.seed,
            max_seconds=args.max_seconds,
        )
    except BurdenBenchmarkError as exc:
        parser.error(str(exc))
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
