"""Experimental synthetic-only orchestration over durable policy reservations."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from rareburden.node import (
    NodeExportError,
    run_offline_node,
    validate_version_compatibility,
)
from rareburden.node_analysis import (
    ALLOWED_SYNTHETIC_DIMENSIONS,
    aggregate_synthetic_records,
    validate_synthetic_records,
)
from rareburden.node_policy import load_disclosure_policy, query_shape_fingerprint
from rareburden.node_policy_store import (
    DurableNodePolicyStore,
    NodePolicyStoreError,
    QueryReceipt,
    canonical_policy_content_sha256,
)


class SyntheticOrchestrationError(ValueError):
    """Raised when the bounded experimental orchestration fails closed."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_FINGERPRINT = re.compile(r"^sha256:[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_SENSITIVE_IDENTIFIER_TERMS = {
    "authorization",
    "bearer",
    "cookie",
    "credential",
    "email",
    "id",
    "identifier",
    "participant",
    "patient",
    "password",
    "person",
    "record",
    "secret",
    "session",
    "token",
}


def _bounded_non_sensitive_identifier(value: object, *, label: str, minimum_length: int = 1) -> str:
    if (
        not isinstance(value, str)
        or len(value) < minimum_length
        or _IDENTIFIER.fullmatch(value) is None
    ):
        raise SyntheticOrchestrationError(f"{label} must be a bounded non-sensitive identifier")
    terms = set(re.split(r"[_.:-]+", value.lower()))
    if terms & _SENSITIVE_IDENTIFIER_TERMS:
        raise SyntheticOrchestrationError(f"{label} must be a bounded non-sensitive identifier")
    return value


def _frozen_json(value: object, *, label: str) -> Any:
    try:
        return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":")))
    except (TypeError, ValueError) as exc:
        raise SyntheticOrchestrationError(f"{label} must be JSON serializable") from exc


def _receipt_document(receipt: QueryReceipt) -> dict[str, object]:
    return {
        "sequence": receipt.sequence,
        "query_fingerprint": receipt.query_fingerprint,
        "overlap_group": receipt.overlap_group,
        "policy_id": receipt.policy_id,
        "chain_sha256": receipt.chain_sha256,
        "previous_chain_sha256": receipt.previous_chain_sha256,
        "recorded_at": receipt.recorded_at,
    }


def run_reserved_synthetic_analysis(
    records: Sequence[Mapping[str, Any]],
    *,
    store: DurableNodePolicyStore,
    query_shape: Mapping[str, Any],
    analysis_id: str,
    overlap_group: str,
    expected_policy_id: str,
    expected_policy_content_sha256: str,
    recorded_at: str,
    execution_id: str,
    coordinator_version: str,
    node_version: str,
) -> dict[str, Any]:
    """Reserve before aggregating and return one receipt-bound in-memory result.

    This interface is an experimental synthetic fixture boundary. A raised error
    after reservation does not refund or retry the committed query.
    """
    validate_version_compatibility(
        coordinator_version=coordinator_version, node_version=node_version
    )
    _bounded_non_sensitive_identifier(execution_id, label="execution_id", minimum_length=3)
    _bounded_non_sensitive_identifier(analysis_id, label="analysis_id", minimum_length=3)
    _bounded_non_sensitive_identifier(overlap_group, label="overlap_group")
    if (
        not isinstance(expected_policy_content_sha256, str)
        or _SHA256.fullmatch(expected_policy_content_sha256) is None
    ):
        raise SyntheticOrchestrationError("expected policy content digest must be a sha256 digest")
    frozen_query = _frozen_json(query_shape, label="query_shape")
    frozen_records = _frozen_json(records, label="records")
    if not isinstance(frozen_query, dict) or not isinstance(frozen_records, list):
        raise SyntheticOrchestrationError("query_shape and records have invalid JSON structure")
    if "analysis_id" in frozen_query:
        raise SyntheticOrchestrationError(
            "analysis identity must be supplied through the operator-bound argument"
        )

    dimensions_value = frozen_query.get("dimensions")
    if not isinstance(dimensions_value, list):
        raise SyntheticOrchestrationError("query dimensions must be an array")
    dimensions = tuple(dimensions_value)
    validate_synthetic_records(frozen_records, dimensions=dimensions)

    # This call is the irreversible boundary. Never retry it here: a database
    # error during COMMIT can have an ambiguous outcome to the caller.
    reserved_query = {**frozen_query, "analysis_id": analysis_id}
    reservation = store.reserve_query(
        reserved_query,
        overlap_group=overlap_group,
        policy_id=expected_policy_id,
        expected_policy_content_sha256=expected_policy_content_sha256,
        recorded_at=recorded_at,
    )

    rows = aggregate_synthetic_records(frozen_records, dimensions=dimensions)
    result = run_offline_node(
        rows,
        execution_id=execution_id,
        coordinator_version=coordinator_version,
        node_version=node_version,
        analysis_id=reservation.registered_query.analysis_id,
        policy_id=reservation.policy.policy_id,
        minimum_cell_count=reservation.policy.minimum_cell_count,
        custodian_minimum_cell_count=reservation.policy.minimum_cell_count,
        max_queries_per_group=reservation.policy.max_queries_per_overlap_group,
        custodian_max_queries_per_group=reservation.policy.max_queries_per_overlap_group,
        allowed_dimension_fields=dimensions,
        custodian_allowed_dimension_fields=reservation.policy.allowed_dimension_fields,
    )
    manifest = result["manifest"]
    if not isinstance(manifest, Mapping):
        raise NodeExportError("node result manifest is invalid")
    return {
        "schema_version": "0.1.0",
        "scope": "experimental_synthetic_only",
        "reservation": {
            **_receipt_document(reservation.receipt),
            "policy_content_sha256": reservation.policy_content_sha256,
            "analysis_id": reservation.registered_query.analysis_id,
            "dimensions": list(reservation.registered_query.dimensions),
            "measure": reservation.registered_query.measure,
            "minimum_cell_count": reservation.policy.minimum_cell_count,
        },
        "execution": result,
        "binding": {
            "receipt_sequence": reservation.receipt.sequence,
            "receipt_chain_sha256": reservation.receipt.chain_sha256,
            "query_fingerprint": reservation.receipt.query_fingerprint,
            "overlap_group": reservation.receipt.overlap_group,
            "policy_id": reservation.policy.policy_id,
            "policy_content_sha256": reservation.policy_content_sha256,
            "execution_id": manifest["execution_id"],
            "input_fingerprint": manifest["input_fingerprint"],
            "output_fingerprint": manifest["output_fingerprint"],
            "minimum_cell_count": reservation.policy.minimum_cell_count,
        },
    }


