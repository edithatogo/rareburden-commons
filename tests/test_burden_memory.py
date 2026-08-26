from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_script() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts/check_burden_memory.py"
    spec = importlib.util.spec_from_file_location("check_burden_memory", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MEMORY = _load_script()


def test_small_workload_records_a_bounded_peak() -> None:
    receipt = MEMORY.measure_peak(iterations=100, seed=7, max_peak_bytes=4 * 1024 * 1024)
    assert receipt["measurement"] == "python_tracemalloc_peak"
    assert 0 < receipt["peak_bytes"] <= receipt["maximum_peak_bytes"]


def test_memory_gate_rejects_invalid_or_exceeded_bounds() -> None:
    with pytest.raises(MEMORY.BurdenMemoryError, match="iterations"):
        MEMORY.measure_peak(iterations=99, seed=7, max_peak_bytes=1024)
    with pytest.raises(MEMORY.BurdenMemoryError, match="limit is"):
        MEMORY.measure_peak(iterations=100, seed=7, max_peak_bytes=1)
