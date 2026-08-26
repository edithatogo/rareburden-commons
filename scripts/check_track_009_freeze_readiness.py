#!/usr/bin/env python3
"""Validate Track 009 freeze readiness without approving or freezing ledger contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
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
OBSERVATION_EFFECT = (
    "dormant_synthetic_preparation_only_dependency_satisfied_without_activation_review_or_freeze"
)
BOUNDED_DISPOSITION_EFFECT = (
    "reversible_synthetic_preparation_and_containment_only_no_review_activation_freeze_or_release"
)
COMPLETION_DECISION = "docs/decisions/2026-08-26-track-009-bounded-completion-authorization.yml"
COMPLETION_PROHIBITED_EFFECTS = {
    "empirical_parameter_activation",
    "controlled_data_activation",
    "independent_review",
    "publication_authority",
    "release_authority",
}


def _repository_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise Track009ReadinessError("upstream evidence path is missing")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise Track009ReadinessError(f"upstream evidence path escapes repository: {value}") from exc
    return candidate


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise Track009ReadinessError(f"cannot hash {path}: {exc}") from exc


def _git_text(root: Path, revision: str) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", revision],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Track009ReadinessError(f"cannot resolve upstream revision {revision}") from exc


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
        transition = document.get("bounded_completion_transition", {})
        decision_path = _repository_path(root, transition.get("decision"))
        decision_hash = str(transition.get("decision_sha256", ""))
        if (
            document.get("status") != "blocked"
            or track_metadata.get("status") != "complete"
            or transition.get("status") != "completed_bounded_scope"
            or transition.get("decision") != COMPLETION_DECISION
            or not SHA256.fullmatch(decision_hash)
            or _sha256(decision_path) != decision_hash
            or transition.get("scope")
            != "bounded synthetic and exactly-receipted public-aggregate contract only"
            or set(transition.get("prohibited_effects", [])) != COMPLETION_PROHIBITED_EFFECTS
        ):
            raise Track009ReadinessError(
                "historical readiness status lacks bounded completion transition"
            )
        completion = _load(decision_path)
        completion_claims = completion.get("claims", {})
        if (
            completion.get("track_id") != "009-evidence-parameter-ledger"
            or completion.get("decision_type") != "bounded_track_completion_authorization"
            or completion.get("decided_by") != "edithatogo"
            or completion.get("authorization", {}).get("track_complete") is not True
            or completion_claims.get("contract_frozen") is not True
            or completion_claims.get("scope_synthetic_and_receipted_public_aggregate_only")
            is not True
            or any(
                completion_claims.get(name) is not False for name in COMPLETION_PROHIBITED_EFFECTS
            )
        ):
            raise Track009ReadinessError("bounded completion decision scope drift")
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

    observation = document.get("upstream_semantic_observation", {})
    if (
        observation.get("observation_status") != "bounded_completion_observed_dependency_satisfied"
        or observation.get("effect") != OBSERVATION_EFFECT
    ):
        raise Track009ReadinessError("Track 008 observation must remain non-activating")
    observed_commit = str(observation.get("observed_repository_commit", ""))
    observed_tree = str(observation.get("observed_repository_tree", ""))
    candidate_commit = str(observation.get("track_008_candidate_commit", ""))
    candidate_tree = str(observation.get("track_008_candidate_tree", ""))
    if any(
        not COMMIT.fullmatch(value)
        for value in (observed_commit, observed_tree, candidate_commit, candidate_tree)
    ):
        raise Track009ReadinessError("upstream observation requires exact commits and trees")
    if _git_text(root, f"{observed_commit}^{{tree}}") != observed_tree:
        raise Track009ReadinessError("observed repository tree does not belong to commit")
    evidence_fields = (
        ("track_008_owner_decision", "track_008_owner_decision_sha256"),
        ("track_008_readiness", "track_008_readiness_sha256"),
        ("advisory_and_owner_preparation", "advisory_and_owner_preparation_sha256"),
    )
    for path_field, hash_field in evidence_fields:
        expected = str(observation.get(hash_field, ""))
        if (
            not SHA256.fullmatch(expected)
            or _sha256(_repository_path(root, observation.get(path_field))) != expected
        ):
            raise Track009ReadinessError(f"upstream observation evidence drift: {path_field}")
    track_008 = _load(_repository_path(root, observation.get("track_008_readiness")))
    track_008_decision = _load(_repository_path(root, observation.get("track_008_owner_decision")))
    preparation = _load(_repository_path(root, observation.get("advisory_and_owner_preparation")))
    if (
        track_008.get("status") != "complete"
        or track_008.get("contract_freeze_gate", {}).get("state") != "satisfied"
        or track_008.get("claims", {}).get("track_complete") is not True
        or track_008.get("final_owner_disposition_candidate", {}).get("exact_candidate_commit")
        != candidate_commit
        or track_008.get("final_owner_disposition_candidate", {}).get("exact_candidate_tree")
        != candidate_tree
        or track_008_decision.get("owner_decision", {}).get("selected_option") != "A"
        or preparation.get("owner_disposition", {}).get("status")
        != "authorized_reversible_preparation_only"
    ):
        raise Track009ReadinessError("upstream observation overstates Track 008 or owner authority")
    if observation.get("track_008_semantic_manifest_sha256") != track_008.get(
        "contract_freeze_gate", {}
    ).get("semantic_manifest_sha256"):
        raise Track009ReadinessError("Track 008 semantic manifest binding drift")

    candidate = document.get("v0_4_candidate_preparation", {})
    if (
        candidate.get("status") != "prepared_synthetic_only_not_frozen"
        or candidate.get("effect")
        != "exact_synthetic_review_preparation_only_no_activation_review_or_freeze"
    ):
        raise Track009ReadinessError("v0.4 candidate must remain synthetic preparation only")
    candidate_commit = str(candidate.get("source_commit", ""))
    candidate_tree = str(candidate.get("source_tree", ""))
    if (
        not COMMIT.fullmatch(candidate_commit)
        or not COMMIT.fullmatch(candidate_tree)
        or _git_text(root, f"{candidate_commit}^{{tree}}") != candidate_tree
    ):
        raise Track009ReadinessError("v0.4 candidate source commit and tree drift")
    for path_field, hash_field in (
        ("candidate_manifest", "candidate_manifest_sha256"),
        ("migration_impact_receipt", "migration_impact_sha256"),
        ("review_preparation", "review_preparation_sha256"),
    ):
        expected = str(candidate.get(hash_field, ""))
        if (
            not SHA256.fullmatch(expected)
            or _sha256(_repository_path(root, candidate.get(path_field))) != expected
        ):
            raise Track009ReadinessError(f"v0.4 candidate evidence drift: {path_field}")
    candidate_manifest = json.loads(
        _repository_path(root, candidate.get("candidate_manifest")).read_text(encoding="utf-8")
    )
    if (
        candidate_manifest.get("candidate_status") != "prepared_synthetic_only_not_frozen"
        or candidate_manifest.get("source_commit") != candidate_commit
        or candidate_manifest.get("source_tree") != candidate_tree
        or any(value is not False for value in candidate_manifest.get("claims", {}).values())
    ):
        raise Track009ReadinessError("v0.4 candidate identity or blocked claims drift")
    for artifact in candidate_manifest.get("exports", []):
        if _sha256(_repository_path(root, artifact.get("path"))) != artifact.get("sha256"):
            raise Track009ReadinessError("v0.4 candidate export hash drift")

    disposition = document.get("bounded_owner_disposition", {})
    decision_path = _repository_path(root, disposition.get("decision"))
    if (
        disposition.get("status") != "authorized_bounded_synthetic_preparation_only"
        or disposition.get("exact_candidate_commit") != "a9ef5b1ffdba55a0d45faf670d8679d890e414d6"
        or disposition.get("exact_candidate_tree") != "6fa0fd46a54db0970ba04611f6cf90443525b9b7"
        or disposition.get("candidate_manifest_sha256")
        != candidate.get("candidate_manifest_sha256")
        or disposition.get("selected_option") != "A"
        or disposition.get("authority") != "repository_owner_sole_accountable_human"
        or disposition.get("governance_status") != "owner_operated_not_independent_review"
        or disposition.get("effect") != BOUNDED_DISPOSITION_EFFECT
    ):
        raise Track009ReadinessError("bounded owner disposition scope or candidate drift")
    decision_sha256 = str(disposition.get("decision_sha256", ""))
    if not SHA256.fullmatch(decision_sha256) or _sha256(decision_path) != decision_sha256:
        raise Track009ReadinessError("bounded owner disposition receipt hash drift")
    decision = _load(decision_path)
    owner_decision = decision.get("owner_decision", {})
    if (
        decision.get("simulation_status") != "simulated_role_separated_advisory_panel"
        or decision.get("candidate", {}).get("commit") != disposition.get("exact_candidate_commit")
        or decision.get("candidate", {}).get("tree") != disposition.get("exact_candidate_tree")
        or owner_decision.get("status") != "recorded"
        or owner_decision.get("selected_option_id") != "A"
        or owner_decision.get("decided_by") != "edithatogo"
    ):
        raise Track009ReadinessError("bounded owner disposition receipt overstates authority")

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
        "Track 009 readiness passed; historical preparation remains bounded and "
        "empirical, controlled-data, independent-review, publication and release "
        "gates remain false."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
