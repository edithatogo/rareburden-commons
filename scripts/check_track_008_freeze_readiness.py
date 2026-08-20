#!/usr/bin/env python3
"""Validate Track 008 freeze readiness without granting approval or freezing contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
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


def _git_bytes(root: Path, revision: str, path: str) -> bytes:
    try:
        return subprocess.run(
            ["git", "show", f"{revision}:{path}"],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Track008ReadinessError(
            f"cannot resolve declared Git object {revision}:{path}"
        ) from exc


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
        raise Track008ReadinessError(f"cannot resolve declared Git revision {revision}") from exc


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
    source_commit = str(binding["source_commit"])
    if _git_text(root, f"{source_commit}^{{tree}}") != binding.get("source_tree"):
        raise Track008ReadinessError("declared source tree does not belong to source commit")
    if manifest.get("candidate_status") != "provisional_synthetic_public_only":
        raise Track008ReadinessError("provisional candidate status is unsafe")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise Track008ReadinessError("provisional candidate artifact inventory is empty")
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise Track008ReadinessError("provisional candidate artifact is invalid")
        artifact_path = artifact.get("path")
        expected_hash = artifact.get("sha256")
        if _sha256(_repository_path(root, artifact_path)) != expected_hash:
            raise Track008ReadinessError("provisional candidate artifact hash drift")
        if (
            hashlib.sha256(_git_bytes(root, source_commit, str(artifact_path))).hexdigest()
            != expected_hash
        ):
            raise Track008ReadinessError("declared Git artifact hash drift")

    try:
        migration = json.loads(
            _repository_path(root, binding["migration_impact_receipt"]).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track008ReadinessError(f"cannot read migration impact receipt: {exc}") from exc
    if (
        migration.get("comparison") != "self-baseline drift check"
        or migration.get("previous_fingerprint") != manifest.get("mapping_fingerprint")
        or migration.get("current_fingerprint") != manifest.get("mapping_fingerprint")
        or migration.get("interpretation")
        != (
            "The bound synthetic mapping has no drift against its own baseline. "
            "This is not an ontology-update assessment or approval receipt."
        )
    ):
        raise Track008ReadinessError(
            "migration receipt must remain an explicit self-baseline-only check"
        )
    freeze = document.get("contract_freeze_gate", {})
    if freeze.get("state") == "satisfied":
        if not COMMIT.fullmatch(str(freeze.get("exact_candidate_commit", ""))):
            raise Track008ReadinessError("freeze requires an exact 40-character candidate commit")
        if not SHA256.fullmatch(str(freeze.get("semantic_manifest_sha256", ""))):
            raise Track008ReadinessError("freeze requires an exact semantic manifest SHA-256")
        if not freeze.get("blocking_findings_resolved") or not freeze.get(
            "accountable_freeze_decision"
        ):
            raise Track008ReadinessError(
                "freeze requires resolved findings and accountable decision"
            )
    elif freeze.get("state") != "pending":
        raise Track008ReadinessError("freeze gate state must be pending or satisfied")


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
        "Track 008 readiness passed; approval, independent review and v0.4 freeze "
        "remain separate gates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
