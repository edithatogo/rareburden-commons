"""Immutable disclosure-policy and synthetic query-ledger primitives."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from rareburden.node import NodeExportError, run_offline_node

_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_POLICY_REQUIRED = {
    "schema_version",
    "policy_id",
    "minimum_cell_count",
    "max_queries_per_overlap_group",
    "allowed_dimension_fields",
    "participant_fields",
    "export_mode",
}
_POLICY_OPTIONAL = {"notes"}
_ALLOWED_DIMENSIONS = {"jurisdiction", "group", "diagnosis"}
_EXPORT_MODES = {"aggregate_only", "metadata_only"}
_FINGERPRINT = re.compile(r"^sha256:[0-9a-f]{64}$")
_SUPPORTED_POLICY_SCHEMA_VERSION = "0.1.0"
_MAXIMUM_POLICY_FANOUT = 1_000
_MAXIMUM_POLICY_STRING_LENGTH = 4_096


def _validate_bounded_policy_json(document: object) -> None:
    if type(document) is not dict:
        raise NodeExportError("disclosure policy must be an exact JSON object")
    nodes = 0
    stack: list[object] = [document]
    while stack:
        current = stack.pop()
        nodes += 1
        if nodes > 10_000:
            raise NodeExportError("disclosure policy exceeds bounded JSON structure")
        if type(current) is dict:
            if len(current) > _MAXIMUM_POLICY_FANOUT:
                raise NodeExportError("disclosure policy exceeds bounded JSON structure")
            for key, value in current.items():
                if type(key) is not str:
                    raise NodeExportError("disclosure policy must use exact JSON types")
                if len(key) > _MAXIMUM_POLICY_STRING_LENGTH:
                    raise NodeExportError("disclosure policy exceeds bounded JSON structure")
                stack.append(value)
        elif type(current) is list:
            if len(current) > _MAXIMUM_POLICY_FANOUT:
                raise NodeExportError("disclosure policy exceeds bounded JSON structure")
            stack.extend(current)
        elif type(current) is str:
            if len(current) > _MAXIMUM_POLICY_STRING_LENGTH:
                raise NodeExportError("disclosure policy exceeds bounded JSON structure")
        elif current is not None and type(current) not in {bool, int, float}:
            raise NodeExportError("disclosure policy must use exact JSON types")


def _non_empty_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise NodeExportError(f"{label} must be a non-empty string")
    return value


def _positive_integer(value: Any, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise NodeExportError(f"{label} must be a positive integer")
    return int(value)


def _unique_strings(value: Any, *, label: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or not value:
        raise NodeExportError(f"{label} must be a non-empty array")
    items = tuple(_non_empty_string(item, label=f"{label} item") for item in value)
    if len(set(items)) != len(items):
        raise NodeExportError(f"{label} must contain unique values")
    return items


@dataclass(frozen=True, slots=True)
class DisclosurePolicy:
    """Validated immutable candidate policy; provenance is checked elsewhere."""

    schema_version: str
    policy_id: str
    minimum_cell_count: int
    max_queries_per_overlap_group: int
    allowed_dimension_fields: tuple[str, ...]
    participant_fields: tuple[str, ...]
    export_mode: str
    notes: tuple[str, ...] = ()


def load_disclosure_policy(document: Mapping[str, Any]) -> DisclosurePolicy:
    """Validate an in-memory policy document and return an immutable value."""
    _validate_bounded_policy_json(document)
    keys = set(document)
    missing = _POLICY_REQUIRED - keys
    unknown = keys - _POLICY_REQUIRED - _POLICY_OPTIONAL
    if missing:
        raise NodeExportError(f"disclosure policy is missing fields: {sorted(missing)}")
    if unknown:
        raise NodeExportError(f"disclosure policy has unknown fields: {sorted(unknown)}")

    schema_version = _non_empty_string(document["schema_version"], label="schema_version")
    if _SEMVER.fullmatch(schema_version) is None:
        raise NodeExportError("schema_version must be a semantic version")
    if schema_version != _SUPPORTED_POLICY_SCHEMA_VERSION:
        raise NodeExportError("schema_version is unsupported")
    dimensions = _unique_strings(
        document["allowed_dimension_fields"], label="allowed_dimension_fields"
    )
    if not set(dimensions).issubset(_ALLOWED_DIMENSIONS):
        raise NodeExportError("allowed_dimension_fields contains an unsupported dimension")
    export_mode = _non_empty_string(document["export_mode"], label="export_mode")
    if export_mode not in _EXPORT_MODES:
        raise NodeExportError("export_mode is unsupported")
    notes_value = document.get("notes", ())
    if isinstance(notes_value, (str, bytes)) or not isinstance(notes_value, Sequence):
        raise NodeExportError("notes must be an array")
    notes = tuple(_non_empty_string(note, label="notes item") for note in notes_value)

    policy_id = _non_empty_string(document["policy_id"], label="policy_id")
    if len(policy_id) < 3:
        raise NodeExportError("policy_id must contain at least three characters")
    participant_fields = _unique_strings(document["participant_fields"], label="participant_fields")
    normalised_participant_fields = {
        item.strip().lower().replace("-", "_").replace(" ", "_") for item in participant_fields
    }
    if set(dimensions) & normalised_participant_fields:
        raise NodeExportError("participant_fields must not overlap allowed_dimension_fields")
    return DisclosurePolicy(
        schema_version=schema_version,
        policy_id=policy_id,
        minimum_cell_count=_positive_integer(
            document["minimum_cell_count"], label="minimum_cell_count"
        ),
        max_queries_per_overlap_group=_positive_integer(
            document["max_queries_per_overlap_group"],
            label="max_queries_per_overlap_group",
        ),
        allowed_dimension_fields=dimensions,
        participant_fields=participant_fields,
        export_mode=export_mode,
        notes=notes,
    )


@dataclass(frozen=True, slots=True)
class QueryLedgerEntry:
    """One immutable, value-free synthetic query registration."""

    sequence: int
    query_fingerprint: str
    overlap_group: str
    analysis_id: str
    policy_id: str
    dimensions: tuple[str, ...]
    measure: str


@dataclass(frozen=True, slots=True)
class QueryLedger:
    """Ephemeral ledger represented by immutable snapshots.

    This value supports bounded synthetic execution. It is resettable by a caller
    and therefore is not an authoritative custodian system of record.
    """

    entries: tuple[QueryLedgerEntry, ...] = ()

    def append(
        self,
        query_shape: Mapping[str, Any],
        *,
        overlap_group: str,
        policy: DisclosurePolicy,
    ) -> QueryLedger:
        """Return a new ledger snapshot after fail-closed policy checks."""
        normalised = _validate_query_shape(query_shape, policy=policy)
        group = _non_empty_string(overlap_group, label="overlap_group")
        fingerprint = query_shape_fingerprint(normalised)
        if any(entry.query_fingerprint == fingerprint for entry in self.entries):
            raise NodeExportError("duplicate query fingerprint is not permitted")
        group_count = sum(entry.overlap_group == group for entry in self.entries)
        if group_count >= policy.max_queries_per_overlap_group:
            raise NodeExportError("overlapping-query budget exhausted")
        entry = QueryLedgerEntry(
            sequence=len(self.entries) + 1,
            query_fingerprint=fingerprint,
            overlap_group=group,
            analysis_id=normalised["analysis_id"],
            policy_id=policy.policy_id,
            dimensions=normalised["dimensions"],
            measure=normalised["measure"],
        )
        return QueryLedger(entries=(*self.entries, entry))


def run_policy_bound_synthetic_node(
    rows: Sequence[Mapping[str, Any]],
    *,
    query_shape: Mapping[str, Any],
    overlap_group: str,
    policy: DisclosurePolicy,
    ledger: QueryLedger,
    execution_id: str,
    coordinator_version: str,
    node_version: str,
) -> tuple[dict[str, Any], QueryLedger]:
    """Register a bounded query and run it under one candidate policy snapshot.

    The returned ledger is the new immutable snapshot. Callers must persist it in
    an independently controlled store before this pattern can be used as an
    authoritative operational boundary.
    """
    next_ledger = ledger.append(query_shape, overlap_group=overlap_group, policy=policy)
    registered = next_ledger.entries[-1]
    expected_fields = {*registered.dimensions, "count"}
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping) or set(row) != expected_fields:
            raise NodeExportError(
                f"row {index} fields must exactly match the registered query dimensions and count"
            )
    result = run_offline_node(
        rows,
        execution_id=execution_id,
        coordinator_version=coordinator_version,
        node_version=node_version,
        analysis_id=registered.analysis_id,
        policy_id=policy.policy_id,
        minimum_cell_count=policy.minimum_cell_count,
        custodian_minimum_cell_count=policy.minimum_cell_count,
        max_queries_per_group=policy.max_queries_per_overlap_group,
        custodian_max_queries_per_group=policy.max_queries_per_overlap_group,
        allowed_dimension_fields=registered.dimensions,
        custodian_allowed_dimension_fields=policy.allowed_dimension_fields,
    )
    return result, next_ledger


def _validate_query_shape(
    query_shape: Mapping[str, Any], *, policy: DisclosurePolicy
) -> dict[str, Any]:
    if not isinstance(query_shape, Mapping):
        raise NodeExportError("query shape must be an object")
    if set(query_shape) != {"analysis_id", "dimensions", "measure"}:
        raise NodeExportError("query shape must contain only analysis_id, dimensions and measure")
    analysis_id = _non_empty_string(query_shape["analysis_id"], label="analysis_id")
    dimensions = _unique_strings(query_shape["dimensions"], label="dimensions")
    if not set(dimensions).issubset(policy.allowed_dimension_fields):
        raise NodeExportError("query shape expands custodian-approved dimensions")
    measure = _non_empty_string(query_shape["measure"], label="measure")
    if measure != "count":
        raise NodeExportError("only the aggregate count measure is supported")
    if policy.export_mode != "aggregate_only":
        raise NodeExportError("policy does not authorize aggregate query execution")
    return {
        "analysis_id": analysis_id,
        "dimensions": tuple(sorted(dimensions)),
        "measure": measure,
    }


def query_shape_fingerprint(query_shape: Mapping[str, Any]) -> str:
    """Return a stable SHA-256 identity for an already bounded query shape."""
    try:
        encoded = json.dumps(
            query_shape, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise NodeExportError("query shape must be canonically serializable") from exc
    fingerprint = "sha256:" + hashlib.sha256(encoded).hexdigest()
    if _FINGERPRINT.fullmatch(fingerprint) is None:  # defensive invariant
        raise NodeExportError("could not create query fingerprint")
    return fingerprint


__all__ = [
    "DisclosurePolicy",
    "QueryLedger",
    "QueryLedgerEntry",
    "load_disclosure_policy",
    "query_shape_fingerprint",
    "run_policy_bound_synthetic_node",
]
