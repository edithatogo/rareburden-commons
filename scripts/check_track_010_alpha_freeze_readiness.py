#!/usr/bin/env python3
"""Validate Track 010 alpha readiness without approving or freezing interfaces."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker, ValidationError


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
CANDIDATE_EFFECT = (
    "dormant_synthetic_preparation_only_no_dependency_satisfaction_review_"
    "alpha_freeze_or_track_003_eligibility"
)
BOUNDED_DISPOSITION_EFFECT = (
    "disposable_synthetic_pre_alpha_preparation_only_no_dependency_review_"
    "freeze_track_003_or_release_authority"
)
TRACK009_COMPLETION_DECISION = (
    "docs/decisions/2026-08-26-track-009-bounded-completion-authorization.yml"
)
TRACK009_PROHIBITED_EFFECTS = {
    "empirical_parameter_activation",
    "controlled_data_activation",
    "independent_review",
    "publication_authority",
    "release_authority",
}
TRACK010_ADVISORY_PACKET = "docs/decisions/2026-08-26-track-010-advisory-review.yml"
TRACK010_REVIEW_COMMIT = "f35fcf25a336bf6639b86a03f8ea172ab61177e2"
TRACK010_REVIEW_TREE = "d1496bdb8f3d8dca0e2362ad97ed3368466a02c4"
TRACK010_CORRECTED_COMMIT = "4ef8a1118b720ad844d0ea7e62dc18a090bc92a1"
TRACK010_CORRECTED_TREE = "c9f153daa76bfe5bfa1343c6c8e91ef10529f11e"


def _load(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise Track010ReadinessError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track010ReadinessError(f"{path} must contain a mapping")
    return value


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise Track010ReadinessError(f"cannot hash {path}: {exc}") from exc


def _repository_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise Track010ReadinessError("candidate evidence path is missing")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise Track010ReadinessError("candidate evidence path escapes repository") from exc
    return candidate


def _git_tree(root: Path, commit: str) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", f"{commit}^{{tree}}"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Track010ReadinessError("cannot resolve candidate source revision") from exc


def _status(root: Path, track: str) -> str:
    path = root / "conductor" / "tracks" / track / "metadata.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track010ReadinessError(f"cannot read metadata {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track010ReadinessError(f"metadata {path} has no status")
    status = value.get("status")
    if not isinstance(status, str):
        raise Track010ReadinessError(f"metadata {path} has no status")
    return status


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
    if observed == "complete":
        decision_path = _repository_path(root, dependency.get("completion_decision"))
        decision_hash = str(dependency.get("completion_decision_sha256", ""))
        if (
            dependency.get("completion_decision") != TRACK009_COMPLETION_DECISION
            or not SHA256.fullmatch(decision_hash)
            or _sha256(decision_path) != decision_hash
            or dependency.get("completion_scope")
            != "bounded synthetic and exactly-receipted public-aggregate contract only"
            or set(dependency.get("prohibited_effects", [])) != TRACK009_PROHIBITED_EFFECTS
        ):
            raise Track010ReadinessError("Track 009 bounded completion binding drift")
        completion = _load(decision_path)
        completion_claims = completion.get("claims", {})
        if (
            completion.get("track_id") != "009-evidence-parameter-ledger"
            or completion.get("decision_type") != "bounded_track_completion_authorization"
            or completion.get("authorization", {}).get("track_complete") is not True
            or completion_claims.get("contract_frozen") is not True
            or any(completion_claims.get(name) is not False for name in TRACK009_PROHIBITED_EFFECTS)
        ):
            raise Track010ReadinessError("Track 009 completion authority scope drift")

    candidate = document.get("synthetic_candidate_preparation", {})
    source_commit = str(candidate.get("source_commit", ""))
    source_tree = str(candidate.get("source_tree", ""))
    if (
        candidate.get("status") != "prepared_synthetic_only_not_alpha_not_frozen"
        or candidate.get("effect") != CANDIDATE_EFFECT
        or not COMMIT.fullmatch(source_commit)
        or not COMMIT.fullmatch(source_tree)
        or _git_tree(root, source_commit) != source_tree
    ):
        raise Track010ReadinessError("synthetic candidate identity or bounded effect drift")
    for path_field, hash_field in (
        ("candidate_manifest", "candidate_manifest_sha256"),
        ("compatibility_receipt", "compatibility_receipt_sha256"),
    ):
        expected_hash = str(candidate.get(hash_field, ""))
        if (
            not SHA256.fullmatch(expected_hash)
            or _sha256(_repository_path(root, candidate.get(path_field))) != expected_hash
        ):
            raise Track010ReadinessError(f"synthetic candidate evidence drift: {path_field}")
    candidate_manifest = json.loads(
        _repository_path(root, candidate.get("candidate_manifest")).read_text(encoding="utf-8")
    )
    if (
        candidate_manifest.get("candidate_status") != "prepared_synthetic_only_not_alpha_not_frozen"
        or candidate_manifest.get("source_commit") != source_commit
        or candidate_manifest.get("source_tree") != source_tree
        or any(value is not False for value in candidate_manifest.get("claims", {}).values())
    ):
        raise Track010ReadinessError("synthetic candidate claims or provenance drift")

    disposition = document.get("bounded_owner_disposition", {})
    disposition_commit = str(disposition.get("exact_candidate_commit", ""))
    disposition_tree = str(disposition.get("exact_candidate_tree", ""))
    if (
        disposition.get("status") != "authorized_disposable_synthetic_pre_alpha_only"
        or not COMMIT.fullmatch(disposition_commit)
        or not COMMIT.fullmatch(disposition_tree)
        or _git_tree(root, disposition_commit) != disposition_tree
        or disposition.get("candidate_manifest_sha256")
        != candidate.get("candidate_manifest_sha256")
        or disposition.get("selected_option") != "A"
        or disposition.get("authority") != "repository_owner_sole_accountable_human"
        or disposition.get("governance_status") != "owner_operated_not_independent_review"
        or disposition.get("effect") != BOUNDED_DISPOSITION_EFFECT
    ):
        raise Track010ReadinessError("bounded owner disposition scope or candidate drift")
    decision_path = _repository_path(root, disposition.get("decision"))
    decision_sha256 = str(disposition.get("decision_sha256", ""))
    if not SHA256.fullmatch(decision_sha256) or _sha256(decision_path) != decision_sha256:
        raise Track010ReadinessError("bounded owner disposition receipt hash drift")
    decision = _load(decision_path)
    owner_decision = decision.get("owner_decision", {})
    if (
        decision.get("simulation_status") != "simulated_role_separated_advisory_panel"
        or decision.get("candidate", {}).get("commit") != disposition_commit
        or decision.get("candidate", {}).get("tree") != disposition_tree
        or decision.get("candidate", {}).get("evidence_manifest_sha256")
        != disposition.get("candidate_manifest_sha256")
        or owner_decision.get("status") != "recorded"
        or owner_decision.get("selected_option_id") != "A"
        or owner_decision.get("decided_by") != "edithatogo"
    ):
        raise Track010ReadinessError("bounded owner disposition receipt overstates authority")

    corrected = document.get("corrected_post_dependency_candidate", {})
    if (
        corrected.get("status") != "prepared_bounded_post_dependency_not_alpha_not_frozen"
        or corrected.get("source_commit") != TRACK010_CORRECTED_COMMIT
        or corrected.get("source_tree") != TRACK010_CORRECTED_TREE
        or _git_tree(root, TRACK010_CORRECTED_COMMIT) != TRACK010_CORRECTED_TREE
        or corrected.get("review_status") != "implemented_pending_role_separated_re_review"
    ):
        raise Track010ReadinessError("corrected post-dependency candidate identity drift")
    for path_field, hash_field in (
        ("candidate_manifest", "candidate_manifest_sha256"),
        ("compatibility_receipt", "compatibility_receipt_sha256"),
        ("engine_receipt", "engine_receipt_sha256"),
    ):
        expected_hash = str(corrected.get(hash_field, ""))
        if (
            not SHA256.fullmatch(expected_hash)
            or _sha256(_repository_path(root, corrected.get(path_field))) != expected_hash
        ):
            raise Track010ReadinessError(f"corrected candidate evidence drift: {path_field}")

    review = document.get("review_gate", {})
    if review.get("repository_panel_status") != "advisory":
        raise Track010ReadinessError("repository panel output must remain advisory")
    if review.get("owner_status") != "owner_operated_not_independent_review":
        raise Track010ReadinessError("owner disposition cannot be independent review")
    if review.get("state") == "satisfied" and any(not review.get(item) for item in REVIEW_RECEIPTS):
        raise Track010ReadinessError("satisfied review requires every accountable receipt")
    if review.get("state") not in {"pending", "satisfied"}:
        raise Track010ReadinessError("review gate state must be pending or satisfied")
    advisory_path = _repository_path(root, review.get("repository_advisory_packet"))
    advisory_hash = str(review.get("repository_advisory_packet_sha256", ""))
    if (
        review.get("repository_advisory_packet") != TRACK010_ADVISORY_PACKET
        or not SHA256.fullmatch(advisory_hash)
        or _sha256(advisory_path) != advisory_hash
    ):
        raise Track010ReadinessError("repository advisory packet binding drift")
    advisory = _load(advisory_path)
    schema = json.loads(
        (root / "schemas/agent-owner-decision-packet.schema.json").read_text(encoding="utf-8")
    )
    try:
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(advisory)
    except ValidationError as exc:
        raise Track010ReadinessError("repository advisory packet schema drift") from exc
    if (
        advisory.get("candidate", {}).get("commit") != TRACK010_REVIEW_COMMIT
        or advisory.get("candidate", {}).get("tree") != TRACK010_REVIEW_TREE
        or _git_tree(root, TRACK010_REVIEW_COMMIT) != TRACK010_REVIEW_TREE
        or advisory.get("recommendation", {}).get("option_id") != "A"
        or advisory.get("owner_decision", {}).get("status") != "recorded"
        or advisory.get("owner_decision", {}).get("selected_option_id") != "A"
        or advisory.get("owner_decision", {}).get("decided_by") != "edithatogo"
        or review.get("repository_recommendation") != "revise"
        or review.get("repository_owner_decision") != "recorded_option_a_bounded_remediation_only"
        or review.get("remediation_status") != "implemented_pending_role_separated_re_review"
        or len(review.get("unresolved_blocking_findings", [])) < 2
    ):
        raise Track010ReadinessError("repository advisory scope or bounded decision drift")

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
    print(
        "Track 010 readiness passed; Track 009 bounded dependency is satisfied "
        "while independent review, alpha freeze and activation remain separate gates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
