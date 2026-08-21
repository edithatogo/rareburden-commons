#!/usr/bin/env python3
"""Validate Track 010 alpha readiness without approving or freezing interfaces."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml


class Track010ReadinessError(ValueError):
    """Raised when the Track 010 alpha-readiness contract is inconsistent."""


FALSE_CLAIMS = {
    "scientific_approval",
    "engineering_approval",
    "patient_community_approval",
    "independent_review",
    "alpha_interface_frozen",
    "empirical_or_production_activation",
    "track_complete",
}
REVIEW_RECEIPTS = {
    "scientific_statistical_receipt",
    "engineering_receipt",
    "patient_community_receipt",
    "independent_scientific_software_receipt",
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise Track010ReadinessError(f"cannot hash {path}: {exc}") from exc


def _repository_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise Track010ReadinessError("Track 010 evidence path is missing")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise Track010ReadinessError(
            f"Track 010 evidence path escapes repository: {value}"
        ) from exc
    return candidate


def _load(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise Track010ReadinessError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track010ReadinessError(f"{path} must contain a mapping")
    return value


def _status(root: Path, track: str) -> str:
    path = root / "conductor" / "tracks" / track / "metadata.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track010ReadinessError(f"cannot read metadata {path}: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("status"), str):
        raise Track010ReadinessError(f"metadata {path} has no status")
    return value["status"]


def validate(path: Path, root: Path) -> None:
    document = _load(path)
    if (
        document.get("schema_version") != "1.0.0"
        or document.get("track") != "010-public-burden-engine"
    ):
        raise Track010ReadinessError("unexpected Track 010 readiness identity")
    if document.get("candidate_interface") != "alpha" or document.get("freeze_order_position") != 3:
        raise Track010ReadinessError("Track 010 must remain third in the serial freeze order")
    if document.get("status") != _status(root, "010-public-burden-engine"):
        raise Track010ReadinessError("readiness status must match Track 010 metadata")

    dependency = document.get("upstream_dependency", {})
    if dependency.get("track") != "009-evidence-parameter-ledger":
        raise Track010ReadinessError("Track 009 must remain the direct dependency")
    observed = _status(root, "009-evidence-parameter-ledger")
    if (
        dependency.get("required_status") != "complete"
        or dependency.get("observed_status") != observed
    ):
        raise Track010ReadinessError("Track 009 dependency state drift")
    expected = "satisfied" if observed == "complete" else "pending"
    if dependency.get("state") != expected:
        raise Track010ReadinessError("Track 009 dependency gate state mismatch")

    reconciliation = document.get("upstream_contract_reconciliation", {})
    if (
        reconciliation.get("status") != "owner_approved_candidate_preparation"
        or reconciliation.get("recommended_option") != "A"
        or reconciliation.get("owner_decision_state") != "recorded_option_A"
        or reconciliation.get("effect")
        != "exact_synthetic_candidate_preparation_only_no_alpha_freeze_or_activation"
        or not COMMIT.fullmatch(str(reconciliation.get("freeze_recording_commit", "")))
        or not COMMIT.fullmatch(str(reconciliation.get("freeze_recording_tree", "")))
    ):
        raise Track010ReadinessError(
            "upstream contract reconciliation must remain exact and recorded"
        )
    for path_field, hash_field in (
        ("track_009_freeze_receipt", "track_009_freeze_receipt_sha256"),
        ("decision_packet", "decision_packet_sha256"),
    ):
        evidence_path = _repository_path(root, reconciliation.get(path_field))
        expected_hash = str(reconciliation.get(hash_field, ""))
        if not SHA256.fullmatch(expected_hash) or _sha256(evidence_path) != expected_hash:
            raise Track010ReadinessError(
                f"upstream reconciliation evidence hash drift: {path_field}"
            )
    upstream_receipt = _load(_repository_path(root, reconciliation.get("track_009_freeze_receipt")))
    if (
        upstream_receipt.get("freeze_status") != "frozen_synthetic_non_empirical"
        or upstream_receipt.get("scope", {}).get("empirical_parameter_count") != 0
        or upstream_receipt.get("claims", {}).get("contract_frozen") is not True
        or upstream_receipt.get("claims", {}).get("track_complete") is not False
    ):
        raise Track010ReadinessError("Track 009 receipt does not preserve synthetic freeze state")
    decision_packet = _load(_repository_path(root, reconciliation.get("decision_packet")))
    if (
        decision_packet.get("track") != "010-public-burden-engine"
        or decision_packet.get("recommendation", {}).get("option_id") != "A"
        or decision_packet.get("owner_decision", {}).get("status") != "recorded"
        or decision_packet.get("owner_decision", {}).get("selected_option_id") != "A"
        or decision_packet.get("owner_decision", {}).get("decided_by") != "edithatogo"
        or decision_packet.get("upstream_evidence", {}).get("freeze_receipt_sha256")
        != reconciliation.get("track_009_freeze_receipt_sha256")
    ):
        raise Track010ReadinessError("Track 010 upstream decision packet identity or state drift")

    candidate_binding = document.get("alpha_candidate_binding", {})
    if (
        candidate_binding.get("status") != "prepared_not_frozen"
        or candidate_binding.get("effect")
        != "candidate_preparation_only_no_alpha_freeze_track_003_or_production_activation"
        or candidate_binding.get("empirical_parameter_count") != 0
        or not COMMIT.fullmatch(str(candidate_binding.get("preparation_source_commit", "")))
        or not COMMIT.fullmatch(str(candidate_binding.get("preparation_source_tree", "")))
    ):
        raise Track010ReadinessError("alpha candidate scope or revision binding drift")
    for path_field, hash_field in (
        ("candidate_manifest", "candidate_manifest_sha256"),
        ("engine_manifest", "engine_manifest_sha256"),
        ("track_009_ledger_receipt", "track_009_ledger_receipt_sha256"),
        ("track_003_interface_manifest", "track_003_interface_manifest_sha256"),
        (
            "compatibility_and_migration_receipt",
            "compatibility_and_migration_receipt_sha256",
        ),
        (
            "benchmark_and_reproducibility_receipt",
            "benchmark_and_reproducibility_receipt_sha256",
        ),
        ("challenge_findings", "challenge_findings_sha256"),
    ):
        evidence_path = _repository_path(root, candidate_binding.get(path_field))
        expected_hash = str(candidate_binding.get(hash_field, ""))
        if not SHA256.fullmatch(expected_hash) or _sha256(evidence_path) != expected_hash:
            raise Track010ReadinessError(f"alpha candidate evidence hash drift: {path_field}")
    try:
        candidate = json.loads(
            _repository_path(root, candidate_binding.get("candidate_manifest")).read_text(
                encoding="utf-8"
            )
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track010ReadinessError(f"cannot read alpha candidate manifest: {exc}") from exc
    if (
        candidate.get("candidate_status") != "prepared_not_frozen"
        or candidate.get("track_009_ledger_binding", {}).get("empirical_parameter_count") != 0
        or candidate.get("engine_manifest", {}).get("sha256")
        != candidate_binding.get("engine_manifest_sha256")
        or candidate.get("claims", {}).get("alpha_interface_frozen") is not False
        or candidate.get("claims", {}).get("empirical_or_production_activation") is not False
        or candidate.get("claims", {}).get("track_003_activated") is not False
        or candidate.get("claims", {}).get("track_complete") is not False
    ):
        raise Track010ReadinessError("alpha candidate identity, scope or claims drift")

    review = document.get("review_gate", {})
    if review.get("repository_panel_status") != "advisory":
        raise Track010ReadinessError("repository panel output must remain advisory")
    if review.get("owner_status") != "owner_operated_not_independent_review":
        raise Track010ReadinessError("owner disposition cannot be independent review")
    if review.get("state") == "satisfied" and any(not review.get(item) for item in REVIEW_RECEIPTS):
        raise Track010ReadinessError("satisfied review requires every accountable receipt")
    if review.get("state") not in {"pending", "satisfied"}:
        raise Track010ReadinessError("review gate state must be pending or satisfied")

    claims = document.get("claims", {})
    if any(claims.get(name) is not False for name in FALSE_CLAIMS):
        raise Track010ReadinessError("blocked Track 010 claims must remain false")
    freeze = document.get("alpha_freeze_gate", {})
    if freeze.get("state") == "satisfied":
        if not COMMIT.fullmatch(str(freeze.get("exact_candidate_commit", ""))):
            raise Track010ReadinessError("freeze requires an exact 40-character candidate commit")
        for field in (
            "engine_manifest_sha256",
            "track_009_ledger_manifest_sha256",
            "track_003_interface_manifest_sha256",
        ):
            if not SHA256.fullmatch(str(freeze.get(field, ""))):
                raise Track010ReadinessError(f"freeze requires an exact SHA-256 for {field}")
        required = (
            "compatibility_and_migration_receipt",
            "benchmark_and_reproducibility_receipt",
            "accountable_alpha_freeze_decision",
        )
        if review.get("state") != "satisfied" or not freeze.get("blocking_findings_resolved"):
            raise Track010ReadinessError("freeze requires satisfied review and resolved findings")
        if any(not freeze.get(field) for field in required):
            raise Track010ReadinessError(
                "freeze requires compatibility, assurance and decision evidence"
            )
    elif freeze.get("state") != "pending":
        raise Track010ReadinessError("freeze gate state must be pending or satisfied")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("readiness", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.readiness.resolve(), args.root.resolve())
    except Track010ReadinessError as exc:
        print(f"Track 010 alpha readiness failed: {exc}")
        return 1
    print("Track 010 readiness passed; independent review and alpha freeze remain separate gates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
