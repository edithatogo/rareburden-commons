#!/usr/bin/env python3
"""Validate the bounded Track 015 archive decision and conditional register."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from rareburden.schema import load_document


class Track015ArchiveCloseoutError(ValueError):
    """Raised when Track 015 archival overclaims or loses a future control."""


def _safe_file(root: Path, value: object) -> Path:
    relative = Path(str(value))
    if relative.is_absolute() or ".." in relative.parts:
        raise Track015ArchiveCloseoutError("closeout reference is unsafe")
    path = root / relative
    if not path.is_file():
        raise Track015ArchiveCloseoutError(f"closeout reference is missing: {relative}")
    return path


def validate(decision_path: Path, register_path: Path, root: Path) -> dict[str, object]:
    decision = load_document(decision_path)
    register = load_document(register_path)

    if decision.get("status") != "owner_approved":
        raise Track015ArchiveCloseoutError("owner closeout decision is not approved")
    if decision.get("selected_option") != "archive_bounded_repository_governance":
        raise Track015ArchiveCloseoutError("bounded archive option is not selected")
    effects = decision.get("effects", {})
    if effects != {
        "track_status": "complete",
        "track_location": "conductor/archive/015-governance-partnership-policy",
        "external_activation_authorized": False,
        "third_party_rights_changed": False,
        "partnership_or_endorsement_confirmed": False,
        "future_scope_requires_new_exact_candidate_decision": True,
    }:
        raise Track015ArchiveCloseoutError("closeout effects overclaim authority")

    if decision.get("conditional_register") != (
        "docs/track-015-external-activation-register-2026-08-21.yml"
    ):
        raise Track015ArchiveCloseoutError("decision does not bind the conditional register")
    historical = load_document(_safe_file(root, decision.get("historical_blocker_record")))
    supersession = historical.get("bounded_scope_supersession", {})
    if supersession.get("decision") != ("docs/decisions/2026-08-21-track-015-bounded-closeout.yml"):
        raise Track015ArchiveCloseoutError("historical blocker record lacks scope supersession")

    if register.get("status") != "standing_conditional_register":
        raise Track015ArchiveCloseoutError("future conditions are not in a standing register")
    if register.get("track_completion_blocking") is not False:
        raise Track015ArchiveCloseoutError("future optional activation still blocks the track")
    if register.get("default_activation") is not False:
        raise Track015ArchiveCloseoutError("external activation must fail closed")
    conditions = register.get("conditions", [])
    expected_ids = {
        "unrelated_community_or_indigenous_authority",
        "country_node_or_controlled_data",
        "publisher_licensor_or_third_party_rights",
        "partnership_endorsement_or_hosting",
        "public_production_or_stable_release",
    }
    if {item.get("id") for item in conditions} != expected_ids:
        raise Track015ArchiveCloseoutError("conditional external controls are incomplete")
    if any(item.get("state") != "not_applicable_until_requested" for item in conditions):
        raise Track015ArchiveCloseoutError("an external condition was activated without evidence")
    if len(register.get("prohibited_inferences", [])) != 5:
        raise Track015ArchiveCloseoutError("prohibited external inferences are incomplete")

    track_dir = root / "conductor/archive/015-governance-partnership-policy"
    metadata = json.loads((track_dir / "metadata.json").read_text(encoding="utf-8"))
    if metadata.get("status") != "complete":
        raise Track015ArchiveCloseoutError("Track 015 metadata is not complete")
    plan = (track_dir / "plan.md").read_text(encoding="utf-8")
    if re.search(r"^- \[ \] ", plan, flags=re.MULTILINE):
        raise Track015ArchiveCloseoutError("Track 015 plan still has unchecked tasks")
    return {
        "status": "track_015_bounded_archive_valid",
        "conditional_gate_count": len(conditions),
        "external_activation": False,
        "track_status": "complete",
        "track_location": "conductor/archive/015-governance-partnership-policy",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("decision", type=Path)
    parser.add_argument("register", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        result = validate(args.decision.resolve(), args.register.resolve(), args.root.resolve())
    except (OSError, TypeError, ValueError) as exc:
        print(f"Track 015 archive closeout failed: {exc}")
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
