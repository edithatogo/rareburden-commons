"""Disclosure-safe primitives for offline federated-node fixtures."""

from __future__ import annotations

import hashlib
import json
import platform
import re
import sys
from collections.abc import Mapping, Sequence
from typing import Any


class NodeExportError(ValueError):
    """Raised when a node export violates its disclosure contract."""


_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_FINGERPRINT = re.compile(r"^sha256:[0-9a-f]{64}$")


def validate_version_compatibility(
    *, coordinator_version: str, node_version: str, supported_major: int = 0
) -> None:
    """Reject malformed or incompatible coordinator/node major versions."""
    coordinator_match = _SEMVER.fullmatch(coordinator_version)
    node_match = _SEMVER.fullmatch(node_version)
    if coordinator_match is None or node_match is None:
        raise NodeExportError("coordinator and node versions must be semantic versions")
    coordinator_major = int(coordinator_match.group(1))
    node_major = int(node_match.group(1))
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
    output_fingerprint: str | None = None,
    status: str = "prepared",
) -> dict[str, Any]:
    """Build a minimal deterministic execution manifest without sensitive values."""
    if not all(
        value.strip() for value in (execution_id, analysis_id, policy_id, input_fingerprint)
    ):
        raise NodeExportError("execution, analysis, policy and input identifiers must be non-empty")
    if _FINGERPRINT.fullmatch(input_fingerprint) is None:
        raise NodeExportError("input fingerprint must be a sha256 digest")
    if status == "completed" and (
        output_fingerprint is None or _FINGERPRINT.fullmatch(output_fingerprint) is None
    ):
        raise NodeExportError("completed manifest requires a sha256 output fingerprint")
    validate_version_compatibility(
        coordinator_version=coordinator_version, node_version=node_version
    )
    if status not in {"prepared", "completed", "failed", "withdrawn"}:
        raise NodeExportError(f"unsupported execution status: {status}")
    manifest: dict[str, Any] = {
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
    if output_fingerprint is not None:
        manifest["output_fingerprint"] = output_fingerprint
    return manifest


def amend_execution_manifest(
    manifest: Mapping[str, Any], *, correction_reason: str, replacement_execution_id: str
) -> dict[str, Any]:
    """Create an immutable correction record without rewriting the source manifest."""
    if not correction_reason.strip() or not replacement_execution_id.strip():
        raise NodeExportError("correction reason and replacement execution ID must be non-empty")
    required = {"execution_id", "schema_version", "analysis_id", "policy_id"}
    if not required.issubset(manifest):
        raise NodeExportError("manifest lacks correction provenance fields")
    if replacement_execution_id == manifest["execution_id"]:
        raise NodeExportError("replacement execution ID must differ from the source")
    if manifest.get("status") == "withdrawn" or "supersedes_execution_id" in manifest:
        raise NodeExportError("withdrawn or superseding manifests cannot be corrected")
    amended = dict(manifest)
    amended.pop("output_fingerprint", None)
    amended["supersedes_execution_id"] = str(manifest["execution_id"])
    amended["execution_id"] = replacement_execution_id
    amended["correction_reason"] = correction_reason
    amended["status"] = "prepared"
    return amended


_SENSITIVE_LOG_TERMS = (
    "token",
    "password",
    "secret",
    "authorization",
    "credential",
    "cookie",
    "session",
    "api_key",
    "person_id",
    "participant_id",
    "email",
)
_SENSITIVE_LOG_VALUE = re.compile(
    r"(?i)(bearer\s+\S+|authorization\s*[:=]\s*\S+|api[_-]?key\s*[:=]\s*\S+)"
)


def redact_node_log(value: Any) -> Any:
    """Return a recursively redacted log-safe copy of node metadata."""
    if isinstance(value, Mapping):
        return {
            str(key): "[REDACTED]"
            if any(term in str(key).lower().replace("-", "_") for term in _SENSITIVE_LOG_TERMS)
            else redact_node_log(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_node_log(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_node_log(item) for item in value)
    if isinstance(value, str) and _SENSITIVE_LOG_VALUE.search(value):
        return "[REDACTED]"
    return value


def capture_environment(*, lockfile_fingerprint: str) -> dict[str, str]:
    """Capture bounded runtime identity for a node preflight manifest."""
    if not lockfile_fingerprint.strip():
        raise NodeExportError("lockfile_fingerprint must be non-empty")
    if _FINGERPRINT.fullmatch(lockfile_fingerprint) is None:
        raise NodeExportError("lockfile_fingerprint must be a sha256 digest")
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
    input_fingerprint: str | None = None,
    minimum_cell_count: int | None = None,
    custodian_minimum_cell_count: int = 5,
    query_history: Sequence[Mapping[str, str]] = (),
    max_queries_per_group: int | None = None,
    custodian_max_queries_per_group: int = 1,
    allowed_dimension_fields: Sequence[str] | None = None,
    custodian_allowed_dimension_fields: Sequence[str] = ("jurisdiction", "group", "diagnosis"),
) -> dict[str, Any]:
    """Execute the synthetic node boundary without persistence or network access."""
    try:
        computed_input_fingerprint = (
            "sha256:"
            + hashlib.sha256(
                json.dumps(list(rows), sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )
    except (TypeError, ValueError) as exc:
        raise NodeExportError("node input must be canonically serializable") from exc
    if input_fingerprint is not None and input_fingerprint != computed_input_fingerprint:
        raise NodeExportError("supplied input fingerprint does not match node input")
    effective_minimum = (
        custodian_minimum_cell_count if minimum_cell_count is None else minimum_cell_count
    )
    if effective_minimum < custodian_minimum_cell_count:
        raise NodeExportError("analysis cannot weaken the custodian minimum-cell threshold")
    effective_query_limit = (
        custodian_max_queries_per_group if max_queries_per_group is None else max_queries_per_group
    )
    if effective_query_limit > custodian_max_queries_per_group:
        raise NodeExportError("analysis cannot weaken the custodian query budget")
    effective_dimensions = (
        tuple(custodian_allowed_dimension_fields)
        if allowed_dimension_fields is None
        else tuple(allowed_dimension_fields)
    )
    if not set(effective_dimensions).issubset(custodian_allowed_dimension_fields):
        raise NodeExportError("analysis cannot expand custodian-approved dimensions")
    validate_query_request(
        query_fingerprint=computed_input_fingerprint,
        overlap_group=analysis_id,
        prior_queries=query_history,
        max_queries_per_group=effective_query_limit,
    )
    exported_rows = validate_aggregate_export(
        rows,
        minimum_cell_count=effective_minimum,
        allowed_dimension_fields=effective_dimensions,
    )
    output_fingerprint = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(exported_rows, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    manifest = build_execution_manifest(
        execution_id=execution_id,
        coordinator_version=coordinator_version,
        node_version=node_version,
        analysis_id=analysis_id,
        policy_id=policy_id,
        input_fingerprint=computed_input_fingerprint,
        output_fingerprint=output_fingerprint,
        status="completed",
    )
    return {
        "schema_version": "0.1.0",
        "manifest": manifest,
        "rows": exported_rows,
    }


def verify_output_fingerprint(result: Mapping[str, Any]) -> None:
    """Verify that a node result's rows match its manifest output digest."""
    manifest = result.get("manifest")
    rows = result.get("rows")
    if not isinstance(manifest, Mapping) or not isinstance(rows, list):
        raise NodeExportError("node result must contain manifest and rows")
    expected = manifest.get("output_fingerprint")
    observed = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    if expected != observed:
        raise NodeExportError("node output fingerprint mismatch")


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

_SENSITIVE_FIELD_TERMS = {
    "person_id",
    "participant_id",
    "record_id",
    "admission_id",
    "date_of_birth",
    "dob",
    "email",
    "address",
    "phone",
    "first_name",
    "last_name",
    "full_name",
}


def validate_query_request(
    *,
    query_fingerprint: str,
    overlap_group: str,
    prior_queries: Sequence[Mapping[str, str]],
    max_queries_per_group: int,
) -> None:
    """Fail closed on replay or a custodian-defined overlapping-query budget."""
    if not query_fingerprint.strip() or not overlap_group.strip():
        raise NodeExportError("query fingerprint and overlap group must be non-empty")
    if max_queries_per_group < 1:
        raise NodeExportError("max_queries_per_group must be positive")
    fingerprints = {str(item.get("query_fingerprint", "")) for item in prior_queries}
    if query_fingerprint in fingerprints:
        raise NodeExportError("duplicate query fingerprint is not permitted")
    group_count = sum(str(item.get("overlap_group", "")) == overlap_group for item in prior_queries)
    if group_count >= max_queries_per_group:
        raise NodeExportError("overlapping-query budget exhausted")


def validate_aggregate_export(
    rows: Sequence[Mapping[str, Any]],
    *,
    count_field: str = "count",
    minimum_cell_count: int = 5,
    allowed_dimension_fields: Sequence[str] = ("jurisdiction", "group", "diagnosis"),
) -> list[dict[str, Any]]:
    """Return disclosure-safe aggregate rows, suppressing cells below threshold."""
    if minimum_cell_count < 1:
        raise NodeExportError("minimum_cell_count must be positive")
    exported: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        keys = {str(key) for key in row}
        normalized_keys = {key.lower().replace("-", "_").replace(" ", "_") for key in keys}
        leaked = sorted(normalized_keys & (_PARTICIPANT_FIELDS | _SENSITIVE_FIELD_TERMS))
        if leaked:
            raise NodeExportError(
                f"row {index} contains participant-level fields: {', '.join(leaked)}"
            )
        if count_field not in row:
            raise NodeExportError(f"row {index} lacks count field {count_field!r}")
        count = row[count_field]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise NodeExportError(f"row {index} count must be a non-negative integer")
        allowed = set(allowed_dimension_fields)
        unexpected = sorted(keys - allowed - {count_field})
        if unexpected:
            raise NodeExportError(
                f"row {index} contains unapproved export fields: {', '.join(unexpected)}"
            )
        safe: dict[str, Any] = {}
        dimensions = [key for key in row if str(key) != count_field]
        if not dimensions:
            raise NodeExportError(f"row {index} requires an approved aggregate dimension")
        for key, value in row.items():
            if str(key) == count_field:
                continue
            if isinstance(value, (Mapping, list, tuple, set)):
                raise NodeExportError(f"row {index} contains nested export values")
            if not isinstance(value, str) or not value.strip():
                raise NodeExportError(f"row {index} dimension values must be non-empty strings")
            safe[str(key)] = value
        if count < minimum_cell_count:
            safe = {"count_status": "suppressed", count_field: None}
        else:
            safe["count_status"] = "released"
            safe[count_field] = count
        exported.append(safe)
    return exported


__all__ = [
    "NodeExportError",
    "amend_execution_manifest",
    "build_execution_manifest",
    "build_synthetic_cohort",
    "capture_environment",
    "redact_node_log",
    "run_offline_node",
    "validate_aggregate_export",
    "validate_query_request",
    "validate_version_compatibility",
    "verify_output_fingerprint",
]
