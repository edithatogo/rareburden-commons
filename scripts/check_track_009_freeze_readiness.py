#!/usr/bin/env python3
"""Validate Track 009 freeze readiness without approving or freezing ledger contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml


class Track009ReadinessError(ValueError):
    """Raised when the Track 009 closure contract is internally inconsistent."""


DEPENDENCIES = ("002-public-source-acquisition", "008-semantic-backbone")
REQUIRED_ISSUES = {"EPI-MED-01", "EPI-MED-02", "GOV-MED-01"}
EXPECTED_ASSIGNMENTS = {
    "EPI-MED-01": "Epidemiology Lead",
    "EPI-MED-02": "Epidemiology Lead",
    "GOV-MED-01": "Data Governance Lead",
}
FALSE_CLAIMS = {
    "empirical_parameter_activation",
    "epidemiology_approval",
    "data_governance_approval",
    "engineering_approval",
    "contract_frozen",
    "track_complete",
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise Track009ReadinessError(f"cannot hash {path}: {exc}") from exc


def _repository_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise Track009ReadinessError("Track 009 evidence path is missing")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise Track009ReadinessError(
            f"Track 009 evidence path escapes repository: {value}"
        ) from exc
    return candidate


def _load(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise Track009ReadinessError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track009ReadinessError(f"{path} must contain a mapping")
    return value


def _metadata(root: Path, track: str) -> dict[str, Any]:
    candidates = [
        root / "conductor" / "tracks" / track / "metadata.json",
        root / "conductor" / "archive" / track / "metadata.json",
    ]
    matches = [candidate for candidate in candidates if candidate.is_file()]
    if len(matches) != 1:
        raise Track009ReadinessError(
            f"track {track} must resolve to exactly one metadata file; found {len(matches)}"
        )
    path = matches[0]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track009ReadinessError(f"cannot read metadata {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track009ReadinessError(f"metadata {path} must be an object")
    return value


def validate(path: Path, root: Path) -> None:
    document = _load(path)
    if (
        document.get("schema_version") != "1.0.0"
        or document.get("track") != "009-evidence-parameter-ledger"
    ):
        raise Track009ReadinessError("unexpected Track 009 readiness identity")
    if document.get("candidate_contract") != "v0.4" or document.get("freeze_order_position") != 2:
        raise Track009ReadinessError("Track 009 must remain second in the v0.4 freeze order")

    track_metadata = _metadata(root, "009-evidence-parameter-ledger")
    if document.get("status") != track_metadata.get("status"):
        raise Track009ReadinessError("readiness status must match Track 009 metadata")
    dependencies = document.get("upstream_dependencies")
    if not isinstance(dependencies, list) or [row.get("track") for row in dependencies] != list(
        DEPENDENCIES
    ):
        raise Track009ReadinessError("both ordered upstream dependencies are required")
    for row in dependencies:
        observed = _metadata(root, row["track"]).get("status")
        if row.get("required_status") != "complete" or row.get("observed_status") != observed:
            raise Track009ReadinessError(f"dependency state drift for {row['track']}")
        expected_state = "satisfied" if observed in {"complete", "archived"} else "pending"
        if row.get("state") != expected_state:
            raise Track009ReadinessError(f"dependency gate state mismatch for {row['track']}")

    reconciliation = document.get("upstream_contract_reconciliation", {})
    if (
        reconciliation.get("status") != "owner_decision_required"
        or reconciliation.get("recommended_option") != "A"
        or reconciliation.get("owner_decision_state") != "pending"
        or reconciliation.get("effect")
        != "none_until_owner_selects_an_option_for_this_exact_upstream_freeze"
        or not COMMIT.fullmatch(str(reconciliation.get("freeze_recording_commit", "")))
        or not COMMIT.fullmatch(str(reconciliation.get("freeze_recording_tree", "")))
    ):
        raise Track009ReadinessError(
            "upstream contract reconciliation must remain exact and pending"
        )
    for path_field, hash_field in (
        ("track_008_freeze_receipt", "track_008_freeze_receipt_sha256"),
        ("decision_packet", "decision_packet_sha256"),
    ):
        evidence_path = _repository_path(root, reconciliation.get(path_field))
        expected = str(reconciliation.get(hash_field, ""))
        if not SHA256.fullmatch(expected) or _sha256(evidence_path) != expected:
            raise Track009ReadinessError(
                f"upstream reconciliation evidence hash drift: {path_field}"
            )
    upstream_receipt = _load(_repository_path(root, reconciliation.get("track_008_freeze_receipt")))
    if (
        upstream_receipt.get("freeze_status") != "frozen_bounded_provisional_non_clinical"
        or upstream_receipt.get("claims", {}).get("contract_frozen") is not True
        or upstream_receipt.get("claims", {}).get("track_complete") is not False
    ):
        raise Track009ReadinessError("Track 008 receipt does not preserve bounded freeze state")
    decision_packet = _load(_repository_path(root, reconciliation.get("decision_packet")))
    if (
        decision_packet.get("track") != "009-evidence-parameter-ledger"
        or decision_packet.get("recommendation", {}).get("option_id") != "A"
        or decision_packet.get("owner_decision", {}).get("status") != "pending"
        or decision_packet.get("upstream_evidence", {}).get("freeze_receipt_sha256")
        != reconciliation.get("track_008_freeze_receipt_sha256")
    ):
        raise Track009ReadinessError("Track 009 upstream decision packet identity or state drift")

    issues = document.get("blocking_data_contract_issues")
    if not isinstance(issues, list) or {row.get("id") for row in issues} != REQUIRED_ISSUES:
        raise Track009ReadinessError("all three bounded-review issues must remain explicit")
    if any(row.get("assigned_role") != EXPECTED_ASSIGNMENTS[row["id"]] for row in issues):
        raise Track009ReadinessError("every blocking issue must have an accountable role")
    if any(row.get("status") not in {"assigned_pending_evidence", "resolved"} for row in issues):
        raise Track009ReadinessError("blocking issue has unsupported status")
    if any(row.get("status") == "resolved" and not row.get("receipt") for row in issues):
        raise Track009ReadinessError("resolved blocking issue requires a receipt")

    governance = document.get("governance", {})
    if governance.get("repository_panel_output") != "advisory":
        raise Track009ReadinessError("repository panel output must remain advisory")
    if governance.get("owner_disposition") != "owner_operated_not_independent_review":
        raise Track009ReadinessError("owner disposition cannot be independent review")
    claims = document.get("claims", {})
    if any(claims.get(name) is not False for name in FALSE_CLAIMS):
        raise Track009ReadinessError("blocked Track 009 claims must remain false")

    freeze = document.get("contract_freeze_gate", {})
    if freeze.get("state") == "satisfied":
        if not COMMIT.fullmatch(str(freeze.get("exact_candidate_commit", ""))):
            raise Track009ReadinessError("freeze requires an exact 40-character candidate commit")
        for field in ("ledger_export_sha256", "source_semantic_transformation_manifest_sha256"):
            if not SHA256.fullmatch(str(freeze.get(field, ""))):
                raise Track009ReadinessError(f"freeze requires an exact SHA-256 for {field}")
        required = (
            "schema_and_migration_receipt",
            "unresolved_issue_disposition",
            "accountable_freeze_decision",
        )
        if not freeze.get("blocking_findings_resolved") or any(
            not freeze.get(field) for field in required
        ):
            raise Track009ReadinessError(
                "freeze requires resolved findings and accountable evidence"
            )
    elif freeze.get("state") != "pending":
        raise Track009ReadinessError("freeze gate state must be pending or satisfied")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("readiness", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.readiness.resolve(), args.root.resolve())
    except Track009ReadinessError as exc:
        print(f"Track 009 freeze readiness failed: {exc}")
        return 1
    print(
        "Track 009 readiness passed; review decisions and v0.4 ledger freeze "
        "remain separate accountable gates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
