"""Disclosure-safe primitives for offline federated-node fixtures."""

from __future__ import annotations

import platform
import sys
from collections.abc import Mapping, Sequence
from typing import Any


class NodeExportError(ValueError):
    """Raised when a node export violates its disclosure contract."""


def validate_version_compatibility(
    *, coordinator_version: str, node_version: str, supported_major: int = 0
) -> None:
    """Reject malformed or incompatible coordinator/node major versions."""
    try:
        coordinator_major = int(coordinator_version.split(".", 1)[0])
        node_major = int(node_version.split(".", 1)[0])
    except (AttributeError, ValueError):
        raise NodeExportError("coordinator and node versions must be semantic versions") from None
    if coordinator_major != supported_major or node_major != supported_major:
        raise NodeExportError("coordinator and node major versions are incompatible")


def build_execution_manifest(
    *,
    execution_id: str,
    coordinator_version: str,
    node_version: str,
    analysis_id: str,
    policy_id: str,
    input_fingerprint: str,
    status: str = "prepared",
) -> dict[str, Any]:
    """Build a minimal deterministic execution manifest without sensitive values."""
    if not all(
        value.strip() for value in (execution_id, analysis_id, policy_id, input_fingerprint)
    ):
        raise NodeExportError("execution, analysis, policy and input identifiers must be non-empty")
    validate_version_compatibility(
        coordinator_version=coordinator_version, node_version=node_version
    )
    if status not in {"prepared", "completed", "failed", "withdrawn"}:
        raise NodeExportError(f"unsupported execution status: {status}")
    return {
        "schema_version": "0.1.0",
        "execution_id": execution_id,
        "coordinator_version": coordinator_version,
        "node_version": node_version,
        "analysis_id": analysis_id,
        "policy_id": policy_id,
        "status": status,
        "input_fingerprint": input_fingerprint,
        "limitations": ["Synthetic/offline manifest; no participant-level data."],
    }


def capture_environment(*, lockfile_fingerprint: str) -> dict[str, str]:
    """Capture bounded runtime identity for a node preflight manifest."""
    if not lockfile_fingerprint.strip():
        raise NodeExportError("lockfile_fingerprint must be non-empty")
    return {
        "python_version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "system": platform.system(),
        "machine": platform.machine(),
        "lockfile_fingerprint": lockfile_fingerprint,
        "runtime": sys.implementation.name,
    }


def run_offline_node(
    rows: Sequence[Mapping[str, Any]],
    *,
    execution_id: str,
    coordinator_version: str,
    node_version: str,
    analysis_id: str,
    policy_id: str,
    input_fingerprint: str,
    minimum_cell_count: int = 5,
) -> dict[str, Any]:
    """Execute the synthetic node boundary without persistence or network access."""
    manifest = build_execution_manifest(
        execution_id=execution_id,
        coordinator_version=coordinator_version,
        node_version=node_version,
        analysis_id=analysis_id,
        policy_id=policy_id,
        input_fingerprint=input_fingerprint,
        status="completed",
    )
    return {
        "manifest": manifest,
        "rows": validate_aggregate_export(rows, minimum_cell_count=minimum_cell_count),
    }


def build_synthetic_cohort() -> list[dict[str, Any]]:
    """Return a deterministic aggregate-only cohort fixture with edge cases."""
    return [
        {"diagnosis": "condition-a", "count": 8},
        {"diagnosis": "condition-b", "count": 5},
        {"diagnosis": "condition-a+condition-b", "count": 2},
    ]


_PARTICIPANT_FIELDS = {
    "person_id",
    "participant_id",
    "record_id",
    "admission_id",
    "date_of_birth",
}


def validate_aggregate_export(
    rows: Sequence[Mapping[str, Any]], *, count_field: str = "count", minimum_cell_count: int = 5
) -> list[dict[str, Any]]:
    """Return disclosure-safe aggregate rows, suppressing cells below threshold."""
    if minimum_cell_count < 1:
        raise NodeExportError("minimum_cell_count must be positive")
    exported: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        keys = {str(key) for key in row}
        leaked = sorted(keys & _PARTICIPANT_FIELDS)
        if leaked:
            raise NodeExportError(
                f"row {index} contains participant-level fields: {', '.join(leaked)}"
            )
        if count_field not in row:
            raise NodeExportError(f"row {index} lacks count field {count_field!r}")
        count = row[count_field]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise NodeExportError(f"row {index} count must be a non-negative integer")
        safe = {str(key): value for key, value in row.items() if str(key) != count_field}
        safe["count_status"] = "suppressed" if count < minimum_cell_count else "released"
        safe[count_field] = None if count < minimum_cell_count else count
        exported.append(safe)
    return exported


__all__ = [
    "NodeExportError",
    "build_execution_manifest",
    "build_synthetic_cohort",
    "capture_environment",
    "run_offline_node",
    "validate_aggregate_export",
    "validate_version_compatibility",
]
