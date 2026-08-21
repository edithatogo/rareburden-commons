#!/usr/bin/env python3
"""Validate the prospective Track 008A/008B split without activating it."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml


class Track008SplitError(ValueError):
    """Raised when the split candidate weakens a fail-closed boundary."""


BASELINE_FILES = {
    "track_008_spec_sha256": "conductor/tracks/008-semantic-backbone/spec.md",
    "track_008_plan_sha256": "conductor/tracks/008-semantic-backbone/plan.md",
    "track_008_metadata_sha256": "conductor/tracks/008-semantic-backbone/metadata.json",
    "track_008_readiness_sha256": "docs/track-008-freeze-readiness-2026-08-21.yml",
    "track_008_final_disposition_sha256": (
        "docs/decisions/2026-08-21-track-008-v0.4-final-disposition.yml"
    ),
    "track_009_metadata_sha256": "conductor/tracks/009-evidence-parameter-ledger/metadata.json",
    "track_009_readiness_sha256": "docs/track-009-freeze-readiness-2026-08-21.yml",
}
REQUIRED_TRANSFERS = {
    "pinned extended source families",
    "patient/community naming and aggregation review",
    "clinical mapping-fitness review",
    "independent semantic review",
    "bounded non-clinical schemas, mappings, hierarchy and migration",
}
FALSE_CLAIMS = {
    "track_008a_complete",
    "track_008b_complete",
    "track_009_unblocked",
    "scope_change_approved",
    "clinical_validation",
    "patient_community_authority",
    "derivative_publication_rights_complete",
    "independent_review",
}


def _mapping(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise Track008SplitError(f"cannot read split candidate {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track008SplitError("split candidate must be a mapping")
    return value


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise Track008SplitError(f"cannot hash baseline file {path}: {exc}") from exc


def _metadata(root: Path, track: str) -> dict[str, Any]:
    path = root / "conductor" / "tracks" / track / "metadata.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track008SplitError(f"cannot read track metadata {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track008SplitError(f"track metadata must be an object: {path}")
    return value


def _git(root: Path, revision: str) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", revision],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Track008SplitError(f"cannot resolve baseline revision {revision}") from exc


def validate(candidate_path: Path, root: Path) -> None:
    """Validate exact binding, prospective scope, and unchanged dependency state."""
    candidate = _mapping(candidate_path)
    if candidate.get("schema_version") != "1.0.0":
        raise Track008SplitError("schema_version must be 1.0.0")
    if candidate.get("status") != "prospective_scope_change_candidate_preparation_only":
        raise Track008SplitError("candidate must remain preparation only")

    authorization = candidate.get("owner_authorization")
    if not isinstance(authorization, dict) or authorization.get("authorized_action") != (
        "prepare_scope_change_candidate_and_dependency_analysis"
    ):
        raise Track008SplitError("owner authorization must remain preparation-only")
    prohibited = set(authorization.get("prohibited_effects", []))
    if not {
        "mark_track_008a_complete",
        "mark_track_008b_complete",
        "unblock_or_activate_track_009",
        "infer_final_owner_disposition",
    }.issubset(prohibited):
        raise Track008SplitError("owner authorization is missing prohibited effects")

    baseline = candidate.get("baseline")
    if not isinstance(baseline, dict):
        raise Track008SplitError("baseline must be a mapping")
    commit = str(baseline.get("repository_commit", ""))
    tree = str(baseline.get("repository_tree", ""))
    if _git(root, f"{commit}^{{tree}}") != tree:
        raise Track008SplitError("baseline commit does not own the declared tree")
    for field, relative in BASELINE_FILES.items():
        if baseline.get(field) != _sha256(root / relative):
            raise Track008SplitError(f"baseline hash drift: {relative}")

    tracks = candidate.get("proposed_tracks")
    if not isinstance(tracks, list) or len(tracks) != 2:
        raise Track008SplitError("exactly two proposed tracks are required")
    by_alias = {row.get("alias"): row for row in tracks if isinstance(row, dict)}
    if set(by_alias) != {"008A", "008B"}:
        raise Track008SplitError("proposed aliases must be 008A and 008B")
    if by_alias["008A"].get("canonical_id") != "008-semantic-backbone":
        raise Track008SplitError("008A must retain the historical canonical identifier")
    if by_alias["008B"].get("canonical_id") != "019-clinical-community-semantic-assurance":
        raise Track008SplitError("008B must use the schema-compatible 019 identifier")
    if by_alias["008A"].get("candidate_state") != "blocked_pending_exact_scope_disposition":
        raise Track008SplitError("008A must remain blocked pending disposition")
    if by_alias["008B"].get("candidate_state") != "proposed_not_registered_or_active":
        raise Track008SplitError("008B must remain unregistered and inactive")

    transfers = candidate.get("transferred_requirement_register")
    if not isinstance(transfers, list):
        raise Track008SplitError("transferred requirement register must be a list")
    original_requirements = {
        row.get("original_requirement") for row in transfers if isinstance(row, dict)
    }
    if original_requirements != REQUIRED_TRANSFERS:
        raise Track008SplitError("transferred requirement register is incomplete or duplicated")

    dependency = candidate.get("dependency_analysis")
    if not isinstance(dependency, dict):
        raise Track008SplitError("dependency analysis must be a mapping")
    current = dependency.get("current_track_009")
    if not isinstance(current, dict) or current != {
        "status": "blocked",
        "dependency": "008-semantic-backbone",
        "activation": False,
    }:
        raise Track008SplitError("Track 009 current dependency state must remain blocked")
    if dependency.get("preparation_candidate_effect") != "none":
        raise Track008SplitError("preparation candidate cannot change dependencies")

    if _metadata(root, "008-semantic-backbone").get("status") != "blocked":
        raise Track008SplitError("current Track 008 metadata must remain blocked")
    track_009 = _metadata(root, "009-evidence-parameter-ledger")
    if track_009.get("status") != "blocked" or track_009.get("dependencies") != [
        "002-public-source-acquisition",
        "008-semantic-backbone",
    ]:
        raise Track008SplitError("current Track 009 metadata or dependency has changed")

    claims = candidate.get("claims")
    if not isinstance(claims, dict) or any(claims.get(name) is not False for name in FALSE_CLAIMS):
        raise Track008SplitError(
            "all completion, activation and authority claims must remain false"
        )
    next_gate = candidate.get("next_gate")
    if not isinstance(next_gate, dict) or next_gate.get("required") != (
        "new_simulated_panel_packet_and_exact_candidate_owner_disposition"
    ):
        raise Track008SplitError("the next exact panel and owner gate is required")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.candidate.resolve(), args.root.resolve())
    except Track008SplitError as exc:
        print(f"Track 008 split candidate failed: {exc}")
        return 1
    print("Track 008 split candidate passed; both tracks and Track 009 remain blocked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
