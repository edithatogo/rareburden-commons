#!/usr/bin/env python3
"""Validate the non-operative Track 008 successor implementation candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


class SuccessorCandidateError(ValueError):
    """Raised when the prepared implementation candidate weakens a gate."""


BASELINE_FILES = {
    "conductor_tracks_sha256": "conductor/tracks.md",
    "conductor_roadmap_sha256": "conductor/roadmap.yml",
    "track_008_metadata_sha256": "conductor/tracks/008-semantic-backbone/metadata.json",
    "track_009_metadata_sha256": "conductor/tracks/009-evidence-parameter-ledger/metadata.json",
}
EXPECTED_MODES = {
    "synthetic_internal_preparation",
    "exact_unmodified_source_asset_handling",
    "source_derived_use",
    "empirical_activation",
    "public_facing_semantics",
    "clinical_use",
    "patient_facing_use",
    "authority_bearing_claim",
}
HIGH_RISK_MODES = EXPECTED_MODES - {
    "synthetic_internal_preparation",
    "exact_unmodified_source_asset_handling",
}
SUCCESSORS = {
    "019-bounded-semantic-infrastructure",
    "020-clinical-community-semantic-assurance",
}
FALSE_CLAIMS = {
    "applied",
    "successor_registered",
    "track_008_complete",
    "track_019_complete",
    "track_020_complete",
    "track_009_unblocked",
    "rights_cleared",
    "clinical_validated",
    "community_authority",
    "independent_review",
}


def _load(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise SuccessorCandidateError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SuccessorCandidateError(f"document must be a mapping: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(candidate_path: Path, root: Path) -> None:
    candidate = _load(candidate_path)
    if candidate.get("status") != "prepared_not_applied":
        raise SuccessorCandidateError("candidate must remain prepared and not applied")
    if candidate.get("next_gate") != (
        "new_simulated_panel_packet_and_exact_implementation_candidate_owner_disposition"
    ):
        raise SuccessorCandidateError("exact panel and owner gate is required")

    baseline = candidate.get("live_state_baseline", {})
    for field, relative in BASELINE_FILES.items():
        if baseline.get(field) != _sha256(root / relative):
            raise SuccessorCandidateError(f"live programme state drift: {relative}")

    for relative in candidate.get("candidate_files", []):
        path = root / relative
        if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            raise SuccessorCandidateError(f"missing or unsafe candidate file: {relative}")

    metadata_rows = []
    for track in ("019", "020"):
        path = root / f"docs/candidates/track-008-successors/{track}-metadata.json"
        try:
            metadata_rows.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise SuccessorCandidateError(f"invalid candidate metadata: {path}") from exc
    if {row.get("id") for row in metadata_rows} != SUCCESSORS or any(
        row.get("status") != "blocked" for row in metadata_rows
    ):
        raise SuccessorCandidateError("both successor metadata candidates must remain blocked")

    modes = _load(root / "docs/candidates/track-008-successors/dependency-modes.yml")
    mode_rows = modes.get("modes", {})
    if set(mode_rows) != EXPECTED_MODES or modes.get("default") != (
        "deny_unknown_or_unlabelled_mode"
    ):
        raise SuccessorCandidateError("mode vocabulary and default must fail closed")
    for name in HIGH_RISK_MODES:
        if set(mode_rows[name].get("required_tracks", [])) != SUCCESSORS:
            raise SuccessorCandidateError(f"high-risk mode bypasses a successor: {name}")
        if not mode_rows[name].get("required_external_evidence"):
            raise SuccessorCandidateError(f"high-risk mode lacks external evidence: {name}")
    if modes.get("claims") != {
        "active": False,
        "dependencies_migrated": False,
        "track_009_unblocked": False,
    }:
        raise SuccessorCandidateError("mode contract cannot claim activation")

    migration = _load(root / "docs/candidates/track-008-successors/reference-migration.yml")
    historical = migration.get("historical_track", {})
    if historical.get("proposed_terminal_state") != "archived_superseded_not_complete":
        raise SuccessorCandidateError("historical Track 008 must never be completed")
    consumers = migration.get("operational_references", [])
    if {row.get("consumer") for row in consumers} != {
        "003-monogenic-diabetes-demonstrator",
        "009-evidence-parameter-ledger",
        "011-bronchiectasis-demonstrator",
        "012-paediatric-burden-demonstrator",
        "014-atlas-api-release",
    }:
        raise SuccessorCandidateError("operational consumer migration is incomplete")
    if any(not row.get("additional_mode_gate") for row in consumers):
        raise SuccessorCandidateError("every consumer requires a mode gate")
    if any(
        migration.get("claims", {}).get(name) is not False
        for name in (
            "applied",
            "historical_track_complete",
            "successors_complete",
            "track_009_unblocked",
        )
    ):
        raise SuccessorCandidateError("migration cannot claim an operative effect")

    claims = candidate.get("claims", {})
    if any(claims.get(name) is not False for name in FALSE_CLAIMS):
        raise SuccessorCandidateError("all completion and authority claims must remain false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.candidate.resolve(), args.root.resolve())
    except (SuccessorCandidateError, OSError) as exc:
        print(f"Track 008 successor implementation candidate failed: {exc}")
        return 1
    print("Track 008 successor implementation candidate passed; no live state changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
