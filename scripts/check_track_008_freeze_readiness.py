#!/usr/bin/env python3
"""Validate Track 008 freeze readiness without granting approval or freezing contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml


class Track008ReadinessError(ValueError):
    """Raised when the Track 008 closure contract is internally inconsistent."""


DEPENDENCIES = ("002-public-source-acquisition", "007-landscape-novelty")
REQUIRED_FINDINGS = {"SEM-MED-01", "RIGHTS-MED-01", "RIGHTS-MED-02", "NAME-MED-01"}
FALSE_CLAIMS = {
    "approved_ontology_pins",
    "naming_authority",
    "independent_semantic_review",
    "track_complete",
}
CANDIDATE_FALSE_CLAIMS = {
    "comprehensive_coverage",
    "clinical_validation",
    "patient_community_authority",
    "independent_review",
    "partnership_or_external_approval",
    "contract_frozen",
    "track_complete",
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise Track008ReadinessError(f"cannot hash {path}: {exc}") from exc


def _repository_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise Track008ReadinessError("provisional candidate path is missing")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise Track008ReadinessError(
            f"provisional candidate path escapes repository: {value}"
        ) from exc
    return candidate


def _load(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise Track008ReadinessError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track008ReadinessError(f"{path} must contain a mapping")
    return value


def _metadata(root: Path, track: str) -> dict[str, Any]:
    candidates = [
        root / "conductor" / "tracks" / track / "metadata.json",
        root / "conductor" / "archive" / track / "metadata.json",
    ]
    matches = [candidate for candidate in candidates if candidate.is_file()]
    if len(matches) != 1:
        raise Track008ReadinessError(
            f"track {track} must resolve to exactly one metadata file; found {len(matches)}"
        )
    path = matches[0]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track008ReadinessError(f"cannot read metadata {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track008ReadinessError(f"metadata {path} must be an object")
    return value


def validate(path: Path, root: Path) -> None:
    document = _load(path)
    if (
        document.get("schema_version") != "1.0.0"
        or document.get("track") != "008-semantic-backbone"
    ):
        raise Track008ReadinessError("unexpected Track 008 readiness identity")
    if document.get("candidate_contract") != "v0.4" or document.get("freeze_order_position") != 1:
        raise Track008ReadinessError("Track 008 must remain first in the v0.4 freeze order")

    track_metadata = _metadata(root, "008-semantic-backbone")
    if document.get("status") != track_metadata.get("status"):
        raise Track008ReadinessError("readiness status must match Track 008 metadata")
    dependencies = document.get("upstream_dependencies")
    if not isinstance(dependencies, list) or [row.get("track") for row in dependencies] != list(
        DEPENDENCIES
    ):
        raise Track008ReadinessError("both ordered upstream dependencies are required")
    for row in dependencies:
        observed = _metadata(root, row["track"]).get("status")
        if row.get("required_status") != "complete" or row.get("observed_status") != observed:
            raise Track008ReadinessError(f"dependency state drift for {row['track']}")
        expected_state = "satisfied" if observed in {"complete", "archived"} else "pending"
        if row.get("state") != expected_state:
            raise Track008ReadinessError(f"dependency gate state mismatch for {row['track']}")

    findings = document.get("naming_and_semantic_gate", {}).get("unresolved_findings", [])
    if {row.get("id") for row in findings if isinstance(row, dict)} != REQUIRED_FINDINGS:
        raise Track008ReadinessError("the four bounded-review findings must remain explicit")
    governance = document.get("governance", {})
    if governance.get("repository_panel_output") != "advisory":
        raise Track008ReadinessError("repository panel output must remain advisory")
    if governance.get("owner_disposition") != "owner_operated_not_independent_review":
        raise Track008ReadinessError("owner disposition cannot be independent review")

    claims = document.get("claims", {})
    if any(claims.get(name) is not False for name in FALSE_CLAIMS):
        raise Track008ReadinessError("blocked Track 008 claims must remain false")

    binding = document.get("provisional_candidate_binding", {})
    if (
        binding.get("status") != "synthetic_public_readiness_only"
        or binding.get("effect") != "none_on_approval_naming_independent_review_freeze_or_track_009"
    ):
        raise Track008ReadinessError("provisional candidate must remain readiness-only")
    if not COMMIT.fullmatch(str(binding.get("source_commit", ""))) or not COMMIT.fullmatch(
        str(binding.get("source_tree", ""))
    ):
        raise Track008ReadinessError(
            "provisional candidate requires exact commit and tree bindings"
        )
    for path_field, hash_field in (
        ("candidate_manifest", "candidate_manifest_sha256"),
        ("migration_impact_receipt", "migration_impact_sha256"),
        ("advisory_options", "advisory_options_sha256"),
    ):
        relative = binding.get(path_field)
        expected = binding.get(hash_field)
        if not isinstance(relative, str) or not SHA256.fullmatch(str(expected)):
            raise Track008ReadinessError("provisional candidate evidence binding is incomplete")
        evidence_path = _repository_path(root, relative)
        if _sha256(evidence_path) != expected:
            raise Track008ReadinessError(f"provisional candidate evidence hash drift: {relative}")

    try:
        manifest = json.loads(
            _repository_path(root, binding["candidate_manifest"]).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track008ReadinessError(f"cannot read provisional candidate manifest: {exc}") from exc
    if manifest.get("source_commit") != binding.get("source_commit") or manifest.get(
        "source_tree"
    ) != binding.get("source_tree"):
        raise Track008ReadinessError("provisional candidate revision binding drift")
    if manifest.get("candidate_status") != "provisional_synthetic_public_only":
        raise Track008ReadinessError("provisional candidate status is unsafe")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise Track008ReadinessError("provisional candidate artifact inventory is empty")
    for artifact in artifacts:
        if not isinstance(artifact, dict) or _sha256(
            _repository_path(root, artifact.get("path"))
        ) != artifact.get("sha256"):
            raise Track008ReadinessError("provisional candidate artifact hash drift")

    candidate_binding = document.get("v0_4_candidate_binding", {})
    if (
        candidate_binding.get("status") != "owner_approved_preparation_not_frozen"
        or candidate_binding.get("review_status") != "owner_operated_not_independent"
        or candidate_binding.get("effect")
        != "candidate_preparation_only_no_contract_freeze_or_track_completion"
    ):
        raise Track008ReadinessError("v0.4 candidate must remain prepared but not frozen")
    source_commit = str(candidate_binding.get("source_commit", ""))
    source_tree = str(candidate_binding.get("source_tree", ""))
    if not COMMIT.fullmatch(source_commit) or not COMMIT.fullmatch(source_tree):
        raise Track008ReadinessError("v0.4 candidate requires exact source commit and tree")
    for path_field, hash_field in (
        ("candidate_manifest", "candidate_manifest_sha256"),
        ("migration_impact_receipt", "migration_impact_sha256"),
        ("owner_preparation_decision", "owner_preparation_decision_sha256"),
        ("challenge_findings", "challenge_findings_sha256"),
    ):
        evidence_path = _repository_path(root, candidate_binding.get(path_field))
        expected = str(candidate_binding.get(hash_field, ""))
        if not SHA256.fullmatch(expected) or _sha256(evidence_path) != expected:
            raise Track008ReadinessError(f"v0.4 candidate evidence hash drift: {path_field}")

    try:
        prepared = json.loads(
            _repository_path(root, candidate_binding["candidate_manifest"]).read_text(
                encoding="utf-8"
            )
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track008ReadinessError(f"cannot read v0.4 candidate manifest: {exc}") from exc
    if (
        prepared.get("candidate_status") != "prepared_not_frozen"
        or prepared.get("source_commit") != candidate_binding.get("source_commit")
        or prepared.get("source_tree") != candidate_binding.get("source_tree")
    ):
        raise Track008ReadinessError("v0.4 candidate identity or status drift")
    if any(prepared.get("claims", {}).get(name) is not False for name in CANDIDATE_FALSE_CLAIMS):
        raise Track008ReadinessError("v0.4 candidate blocked claims must remain false")
    allowlist = prepared.get("public_source_allowlist")
    if not isinstance(allowlist, list) or [row.get("source_id") for row in allowlist] != [
        "orphadata-science-alignments",
        "mondo-disease-ontology",
        "human-phenotype-ontology",
    ]:
        raise Track008ReadinessError("v0.4 candidate source allowlist drift")
    for source in allowlist:
        assets = source.get("assets", [source])
        if not isinstance(assets, list) or not assets:
            raise Track008ReadinessError("v0.4 candidate source asset inventory is empty")
        for asset in assets:
            if not isinstance(asset, dict) or not SHA256.fullmatch(str(asset.get("sha256", ""))):
                raise Track008ReadinessError("v0.4 candidate source asset digest is invalid")
    if len(allowlist[2].get("assets", [])) != 9 or not allowlist[2].get("excluded_asset_classes"):
        raise Track008ReadinessError("HPO candidate must remain an exact nine-asset allowlist")
    derived = prepared.get("derived_candidate_artifacts")
    if not isinstance(derived, list) or len(derived) != 3:
        raise Track008ReadinessError("v0.4 derived candidate inventory is incomplete")
    for artifact in derived:
        artifact_path = _repository_path(root, artifact.get("path"))
        if not SHA256.fullmatch(str(artifact.get("sha256", ""))) or _sha256(
            artifact_path
        ) != artifact.get("sha256"):
            raise Track008ReadinessError("v0.4 derived candidate artifact hash drift")
    disposition = document.get("final_owner_disposition_candidate", {})
    if (
        not COMMIT.fullmatch(str(disposition.get("exact_candidate_commit", "")))
        or not COMMIT.fullmatch(str(disposition.get("exact_candidate_tree", "")))
        or disposition.get("recommended_option") != "A"
        or disposition.get("owner_decision_state") != "recorded_option_A"
        or disposition.get("effect") != "authorizes_exact_bounded_contract_freeze_only"
    ):
        raise Track008ReadinessError("final owner disposition must remain exact and recorded")
    decision_packet = _repository_path(root, disposition.get("decision_packet"))
    decision_hash = str(disposition.get("decision_packet_sha256", ""))
    if not SHA256.fullmatch(decision_hash) or _sha256(decision_packet) != decision_hash:
        raise Track008ReadinessError("final owner disposition packet hash drift")
    decision = _load(decision_packet)
    owner_decision = decision.get("owner_decision", {})
    if (
        decision.get("candidate", {}).get("commit") != disposition.get("exact_candidate_commit")
        or decision.get("candidate", {}).get("tree") != disposition.get("exact_candidate_tree")
        or owner_decision.get("status") != "recorded"
        or owner_decision.get("selected_option_id") != "A"
        or owner_decision.get("decided_by") != "edithatogo"
    ):
        raise Track008ReadinessError("recorded owner decision identity or candidate drift")
    freeze = document.get("contract_freeze_gate", {})
    if freeze.get("state") == "satisfied":
        if freeze.get("exact_candidate_commit") != disposition.get(
            "exact_candidate_commit"
        ) or freeze.get("exact_candidate_tree") != disposition.get("exact_candidate_tree"):
            raise Track008ReadinessError("freeze candidate revision must match the owner decision")
        if freeze.get("semantic_manifest_sha256") != candidate_binding.get(
            "candidate_manifest_sha256"
        ):
            raise Track008ReadinessError("freeze semantic manifest must match the candidate")
        if not freeze.get("blocking_findings_resolved") or not freeze.get(
            "accountable_freeze_decision"
        ):
            raise Track008ReadinessError(
                "freeze requires resolved findings and accountable decision"
            )
        if freeze.get("resolution_scope") != "bounded_provisional_non_clinical_contract_only":
            raise Track008ReadinessError("freeze finding resolution scope is too broad or missing")
        for path_field, hash_field in (
            ("migration_impact_receipt", "migration_impact_sha256"),
            ("freeze_receipt", "freeze_receipt_sha256"),
        ):
            evidence_path = _repository_path(root, freeze.get(path_field))
            expected = str(freeze.get(hash_field, ""))
            if not SHA256.fullmatch(expected) or _sha256(evidence_path) != expected:
                raise Track008ReadinessError(f"freeze evidence hash drift: {path_field}")
        if freeze.get("accountable_freeze_decision") != disposition.get("decision_packet"):
            raise Track008ReadinessError("freeze accountable decision binding drift")
        receipt = _load(_repository_path(root, freeze.get("freeze_receipt")))
        if (
            receipt.get("freeze_status") != "frozen_bounded_provisional_non_clinical"
            or receipt.get("candidate", {}).get("commit") != freeze.get("exact_candidate_commit")
            or receipt.get("candidate", {}).get("tree") != freeze.get("exact_candidate_tree")
            or receipt.get("candidate", {}).get("manifest_sha256")
            != freeze.get("semantic_manifest_sha256")
            or receipt.get("owner_decision", {}).get("sha256") != decision_hash
            or receipt.get("claims", {}).get("track_complete") is not False
        ):
            raise Track008ReadinessError("freeze receipt identity, scope or claims drift")
    elif freeze.get("state") != "pending":
        raise Track008ReadinessError("freeze gate state must be pending or satisfied")
    if claims.get("contract_frozen") is not (freeze.get("state") == "satisfied"):
        raise Track008ReadinessError("contract-frozen claim must match the freeze gate")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("readiness", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.readiness.resolve(), args.root.resolve())
    except Track008ReadinessError as exc:
        print(f"Track 008 freeze readiness failed: {exc}")
        return 1
    print(
        "Track 008 readiness passed; the bounded v0.4 contract state is internally "
        "consistent and Track completion remains a separate gate."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
