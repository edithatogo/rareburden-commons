#!/usr/bin/env python3
"""Validate Track 009 bounded completion authorization and lifecycle state."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

DECISION = Path("docs/decisions/2026-08-26-track-009-bounded-completion-authorization.yml")
FREEZE_MANIFEST = Path("manifests/ledger/track-009-v0.4-contract-freeze.json")
FREEZE_DISPOSITION = Path("docs/decisions/2026-08-22-track-009-owner-v04-freeze-disposition.yml")
PLAN = Path("conductor/tracks/009-evidence-parameter-ledger/plan.md")
METADATA = Path("conductor/tracks/009-evidence-parameter-ledger/metadata.json")
REVIEW = Path("conductor/tracks/009-evidence-parameter-ledger/review.md")
REGISTRY = Path("conductor/tracks.md")
SETUP_STATE = Path("conductor/setup_state.json")
BASELINE_COMMIT = "2ac13c0f93c95b4e1133a13790e2359d272f01da"
BASELINE_TREE = "2b8cc2387a23e68359b39c809d76459a25a7b470"
TRACK_ID = "009-evidence-parameter-ledger"


class BoundedCompletionError(ValueError):
    """The Track 009 completion authorization or lifecycle state escaped scope."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BoundedCompletionError(f"expected mapping in {path}")
    return value


def validate_authorization(root: Path) -> None:
    decision = _mapping(root / DECISION)
    candidate = decision.get("candidate", {})
    authorization = decision.get("authorization", {})
    claims = decision.get("claims", {})
    expected_claims = {
        "contract_frozen": True,
        "scope_synthetic_and_receipted_public_aggregate_only": True,
        "empirical_parameter_activation": False,
        "controlled_data_activation": False,
        "independent_review": False,
        "publication_authority": False,
        "release_authority": False,
    }
    if (
        decision.get("track_id") != TRACK_ID
        or decision.get("decision_type") != "bounded_track_completion_authorization"
        or decision.get("decided_by") != "edithatogo"
        or decision.get("accountable_role") != "repository owner and sole accountable human"
        or not isinstance(candidate, dict)
        or candidate.get("commit") != BASELINE_COMMIT
        or candidate.get("tree") != BASELINE_TREE
        or not isinstance(authorization, dict)
        or authorization.get("track_complete") is not True
        or authorization.get("scope")
        != "bounded synthetic and exactly-receipted public-aggregate contract only"
        or claims != expected_claims
    ):
        raise BoundedCompletionError("bounded owner authorization scope drift")

    for key, expected_path in (
        ("freeze_manifest", FREEZE_MANIFEST),
        ("freeze_disposition", FREEZE_DISPOSITION),
    ):
        binding = candidate.get(key, {})
        if (
            not isinstance(binding, dict)
            or binding.get("path") != expected_path.as_posix()
            or binding.get("sha256") != _sha256(root / expected_path)
        ):
            raise BoundedCompletionError(f"{key} binding drift")

    freeze_manifest = json.loads((root / FREEZE_MANIFEST).read_text(encoding="utf-8"))
    freeze_disposition = _mapping(root / FREEZE_DISPOSITION)
    for source, label in (
        (freeze_manifest, "freeze manifest"),
        (freeze_disposition, "freeze disposition"),
    ):
        source_claims = source.get("claims", {})
        if (
            source_claims.get("contract_frozen") is not True
            or source_claims.get("track_complete") is not False
            or source_claims.get("release_authority") is not False
        ):
            raise BoundedCompletionError(f"{label} authority boundary drift")


def validate_completion_state(root: Path) -> None:
    validate_authorization(root)
    plan = (root / PLAN).read_text(encoding="utf-8")
    if re.search(r"^- \[[ ~]\]", plan, flags=re.MULTILINE):
        raise BoundedCompletionError("Track 009 plan still has pending tasks")
    metadata = json.loads((root / METADATA).read_text(encoding="utf-8"))
    setup_state = json.loads((root / SETUP_STATE).read_text(encoding="utf-8"))
    registry = (root / REGISTRY).read_text(encoding="utf-8")
    review = (root / REVIEW).read_text(encoding="utf-8")
    expected_registry = (
        "| 009 | Evidence and parameter ledger | Complete "
        "(bounded synthetic and receipted-public-aggregate scope) |"
    )
    if metadata.get("status") != "complete":
        raise BoundedCompletionError("Track 009 metadata is not complete")
    if expected_registry not in registry:
        raise BoundedCompletionError("Track 009 registry completion scope drift")
    if TRACK_ID not in setup_state.get("completed_tracks", []):
        raise BoundedCompletionError("Track 009 missing from completed tracks")
    if TRACK_ID in setup_state.get("blocked_tracks", []):
        raise BoundedCompletionError("Track 009 remains in blocked tracks")
    if DECISION.as_posix() not in review:
        raise BoundedCompletionError("Track 009 review lacks completion authorization")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        if args.require_complete:
            validate_completion_state(args.root.resolve())
        else:
            validate_authorization(args.root.resolve())
    except (BoundedCompletionError, OSError, json.JSONDecodeError) as exc:
        print(f"Track 009 bounded completion failed: {exc}")
        return 1
    print(
        "Track 009 bounded completion authorization passed; empirical, "
        "controlled-data, independent-review, publication and release claims "
        "remain false."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
