from __future__ import annotations

import pytest

from rareburden.operations import (
    OperationalMetricError,
    ResourceBudgetError,
    build_exercise_receipt,
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


def test_exercise_receipt_is_metadata_only_and_non_production() -> None:
    receipt = build_exercise_receipt(
        exercise_id="rollback-synthetic-01",
        release_id="v0.3.0-rc.2",
        commit="0" * 40,
        outcome="pass",
        failure_cases=["checksum_mismatch", "missing_artifact"],
        input_hashes=["a" * 64],
        output_hashes=["b" * 64],
    )
    assert receipt["production_authorized"] is False
    assert receipt["receipt_type"] == "synthetic_operations_exercise"


def test_exercise_receipt_rejects_invalid_identity_or_outcome() -> None:
    with pytest.raises(OperationalMetricError):
        build_exercise_receipt(
            exercise_id="x",
            release_id="r",
            commit="not-a-commit",
            outcome="pass",
            failure_cases=[],
            input_hashes=[],
            output_hashes=[],
        )
