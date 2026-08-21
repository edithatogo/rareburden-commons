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
        reconciliation.get("status") != "owner_approved_candidate_preparation"
        or reconciliation.get("recommended_option") != "A"
        or reconciliation.get("owner_decision_state") != "recorded_option_A"
        or reconciliation.get("effect")
        != "exact_candidate_preparation_only_no_freeze_or_empirical_activation"
        or not COMMIT.fullmatch(str(reconciliation.get("freeze_recording_commit", "")))
        or not COMMIT.fullmatch(str(reconciliation.get("freeze_recording_tree", "")))
    ):
        raise Track009ReadinessError(
            "upstream contract reconciliation must remain exact and recorded"
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
        or decision_packet.get("owner_decision", {}).get("status") != "recorded"
        or decision_packet.get("owner_decision", {}).get("selected_option_id") != "A"
        or decision_packet.get("owner_decision", {}).get("decided_by") != "edithatogo"
        or decision_packet.get("upstream_evidence", {}).get("freeze_receipt_sha256")
        != reconciliation.get("track_008_freeze_receipt_sha256")
    ):
        raise Track009ReadinessError("Track 009 upstream decision packet identity or state drift")

    candidate_binding = document.get("v0_4_candidate_binding", {})
    if (
        candidate_binding.get("status") != "prepared_not_frozen"
        or candidate_binding.get("effect")
        != "candidate_preparation_only_no_contract_freeze_or_track_completion"
        or candidate_binding.get("parameter_count") != 2
        or candidate_binding.get("empirical_parameter_count") != 0
        or not COMMIT.fullmatch(str(candidate_binding.get("preparation_source_commit", "")))
        or not COMMIT.fullmatch(str(candidate_binding.get("preparation_source_tree", "")))
    ):
        raise Track009ReadinessError("v0.4 ledger candidate scope or revision binding drift")
    for path_field, hash_field in (
        ("candidate_manifest", "candidate_manifest_sha256"),
        ("ledger_export", "ledger_export_sha256"),
        ("schema_and_migration_receipt", "schema_and_migration_receipt_sha256"),
        (
            "source_semantic_transformation_bindings",
            "source_semantic_transformation_bindings_sha256",
        ),
        ("challenge_findings", "challenge_findings_sha256"),
    ):
        evidence_path = _repository_path(root, candidate_binding.get(path_field))
        expected = str(candidate_binding.get(hash_field, ""))
        if not SHA256.fullmatch(expected) or _sha256(evidence_path) != expected:
            raise Track009ReadinessError(f"v0.4 ledger candidate evidence hash drift: {path_field}")
    try:
        candidate = json.loads(
            _repository_path(root, candidate_binding.get("candidate_manifest")).read_text(
                encoding="utf-8"
            )
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track009ReadinessError(f"cannot read v0.4 ledger candidate manifest: {exc}") from exc
    if (
        candidate.get("candidate_status") != "prepared_not_frozen"
        or candidate.get("ledger_export", {}).get("sha256")
        != candidate_binding.get("ledger_export_sha256")
        or candidate.get("ledger_export", {}).get("empirical_parameter_count") != 0
        or candidate.get("claims", {}).get("contract_frozen") is not False
        or candidate.get("claims", {}).get("track_complete") is not False
    ):
        raise Track009ReadinessError("v0.4 ledger candidate identity, scope or claims drift")

    disposition = document.get("final_owner_disposition_candidate", {})
    if (
        disposition.get("exact_candidate_commit") != "55f58f7b5f7522fa9b988c4e57dc967969cca7b7"
        or disposition.get("exact_candidate_tree") != "59c720c68ccbe91c35dc2e3b07900a68a76b6431"
        or disposition.get("recommended_option") != "A"
        or disposition.get("owner_decision_state") != "recorded_option_A"
        or disposition.get("effect")
        != "authorizes_exact_synthetic_non_empirical_contract_freeze_only"
    ):
        raise Track009ReadinessError("final Track 009 disposition must remain exact and recorded")
    disposition_path = _repository_path(root, disposition.get("decision_packet"))
    disposition_hash = str(disposition.get("decision_packet_sha256", ""))
    if not SHA256.fullmatch(disposition_hash) or _sha256(disposition_path) != disposition_hash:
        raise Track009ReadinessError("final Track 009 disposition packet hash drift")
    disposition_packet = _load(disposition_path)
    if (
        disposition_packet.get("candidate", {}).get("commit")
        != disposition.get("exact_candidate_commit")
        or disposition_packet.get("candidate", {}).get("tree")
        != disposition.get("exact_candidate_tree")
        or disposition_packet.get("candidate", {}).get("manifest_sha256")
        != candidate_binding.get("candidate_manifest_sha256")
        or disposition_packet.get("recommendation", {}).get("option_id") != "A"
        or disposition_packet.get("owner_decision", {}).get("status") != "recorded"
        or disposition_packet.get("owner_decision", {}).get("selected_option_id") != "A"
        or disposition_packet.get("owner_decision", {}).get("decided_by") != "edithatogo"
    ):
        raise Track009ReadinessError("final Track 009 disposition identity or state drift")

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
        if (
            freeze.get("exact_candidate_commit") != disposition.get("exact_candidate_commit")
            or freeze.get("exact_candidate_tree") != disposition.get("exact_candidate_tree")
            or freeze.get("ledger_export_sha256") != candidate_binding.get("ledger_export_sha256")
            or freeze.get("source_semantic_transformation_manifest_sha256")
            != candidate_binding.get("source_semantic_transformation_bindings_sha256")
        ):
            raise Track009ReadinessError("freeze candidate or artifact binding drift")
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
        if (
            freeze.get("resolution_scope") != "synthetic_non_empirical_contract_only"
            or freeze.get("unresolved_issue_disposition")
            != "remain_open_and_blocking_for_any_empirical_expansion"
            or freeze.get("accountable_freeze_decision") != disposition.get("decision_packet")
        ):
            raise Track009ReadinessError("freeze scope or residual issue disposition drift")
        for path_field, hash_field in (
            ("schema_and_migration_receipt", "schema_and_migration_receipt_sha256"),
            ("freeze_receipt", "freeze_receipt_sha256"),
        ):
            evidence_path = _repository_path(root, freeze.get(path_field))
            expected = str(freeze.get(hash_field, ""))
            if not SHA256.fullmatch(expected) or _sha256(evidence_path) != expected:
                raise Track009ReadinessError(f"freeze evidence hash drift: {path_field}")
        receipt = _load(_repository_path(root, freeze.get("freeze_receipt")))
        if (
            receipt.get("freeze_status") != "frozen_synthetic_non_empirical"
            or receipt.get("candidate", {}).get("commit") != freeze.get("exact_candidate_commit")
            or receipt.get("candidate", {}).get("tree") != freeze.get("exact_candidate_tree")
            or receipt.get("candidate", {}).get("ledger_export_sha256")
            != freeze.get("ledger_export_sha256")
            or receipt.get("owner_decision", {}).get("sha256") != disposition_hash
            or receipt.get("scope", {}).get("empirical_parameter_count") != 0
            or receipt.get("claims", {}).get("empirical_parameter_activation") is not False
            or receipt.get("claims", {}).get("track_complete") is not False
        ):
            raise Track009ReadinessError("freeze receipt identity, scope or claims drift")
    elif freeze.get("state") != "pending":
        raise Track009ReadinessError("freeze gate state must be pending or satisfied")
    if claims.get("contract_frozen") is not (freeze.get("state") == "satisfied"):
        raise Track009ReadinessError("contract-frozen claim must match the freeze gate")


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
        "Track 009 readiness passed; the synthetic non-empirical v0.4 freeze is "
        "internally consistent and empirical activation remains separately blocked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
