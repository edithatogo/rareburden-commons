from __future__ import annotations

import pytest

from rareburden.operations import OperationalMetricError, build_metric


def test_metric_is_deterministic_and_metadata_only() -> None:
    metric = build_metric(
        "node.execution.duration",
        1.5,
        labels={"status": "passed", "runtime": "python"},
        recorded_at="2026-08-02T00:00:00Z",
    )
    assert metric == {
        "metric": "node.execution.duration",
        "value": 1.5,
        "labels": {"runtime": "python", "status": "passed"},
        "recorded_at_utc": "2026-08-02T00:00:00Z",
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": "bad name", "value": 1},
        {"name": "safe.metric", "value": float("nan")},
        {"name": "safe.metric", "value": 1, "labels": {"api_token": "x"}},
        {"name": "safe.metric", "value": 1, "labels": {"status": "participant-1"}},
    ],
)
def test_metric_rejects_invalid_or_sensitive_metadata(kwargs: dict[str, object]) -> None:
    with pytest.raises(OperationalMetricError):
        build_metric(**kwargs)  # type: ignore[arg-type]