def verify_reserved_synthetic_result(
    envelope: Mapping[str, Any],
    *,
    trusted_policy_document: Mapping[str, Any],
    trusted_input_rows: Sequence[Mapping[str, Any]],
    trusted_query_shape: Mapping[str, Any],
    trusted_analysis_id: str,
    trusted_overlap_group: str,
    trusted_execution_id: str,
    trusted_coordinator_version: str,
    trusted_node_version: str,
) -> None:
    """Verify correspondence to independently retained synthetic references.

    The trusted inputs are an operator provenance premise; this function does
    not establish their authenticity, store membership or external authority.
    """
    if (
        set(envelope) != {"schema_version", "scope", "reservation", "execution", "binding"}
        or envelope.get("schema_version") != "0.1.0"
        or envelope.get("scope") != "experimental_synthetic_only"
    ):
        raise SyntheticOrchestrationError("reserved result envelope is malformed")
    reservation = envelope.get("reservation")
    binding = envelope.get("binding")
    execution = envelope.get("execution")
    if (
        not isinstance(reservation, Mapping)
        or not isinstance(binding, Mapping)
        or not isinstance(execution, Mapping)
    ):
        raise SyntheticOrchestrationError("reserved result envelope is malformed")
    required_reservation = {
        "sequence",
        "query_fingerprint",
        "overlap_group",
        "policy_id",
        "chain_sha256",
        "previous_chain_sha256",
        "recorded_at",
        "policy_content_sha256",
        "analysis_id",
        "dimensions",
        "measure",
        "minimum_cell_count",
    }
    required_binding = {
        "receipt_sequence",
        "receipt_chain_sha256",
        "query_fingerprint",
        "overlap_group",
        "policy_id",
        "policy_content_sha256",
        "execution_id",
        "input_fingerprint",
        "output_fingerprint",
        "minimum_cell_count",
    }
    if (
        set(reservation) != required_reservation
        or set(binding) != required_binding
        or set(execution) != {"schema_version", "manifest", "rows"}
        or execution.get("schema_version") != "0.1.0"
        or any(binding.get(field) is None for field in required_binding)
    ):
        raise SyntheticOrchestrationError("reserved result envelope is malformed")
    manifest = execution.get("manifest")
    if not isinstance(manifest, Mapping):
        raise SyntheticOrchestrationError("reserved result manifest is malformed")
    required_manifest_bindings = {
        "execution_id",
        "analysis_id",
        "policy_id",
        "input_fingerprint",
        "output_fingerprint",
    }
    required_manifest = {
        "schema_version",
        "execution_id",
        "coordinator_version",
        "node_version",
        "analysis_id",
        "policy_id",
        "status",
        "input_fingerprint",
        "output_fingerprint",
        "limitations",
    }
    if (
        set(manifest) != required_manifest
        or not required_manifest_bindings.issubset(manifest)
        or any(manifest.get(field) is None for field in required_manifest_bindings)
        or manifest.get("schema_version") != "0.1.0"
        or manifest.get("status") != "completed"
        or manifest.get("limitations") != ["Synthetic/offline manifest; no participant-level data."]
        or not all(
            isinstance(binding.get(field), str)
            and _FINGERPRINT.fullmatch(binding[field]) is not None
            for field in ("query_fingerprint", "input_fingerprint", "output_fingerprint")
        )
        or not isinstance(binding.get("policy_content_sha256"), str)
        or _SHA256.fullmatch(binding["policy_content_sha256"]) is None
    ):
        raise SyntheticOrchestrationError("reserved result binding is malformed")
    pairs = (
        (binding.get("receipt_sequence"), reservation.get("sequence")),
        (binding.get("receipt_chain_sha256"), reservation.get("chain_sha256")),
        (binding.get("query_fingerprint"), reservation.get("query_fingerprint")),
        (binding.get("overlap_group"), reservation.get("overlap_group")),
        (binding.get("policy_id"), reservation.get("policy_id")),
        (binding.get("policy_content_sha256"), reservation.get("policy_content_sha256")),
        (binding.get("execution_id"), manifest.get("execution_id")),
        (binding.get("input_fingerprint"), manifest.get("input_fingerprint")),
        (binding.get("output_fingerprint"), manifest.get("output_fingerprint")),
        (binding.get("minimum_cell_count"), reservation.get("minimum_cell_count")),
        (reservation.get("analysis_id"), manifest.get("analysis_id")),
        (reservation.get("policy_id"), manifest.get("policy_id")),
    )
    if any(left != right for left, right in pairs):
        raise SyntheticOrchestrationError("reserved result binding mismatch")
    try:
        _bounded_non_sensitive_identifier(
            trusted_analysis_id, label="trusted_analysis_id", minimum_length=3
        )
        _bounded_non_sensitive_identifier(
            trusted_overlap_group, label="trusted_overlap_group", minimum_length=1
        )
        _bounded_non_sensitive_identifier(
            trusted_execution_id, label="trusted_execution_id", minimum_length=3
        )
        trusted_policy = load_disclosure_policy(trusted_policy_document)
        trusted_policy_digest = canonical_policy_content_sha256(trusted_policy_document)
    except (NodeExportError, NodePolicyStoreError) as exc:
        raise SyntheticOrchestrationError("trusted policy is invalid") from exc
    if (
        trusted_policy.policy_id != reservation.get("policy_id")
        or trusted_policy_digest != reservation.get("policy_content_sha256")
        or type(reservation.get("minimum_cell_count")) is not int
        or trusted_policy.minimum_cell_count != reservation.get("minimum_cell_count")
        or trusted_analysis_id != reservation.get("analysis_id")
        or trusted_overlap_group != reservation.get("overlap_group")
        or trusted_execution_id != manifest.get("execution_id")
    ):
        raise SyntheticOrchestrationError("trusted policy binding mismatch")
    _bounded_non_sensitive_identifier(
        manifest.get("execution_id"), label="execution_id", minimum_length=3
    )
    dimensions = reservation.get("dimensions")
    sequence = reservation.get("sequence")
    previous_chain = reservation.get("previous_chain_sha256")
    recorded_at = reservation.get("recorded_at")
    minimum_cell_count = reservation.get("minimum_cell_count")
    if (
        not isinstance(sequence, int)
        or isinstance(sequence, bool)
        or sequence < 1
        or not all(
            isinstance(reservation.get(field), str)
            and _IDENTIFIER.fullmatch(reservation[field]) is not None
            for field in ("analysis_id", "policy_id", "overlap_group")
        )
        or not isinstance(reservation.get("query_fingerprint"), str)
        or _FINGERPRINT.fullmatch(reservation["query_fingerprint"]) is None
        or not isinstance(reservation.get("policy_content_sha256"), str)
        or _SHA256.fullmatch(reservation["policy_content_sha256"]) is None
        or not isinstance(reservation.get("chain_sha256"), str)
        or _SHA256.fullmatch(reservation["chain_sha256"]) is None
        or (
            previous_chain is not None
            and (not isinstance(previous_chain, str) or _SHA256.fullmatch(previous_chain) is None)
        )
        or not isinstance(recorded_at, str)
        or not isinstance(dimensions, list)
        or not dimensions
        or any(not isinstance(value, str) or not value for value in dimensions)
        or dimensions != sorted(set(dimensions))
        or not set(dimensions).issubset(ALLOWED_SYNTHETIC_DIMENSIONS)
        or reservation.get("measure") != "count"
        or type(minimum_cell_count) is not int
        or minimum_cell_count < 1
    ):
        raise SyntheticOrchestrationError("reserved result query identity is malformed")
    try:
        parsed_recorded_at = datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))
        validate_version_compatibility(
            coordinator_version=manifest["coordinator_version"],
            node_version=manifest["node_version"],
        )
    except (AttributeError, TypeError, ValueError, NodeExportError) as exc:
        raise SyntheticOrchestrationError("reserved result query identity is malformed") from exc
    if parsed_recorded_at.tzinfo is None or parsed_recorded_at.utcoffset() is None:
        raise SyntheticOrchestrationError("reserved result query identity is malformed")
    expected_query_fingerprint = query_shape_fingerprint(
        {
            "analysis_id": reservation.get("analysis_id"),
            "dimensions": dimensions,
            "measure": reservation.get("measure"),
        }
    )
    chain_payload = {
        "sequence": reservation.get("sequence"),
        "query_fingerprint": reservation.get("query_fingerprint"),
        "overlap_group": reservation.get("overlap_group"),
        "analysis_id": reservation.get("analysis_id"),
        "policy_id": reservation.get("policy_id"),
        "dimensions": dimensions,
        "measure": reservation.get("measure"),
        "previous_chain_sha256": reservation.get("previous_chain_sha256"),
        "recorded_at": reservation.get("recorded_at"),
    }
    expected_chain = hashlib.sha256(
        json.dumps(chain_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "ascii"
        )
    ).hexdigest()
    if (
        reservation.get("query_fingerprint") != expected_query_fingerprint
        or reservation.get("chain_sha256") != expected_chain
    ):
        raise SyntheticOrchestrationError("reserved result query identity mismatch")
    try:
        frozen_input_rows = _frozen_json(trusted_input_rows, label="trusted_input_rows")
        frozen_query = _frozen_json(trusted_query_shape, label="trusted_query_shape")
        if not isinstance(frozen_input_rows, list) or not isinstance(frozen_query, dict):
            raise SyntheticOrchestrationError("trusted aggregate input is malformed")
        if set(frozen_query) != {"dimensions", "measure"}:
            raise SyntheticOrchestrationError("trusted aggregate input is malformed")
        trusted_dimensions = frozen_query["dimensions"]
        if (
            not isinstance(trusted_dimensions, list)
            or not trusted_dimensions
            or any(not isinstance(value, str) or not value for value in trusted_dimensions)
            or len(set(trusted_dimensions)) != len(trusted_dimensions)
        ):
            raise SyntheticOrchestrationError("trusted aggregate input is malformed")
        normalised_trusted_dimensions = sorted(trusted_dimensions)
        if normalised_trusted_dimensions != dimensions or frozen_query[
            "measure"
        ] != reservation.get("measure"):
            raise SyntheticOrchestrationError("trusted aggregate input or output mismatch")
        expected_input_fields = {*normalised_trusted_dimensions, "count"}
        if any(
            not isinstance(row, dict) or set(row) != expected_input_fields
            for row in frozen_input_rows
        ):
            raise SyntheticOrchestrationError("trusted aggregate input is malformed")
        expected_execution = run_offline_node(
            frozen_input_rows,
            execution_id=trusted_execution_id,
            coordinator_version=trusted_coordinator_version,
            node_version=trusted_node_version,
            analysis_id=trusted_analysis_id,
            policy_id=trusted_policy.policy_id,
            minimum_cell_count=trusted_policy.minimum_cell_count,
            custodian_minimum_cell_count=trusted_policy.minimum_cell_count,
            max_queries_per_group=trusted_policy.max_queries_per_overlap_group,
            custodian_max_queries_per_group=trusted_policy.max_queries_per_overlap_group,
            allowed_dimension_fields=normalised_trusted_dimensions,
            custodian_allowed_dimension_fields=trusted_policy.allowed_dimension_fields,
        )
    except (TypeError, ValueError, UnicodeEncodeError, NodeExportError) as exc:
        raise SyntheticOrchestrationError("trusted aggregate input is malformed") from exc
    if _frozen_json(execution, label="execution") != _frozen_json(
        expected_execution, label="expected_execution"
    ):
        raise SyntheticOrchestrationError("trusted aggregate input or output mismatch")


__all__ = [
    "SyntheticOrchestrationError",
    "run_reserved_synthetic_analysis",
    "verify_reserved_synthetic_result",
]
