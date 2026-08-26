#!/usr/bin/env python3
"""Measure the bounded Track 010 workload's Python allocation peak."""

from __future__ import annotations

import argparse
import json
import tracemalloc
from collections.abc import Sequence
from typing import Any

from rareburden.model import MAX_SIMULATION_ITERATIONS, simulate_product
from rareburden.uncertainty import decompose_independent_product

try:
    from scripts.check_burden_benchmark import LEFT, RIGHT
except ModuleNotFoundError:  # Direct execution places scripts/ on sys.path.
    from check_burden_benchmark import LEFT, RIGHT  # type: ignore[no-redef]


class BurdenMemoryError(RuntimeError):
    """Raised when the bounded workload exceeds its allocation envelope."""


def measure_peak(*, iterations: int, seed: int, max_peak_bytes: int) -> dict[str, Any]:
    """Run simulation and decomposition under a fail-closed allocation ceiling."""
    if iterations < 100 or iterations > MAX_SIMULATION_ITERATIONS:
        raise BurdenMemoryError(f"iterations must be between 100 and {MAX_SIMULATION_ITERATIONS:,}")
    if max_peak_bytes <= 0:
        raise BurdenMemoryError("max_peak_bytes must be positive")
    tracemalloc.start()
    try:
        simulate_product(LEFT, RIGHT, iterations=iterations, seed=seed)
        decompose_independent_product(LEFT, RIGHT, iterations=iterations, seed=seed)
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    if peak > max_peak_bytes:
        raise BurdenMemoryError(
            f"reference workload peak was {peak} bytes; limit is {max_peak_bytes} bytes"
        )
    return {
        "schema_version": "0.1.0",
        "workload": "synthetic-independent-product",
        "iterations": iterations,
        "seed": seed,
        "measurement": "python_tracemalloc_peak",
        "peak_bytes": peak,
        "maximum_peak_bytes": max_peak_bytes,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=MAX_SIMULATION_ITERATIONS)
    parser.add_argument("--seed", type=int, default=20260731)
    parser.add_argument("--max-peak-bytes", type=int, default=64 * 1024 * 1024)
    args = parser.parse_args(argv)
    try:
        receipt = measure_peak(
            iterations=args.iterations,
            seed=args.seed,
            max_peak_bytes=args.max_peak_bytes,
        )
    except BurdenMemoryError as exc:
        parser.error(str(exc))
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
