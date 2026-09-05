#!/usr/bin/env python3
"""Validate Track 011 reference closeout authorization and lifecycle state."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

DECISION = Path("docs/decisions/2026-09-05-track-011-owner-reference-disposition.yml")
PANEL = Path("docs/reviews/track-011-reference-output-panel-2026-09-05.yml")
REGISTRATION = Path("docs/track-011-rbc-p003-bounded-registration-2026-09-05.yml")
QUALIFICATION = Path("docs/track-011-aetiologic-evidence-qualification-2026-09-05.yml")
LEDGER = Path("docs/track-011-outcome-service-evidence-ledger-2026-09-05.yml")
GAP_REGISTER = Path("docs/track-011-evidence-gap-register-2026-09-05.yml")
CLOSEOUT = Path("docs/track-011-reference-closeout-2026-09-05.md")
MANIFEST = Path("manifests/demonstrators/track-011-reference-execution-2026-09-05.json")
ENGINE = Path("src/rareburden/demonstrator_bronchiectasis.py")
PLAN = Path("conductor/tracks/011-bronchiectasis-demonstrator/plan.md")
METADATA = Path("conductor/tracks/011-bronchiectasis-demonstrator/metadata.json")
REVIEW = Path("conductor/tracks/011-bronchiectasis-demonstrator/review.md")
REGISTRY = Path("conductor/tracks.md")
SETUP_STATE = Path("conductor/setup_state.json")
OUTPUT_DIR = Path("results/track-011-reference-2026-09-05")

EXPECTED_OUTPUT_HASHES = {
    "reference-report.md": "48f4c9d0eb532886b39743d76d017ecfac94554dbd17934d3427636b26e93549",
    "reference-results.json": "e2fd809ed7c4f53864b6c69c3143237d5763a85b9f19150462a6c0d2085eb996",
    "reference-tables.csv": "e157f69e2cbc82a1518ed41df33f2e41860847bff4dae737ee2140a2a7c95f17",
}

TRACK_ID = "011-bronchiectasis-demonstrator"


class Track011CloseoutError(ValueError):
    """The Track 011 closeout authorization or lifecycle state escaped scope."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Track011CloseoutError(f"expected mapping in {path}")
    return value


def validate_authorization(root: Path) -> None:
    decision = _mapping(root / DECISION)
    authorization = decision.get("authorization", {})
    claims = decision.get("claims", {})
    expected_claims = {
        "contract_frozen": True,
        "scope_reference_demonstrator_only": True,
        "empirical_activation": False,
        "clinical_interpretation": False,
        "independent_review": False,
        "patient_community_approval": False,
        "publication_authority": False,
        "release_authority": False,
    }
    if (
        decision.get("track_id") != TRACK_ID
        or decision.get("decision_type") != "bounded_demonstrator_reference_disposition"
        or decision.get("decided_by") != "edithatogo"
        or decision.get("accountable_role") != "repository owner and sole accountable human"
        or decision.get("selected_option") != "A"
        or not isinstance(authorization, dict)
        or authorization.get("track_complete") is not True
        or authorization.get("scope")
        != "bounded synthetic reference demonstrator; no empirical validation"
        or claims != expected_claims
    ):
        raise Track011CloseoutError("bounded owner authorization scope drift")

    # Verify panel review
    panel = _mapping(root / PANEL)
    if panel.get("track_id") != TRACK_ID:
        raise Track011CloseoutError("panel track binding drift")
    if panel.get("panel_assurance") != "simulated_role_separated_advisory_panel":
        raise Track011CloseoutError("panel simulation status drift")
    if panel.get("status") != "actual_output_review_passed":
        raise Track011CloseoutError("panel review status not passed")

    # Verify core artifacts exist
    for artifact in (
        REGISTRATION,
        QUALIFICATION,
        LEDGER,
        GAP_REGISTER,
        CLOSEOUT,
        MANIFEST,
        ENGINE,
    ):
        if not (root / artifact).exists():
            raise Track011CloseoutError(f"missing required artifact: {artifact}")

    # Verify execution manifest and output hashes
    manifest_text = (root / MANIFEST).read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    if manifest.get("track_id") != TRACK_ID:
        raise Track011CloseoutError("manifest track binding drift")

    for filename, expected_hash in EXPECTED_OUTPUT_HASHES.items():
        file_path = root / OUTPUT_DIR / filename
        if not file_path.exists():
            raise Track011CloseoutError(f"missing output file: {file_path}")
        actual_hash = _sha256(file_path)
        if actual_hash != expected_hash:
            raise Track011CloseoutError(
                f"output file {filename} hash mismatch: {actual_hash} != {expected_hash}"
            )


def validate_plan_and_registry(root: Path) -> None:
    plan_text = (root / PLAN).read_text(encoding="utf-8")
    unchecked = re.findall(r"^- \[ \].*$", plan_text, flags=re.MULTILINE)
    if unchecked:
        raise Track011CloseoutError(
            f"plan.md contains {len(unchecked)} unchecked task(s): {unchecked}"
        )

    metadata = json.loads((root / METADATA).read_text(encoding="utf-8"))
    if metadata.get("status") != "complete":
        raise Track011CloseoutError("metadata.json status must be 'complete'")

    registry_text = (root / REGISTRY).read_text(encoding="utf-8")
    match = re.search(
        r"^\|\s*011\s*\|.*?\|\s*([^|]+?)\s*\|\s*Must\s*\|",
        registry_text,
        flags=re.MULTILINE,
    )
    if not match or "Complete" not in match.group(1):
        raise Track011CloseoutError("tracks.md row 011 is not marked Complete")

    setup = json.loads((root / SETUP_STATE).read_text(encoding="utf-8"))
    if TRACK_ID not in setup.get("completed_tracks", []):
        raise Track011CloseoutError(f"{TRACK_ID} missing from setup_state.json completed_tracks")
    if TRACK_ID in setup.get("blocked_tracks", []):
        raise Track011CloseoutError(f"{TRACK_ID} must not be in setup_state.json blocked_tracks")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    args = parser.parse_args()

    validate_authorization(args.root)
    validate_plan_and_registry(args.root)
    print(
        "Track 011 reference closeout authorization passed; "
        "empirical, clinical, independent-review, publication and release claims remain false."
    )


if __name__ == "__main__":
    main()
