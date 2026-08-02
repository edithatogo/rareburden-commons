from __future__ import annotations

import pytest

from rareburden.operations import (
    ResourceBudgetError,
    build_resource_budget,
    check_resource_budget,
)


def _budget() -> dict[str, object]:
    return build_resource_budget(
        package_size_bytes=10_000,
        install_disk_bytes=25_000,
        peak_rss_bytes=50_000,
        cpu_seconds=2.0,
        workload_seconds=5.0,
    )


def test_resource_budget_accepts_measurement_at_limit() -> None:
    budget = _budget()
    check_resource_budget(budget, budget)


def test_resource_budget_rejects_overage() -> None:
    budget = _budget()
    measurement = dict(budget)
    measurement["peak_rss_bytes"] = 50_001
    with pytest.raises(ResourceBudgetError, match="peak_rss_bytes"):
        check_resource_budget(budget, measurement)


@pytest.mark.parametrize("kwargs", [{"cpu_seconds": 0}, {"workload_seconds": float("inf")}])
def test_resource_budget_rejects_non_positive_or_non_finite(kwargs: dict[str, object]) -> None:
    values = {
        "package_size_bytes": 10_000,
        "install_disk_bytes": 25_000,
        "peak_rss_bytes": 50_000,
        "cpu_seconds": 2.0,
        "workload_seconds": 5.0,
    }
    values.update(kwargs)
    with pytest.raises(ResourceBudgetError):
        build_resource_budget(**values)
