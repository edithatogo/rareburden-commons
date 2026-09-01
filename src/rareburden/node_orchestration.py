"""Experimental synthetic-only orchestration over durable policy reservations."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from rareburden.node import (
    NodeExportError,
    run_offline_node,
    validate_version_compatibility,
    verify_output_fingerprint,
)
from rareburden.node_analysis import aggregate_synthetic_records, validate_synthetic_records
from rareburden.node_policy import query_shape_fingerprint
from rareburden.node_policy_store import DurableNodePolicyStore, QueryReceipt


class SyntheticOrchestrationError(ValueError):
    """Raised when the bounded experimental orchestration fails closed."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


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
        },
    }


def verify_reserved_synthetic_result(envelope: Mapping[str, Any]) -> None:
    """Fail closed if a returned result was detached from its reservation."""
    reservation = envelope.get("reservation")
    binding = envelope.get("binding")
    execution = envelope.get("execution")
    if (
        not isinstance(reservation, Mapping)
        or not isinstance(binding, Mapping)
        or not isinstance(execution, Mapping)
    ):
        raise SyntheticOrchestrationError("reserved result envelope is malformed")
    manifest = execution.get("manifest")
    if not isinstance(manifest, Mapping):
        raise SyntheticOrchestrationError("reserved result manifest is malformed")
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
        (reservation.get("analysis_id"), manifest.get("analysis_id")),
        (reservation.get("policy_id"), manifest.get("policy_id")),
    )
    if any(left != right for left, right in pairs):
        raise SyntheticOrchestrationError("reserved result binding mismatch")
    dimensions = reservation.get("dimensions")
    try:
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
            json.dumps(
                chain_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode("ascii")
        ).hexdigest()
    except (TypeError, ValueError, UnicodeEncodeError, NodeExportError) as exc:
        raise SyntheticOrchestrationError("reserved result query identity is malformed") from exc
    if (
        reservation.get("query_fingerprint") != expected_query_fingerprint
        or reservation.get("chain_sha256") != expected_chain
    ):
        raise SyntheticOrchestrationError("reserved result query identity mismatch")
    rows = execution.get("rows")
    if (
        reservation.get("measure") != "count"
        or not isinstance(dimensions, list)
        or not isinstance(rows, list)
        or any(
            not isinstance(row, Mapping)
            or not set(dimensions).issubset(row)
            or "count_status" not in row
            or not set(row).issubset({*dimensions, "count", "count_status"})
            for row in rows
        )
    ):
        raise SyntheticOrchestrationError("reserved result query shape mismatch")
    try:
        verify_output_fingerprint(execution)
    except NodeExportError as exc:
        raise SyntheticOrchestrationError("reserved result output mismatch") from exc


__all__ = [
    "SyntheticOrchestrationError",
    "run_reserved_synthetic_analysis",
    "verify_reserved_synthetic_result",
]
