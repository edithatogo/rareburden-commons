from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_script() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts/check_burden_benchmark.py"
    spec = importlib.util.spec_from_file_location("check_burden_benchmark", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BENCHMARK = _load_script()


def test_benchmark_receipt_is_scientifically_reproducible() -> None:
    first = BENCHMARK.run_benchmark(
        iterations=100,
        seed=7,
        max_seconds=10,
        clock=iter([1.0, 1.5]).__next__,
    )
    second = BENCHMARK.run_benchmark(
        iterations=100,
        seed=7,
        max_seconds=10,
        clock=iter([5.0, 5.5]).__next__,
    )
    assert first == second
    assert first["timing_basis"] == "process_cpu"
    assert (
        first["scientific_output_sha256"]
        == "5783be615ac183170e896abf255d77961d965caa40ed13d744bb0d2bef575730"
    )
    assert first["elapsed_seconds"] == 0.5


def test_representative_large_synthetic_workload_stays_bounded() -> None:
    receipt = BENCHMARK.run_benchmark(iterations=100_000, seed=20260731, max_seconds=15)
    assert receipt["iterations"] == 100_000
    assert receipt["timing_basis"] == "process_cpu"
    assert receipt["elapsed_seconds"] <= receipt["maximum_seconds"]
    assert receipt["scientific_output_sha256"]


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"iterations": 99, "seed": 1, "max_seconds": 1}, "iterations"),
        ({"iterations": 100, "seed": 1, "max_seconds": 0}, "positive"),
        ({"iterations": 100, "seed": 1, "max_seconds": 1}, "limit"),
    ],
)
def test_benchmark_fails_closed(kwargs: dict[str, int], message: str) -> None:
    clock = iter([0.0, 2.0]).__next__
    with pytest.raises(BENCHMARK.BurdenBenchmarkError, match=message):
        BENCHMARK.run_benchmark(**kwargs, clock=clock)
