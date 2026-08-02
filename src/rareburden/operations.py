"""Privacy-safe, metadata-only operational metrics primitives."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any


class OperationalMetricError(ValueError):
    """Raised when a metric would contain unsafe or invalid metadata."""


class ResourceBudgetError(ValueError):
    """Raised when an operational measurement violates the declared budget."""


_NAME = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")
_SENSITIVE = re.compile(
    r"(?:token|secret|password|credential|api[_-]?key|authorization|person|participant|subject|email|phone|address|name|identifier)",
    re.IGNORECASE,
)


def build_metric(
    name: str,
    value: int | float,
    *,
    labels: Mapping[str, str] | None = None,
    recorded_at: str | None = None,
) -> dict[str, Any]:
    """Build a privacy-safe metric record without retaining event payloads."""
    if not isinstance(name, str) or not _NAME.fullmatch(name):
        raise OperationalMetricError("metric name must be a lowercase dotted identifier")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise OperationalMetricError("metric value must be a finite number")
    safe_labels: dict[str, str] = {}
    for key, label in (labels or {}).items():
        if not isinstance(key, str) or _SENSITIVE.search(key):
            raise OperationalMetricError("metric labels must not contain sensitive fields")
        if not isinstance(label, str) or len(label) > 128 or _SENSITIVE.search(label):
            raise OperationalMetricError("metric label values must be short and non-sensitive")
        safe_labels[key] = label
    timestamp = recorded_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
        raise OperationalMetricError("recorded_at must be an explicit UTC timestamp")
    return {
        "metric": name,
        "value": value,
        "labels": dict(sorted(safe_labels.items())),
        "recorded_at_utc": timestamp,
    }


def build_resource_budget(
    *,
    package_size_bytes: int,
    install_disk_bytes: int,
    peak_rss_bytes: int,
    cpu_seconds: float,
    workload_seconds: float,
) -> dict[str, Any]:
    """Return a versioned, explicit resource budget for synthetic exercises."""
    values = {
        "package_size_bytes": package_size_bytes,
        "install_disk_bytes": install_disk_bytes,
        "peak_rss_bytes": peak_rss_bytes,
        "cpu_seconds": cpu_seconds,
        "workload_seconds": workload_seconds,
    }
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float)) for value in values.values()
    ):
        raise ResourceBudgetError("resource budgets must be numeric")
    if any(value <= 0 or not math.isfinite(float(value)) for value in values.values()):
        raise ResourceBudgetError("resource budgets must be finite and positive")
    return {"schema_version": "0.1.0", "budget_type": "synthetic_operations", **values}


def check_resource_budget(budget: Mapping[str, Any], measurement: Mapping[str, Any]) -> None:
    """Fail closed when a measured value exceeds its corresponding budget."""
    required = (
        "package_size_bytes",
        "install_disk_bytes",
        "peak_rss_bytes",
        "cpu_seconds",
        "workload_seconds",
    )
    if (
        budget.get("schema_version") != "0.1.0"
        or budget.get("budget_type") != "synthetic_operations"
    ):
        raise ResourceBudgetError("unsupported resource budget schema")
    for key in required:
        limit = budget.get(key)
        observed = measurement.get(key)
        if (
            isinstance(limit, bool)
            or not isinstance(limit, (int, float))
            or not math.isfinite(float(limit))
        ):
            raise ResourceBudgetError(f"invalid budget for {key}")
        if (
            isinstance(observed, bool)
            or not isinstance(observed, (int, float))
            or not math.isfinite(float(observed))
        ):
            raise ResourceBudgetError(f"missing or invalid measurement for {key}")
        if observed > limit:
            raise ResourceBudgetError(f"resource budget exceeded for {key}")


__all__ = [
    "OperationalMetricError",
    "ResourceBudgetError",
    "build_metric",
    "build_resource_budget",
    "check_resource_budget",
]
