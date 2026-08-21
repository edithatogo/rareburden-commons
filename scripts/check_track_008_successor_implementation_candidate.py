#!/usr/bin/env python3
"""Validate the non-operative Track 008 successor implementation candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


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
EXPECTED_ATOMIC_EFFECTS = {
    "register_019",
    "register_020",
    "archive_008_as_superseded_not_complete",
    "migrate_operational_references",
    "install_default_deny_mode_validator",
    "regenerate_runtime_assets",
}
EXPECTED_PROHIBITED_EFFECTS = {
    "modify_live_track_registry",
    "modify_live_roadmap",
    "modify_live_track_metadata",
    "register_successor",
    "complete_any_track",
    "unblock_track_009",
    "activate_semantic_mode",
}
EXPECTED_CONSUMERS = {
    "003-monogenic-diabetes-demonstrator",
    "009-evidence-parameter-ledger",
    "011-bronchiectasis-demonstrator",
    "012-paediatric-burden-demonstrator",
    "014-atlas-api-release",
}
EXPECTED_MIGRATIONS = {
    "009-evidence-parameter-ledger": (
        ["002-public-source-acquisition", "008-semantic-backbone"],
        ["002-public-source-acquisition", "019-bounded-semantic-infrastructure"],
    ),
    "003-monogenic-diabetes-demonstrator": (
        [
            "008-semantic-backbone",
            "009-evidence-parameter-ledger",
            "010-public-burden-engine",
        ],
        [
            "019-bounded-semantic-infrastructure",
            "009-evidence-parameter-ledger",
            "010-public-burden-engine",
        ],
    ),
    "011-bronchiectasis-demonstrator": (
        [
            "008-semantic-backbone",
            "009-evidence-parameter-ledger",
            "010-public-burden-engine",
        ],
        [
            "019-bounded-semantic-infrastructure",
            "009-evidence-parameter-ledger",
            "010-public-burden-engine",
        ],
    ),
    "012-paediatric-burden-demonstrator": (
        [
            "004-federated-node-runner",
            "005-economic-social-burden",
            "008-semantic-backbone",
            "009-evidence-parameter-ledger",
            "010-public-burden-engine",
        ],
        [
            "004-federated-node-runner",
            "005-economic-social-burden",
            "019-bounded-semantic-infrastructure",
            "009-evidence-parameter-ledger",
            "010-public-burden-engine",
        ],
    ),
    "014-atlas-api-release": (
        ["Track 008 plan reference"],
        ["Track 019 plus Track 020 for public semantic output"],
    ),
}
EXPECTED_ROLLBACK = (
    "revert_entire_atomic_change_and_restore_all_consumers_to_blocked_historical_008_dependency"
)


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
    if candidate.get("status") == "superseded_by_bounded_completion_scope":
        decision_path = candidate.get("superseded_by")
        if not isinstance(decision_path, str) or not (root / decision_path).is_file():
            raise SuccessorCandidateError(
                "superseded candidate must name its bounded completion decision"
            )
        decision = _load(root / decision_path)
        if decision.get("track_id") != "008-semantic-backbone":
            raise SuccessorCandidateError("superseding decision must identify Track 008")
        if decision.get("owner_decision", {}).get("selected_option") != "A":
            raise SuccessorCandidateError("superseding decision must select bounded option A")
        if decision.get("effect", {}).get("track_008_status") != "complete_for_bounded_scope":
            raise SuccessorCandidateError(
                "superseding decision must complete only the bounded scope"
            )
        return
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

    candidate_files = candidate.get("candidate_files", [])
    file_hashes = candidate.get("candidate_file_sha256", {})
    if set(candidate_files) != set(file_hashes) or len(candidate_files) != len(file_hashes):
        raise SuccessorCandidateError("candidate file manifest is incomplete or duplicated")
    for relative in candidate_files:
        path = root / relative
        if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            raise SuccessorCandidateError(f"missing or unsafe candidate file: {relative}")
        if file_hashes.get(relative) != _sha256(path):
            raise SuccessorCandidateError(f"candidate file hash drift: {relative}")
    if set(candidate.get("required_atomic_effects", [])) != EXPECTED_ATOMIC_EFFECTS:
        raise SuccessorCandidateError("required atomic effects are incomplete")
    if set(candidate.get("prohibited_current_effects", [])) != EXPECTED_PROHIBITED_EFFECTS:
        raise SuccessorCandidateError("prohibited current effects are incomplete")

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

    receipt_schema_path = (
        root / "docs/candidates/track-008-successors/external-evidence-receipt.schema.json"
    )
    try:
        receipt_schema = json.loads(receipt_schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(receipt_schema)
    except (OSError, UnicodeError, json.JSONDecodeError, SchemaError) as exc:
        raise SuccessorCandidateError("external evidence receipt schema is invalid") from exc
    register = _load(root / "docs/candidates/track-008-successors/external-evidence-register.yml")
    receipts = register.get("receipts", [])
    if register.get("status") != "candidate_not_active" or not isinstance(receipts, list):
        raise SuccessorCandidateError("external evidence register must remain inactive")
    receipt_validator = Draft202012Validator(receipt_schema)
    for receipt in receipts:
        if list(receipt_validator.iter_errors(receipt)):
            raise SuccessorCandidateError("external evidence receipt is schema-invalid")
        if receipt.get("status") == "qualifying":
            raise SuccessorCandidateError(
                "non-operative candidate cannot contain a qualifying external receipt"
            )
    if any(register.get("claims", {}).values()):
        raise SuccessorCandidateError("external evidence register cannot satisfy a gate")

    migration = _load(root / "docs/candidates/track-008-successors/reference-migration.yml")
    historical = migration.get("historical_track", {})
    if historical.get("proposed_terminal_state") != "archived_superseded_not_complete":
        raise SuccessorCandidateError("historical Track 008 must never be completed")
    consumers = migration.get("operational_references", [])
    if {row.get("consumer") for row in consumers} != EXPECTED_CONSUMERS or len(consumers) != len(
        EXPECTED_CONSUMERS
    ):
        raise SuccessorCandidateError("operational consumer migration is incomplete")
    if any(not row.get("additional_mode_gate") for row in consumers):
        raise SuccessorCandidateError("every consumer requires a mode gate")
    for row in consumers:
        expected_current, expected_proposed = EXPECTED_MIGRATIONS[row["consumer"]]
        if row.get("current") != expected_current or row.get("proposed") != expected_proposed:
            raise SuccessorCandidateError(
                f"consumer dependency migration has drifted: {row['consumer']}"
            )
    atomicity = migration.get("atomicity", {})
    if (
        set(atomicity.get("apply_together", [])) != EXPECTED_ATOMIC_EFFECTS
        or atomicity.get("rollback") != EXPECTED_ROLLBACK
    ):
        raise SuccessorCandidateError("atomic application or rollback contract has drifted")

    spec_019 = (root / "docs/candidates/track-008-successors/019-spec.md").read_text(
        encoding="utf-8"
    )
    required_019_clauses = (
        "Every distributed exact-unmodified asset has exact source-specific rights",
        "already-public derived artifacts remain unavailable for additional",
        "Unknown semantic-use modes deny by default",
    )
    if any(clause not in spec_019 for clause in required_019_clauses):
        raise SuccessorCandidateError("Track 019 critical acceptance clauses have drifted")
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
