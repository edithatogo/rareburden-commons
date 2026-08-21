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
