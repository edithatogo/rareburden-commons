"""Experimental public-use descriptive counting, separate from synthetic runners."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from typing import Any

from rareburden.node import NodeExportError, validate_aggregate_export
from rareburden.node_policy_store import DurableNodePolicyStore

LABELS = {
    "uci": {
        "NO": "no_recorded_readmission",
        "<30": "readmission_under_30_days",
        ">30": "readmission_over_30_days",
    },
    "nhanes": {
        "1": "reported_diabetes",
        "2": "reported_no_diabetes",
        "3": "borderline",
        "7": "refused",
        "9": "unknown",
        "missing": "missing",
    },
}


def _number(value: Any) -> str:
    if value is None or (type(value) is float and math.isnan(value)):
        return "missing"
    if type(value) not in (int, float) or not math.isfinite(value):
        raise NodeExportError("NHANES code must be finite numeric or missing")
    if int(value) != value:
        raise NodeExportError("NHANES code must be an integer")
    return str(int(value))


def prepare_public_records(rows: Iterable[Mapping[str, Any]], *, dataset: str) -> tuple[str, ...]:
    """Freeze allowlisted categories; duplicate observational-unit IDs fail.

    UCI units are encounters, not people. NHANES units are unweighted questionnaire
    respondents. Identifiers and unselected attributes never leave this function.
    """
    if dataset not in LABELS:
        raise NodeExportError("unsupported public dataset")
    seen: set[str] = set()
    labels = []
    for row in rows:
        required = (
            {"encounter_id", "patient_nbr", "readmitted"}
            if dataset == "uci"
            else {"SEQN", "DIQ010"}
        )
        if not required.issubset(row):
            raise NodeExportError("required public fields are missing")
        if dataset == "uci":
            identifier = row["encounter_id"]
            if any(
                type(v) is not str or re.fullmatch(r"[0-9]+", v) is None
                for v in (identifier, row["patient_nbr"])
            ):
                raise NodeExportError("UCI identifiers must be digit strings")
            code = row["readmitted"]
        else:
            identifier = _number(row["SEQN"])
            if identifier == "missing" or int(identifier) <= 0:
                raise NodeExportError("NHANES respondent key is invalid")
            code = _number(row["DIQ010"])
        if identifier in seen:
            raise NodeExportError("duplicate observational unit")
        seen.add(identifier)
        if type(code) is not str or code not in LABELS[dataset]:
            raise NodeExportError("unsupported response code")
        labels.append(LABELS[dataset][code])
    if not labels:
        raise NodeExportError("public input is empty")
    return tuple(labels)


def run_public_counts(
    rows: Iterable[Mapping[str, Any]],
    *,
    dataset: str,
    source_sha256: str,
    store: DurableNodePolicyStore,
    policy_id: str,
    policy_sha256: str,
    recorded_at: str,
) -> dict[str, Any]:
    """Reserve before counting; no retries/refunds after commitment.

    Caller must verify source bytes; a supplied digest is not origin authentication.
    Local privileged actors and database replacement remain outside this prototype.
    """
    for digest in (source_sha256, policy_sha256):
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise NodeExportError("fingerprint must be a SHA-256 digest")
    labels = prepare_public_records(rows, dataset=dataset)
    identity = f"public-{dataset}-descriptive-v1"
    reservation = store.reserve_query(
        {"analysis_id": identity, "dimensions": ["group"], "measure": "count"},
        overlap_group=identity,
        policy_id=policy_id,
        expected_policy_content_sha256=policy_sha256,
        recorded_at=recorded_at,
    )
    if reservation.policy.export_mode != "aggregate_only":
        raise NodeExportError("public counts require aggregate-only policy")
    counts = Counter(labels)
    categories = list(LABELS[dataset].values())
    exported = validate_aggregate_export(
        [{"group": category, "count": counts[category]} for category in categories],
        minimum_cell_count=reservation.policy.minimum_cell_count,
        allowed_dimension_fields=reservation.policy.allowed_dimension_fields,
    )
    result: dict[str, Any] = {
        "schema_version": "0.1.0",
        "evidence_type": "real_public_use_data",
        "scope": "experimental_descriptive_counts",
        "dataset": dataset,
        "unit": "encounter" if dataset == "uci" else "unweighted_respondent",
        "population_estimate": False,
        "clinical_validation": False,
        "custodian_deployment": False,
        "source_sha256": source_sha256,
        "policy_sha256": reservation.policy_content_sha256,
        "query_sha256": reservation.receipt.query_fingerprint,
        "receipt_chain_sha256": reservation.receipt.chain_sha256,
        "receipt_sequence": reservation.receipt.sequence,
        "category_order": categories,
        "rows": exported,
    }
    result["output_sha256"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return result
