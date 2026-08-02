"""Privacy-safe, metadata-only operational metrics primitives."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any


class OperationalMetricError(ValueError):
    """Raised when a metric would contain unsafe or invalid metadata."""


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


__all__ = ["OperationalMetricError", "build_metric"]
