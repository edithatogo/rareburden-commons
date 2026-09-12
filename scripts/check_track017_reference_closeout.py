#!/usr/bin/env python3
"""Validate Track 017 reference closeout authorization and lifecycle state."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

DECISION = Path("docs/decisions/2026-09-06-track-017-owner-reference-disposition.yml")
PANEL = Path("docs/reviews/track-017-reference-output-panel-2026-09-06.yml")
REGISTRATION = Path("docs/track-017-rbc-a001-bounded-registration-2026-09-06.yml")
CLOSEOUT = Path("docs/track-017-reference-closeout-2026-09-06.md")
MANIFEST = Path("manifests/demonstrators/track-017-reference-execution-2026-09-06.json")
ENGINE = Path("src/rareburden/demonstrator_adoption.py")
PLAN = Path("conductor/tracks/017-documentation-adoption-v1/plan.md")
METADATA = Path("conductor/tracks/017-documentation-adoption-v1/metadata.json")
REVIEW = Path("conductor/tracks/017-documentation-adoption-v1/review.md")
REGISTRY = Path("conductor/tracks.md")
SETUP_STATE = Path("conductor/setup_state.json")
OUTPUT_DIR = Path("results/track-017-reference-2026-09-06")

EXPECTED_OUTPUT_HASHES = {
    "reference-report.md": "779bff3fe5350b05ba5e81e5801726d9486e3342f91618e9a4796f06ce98e14a",
    "reference-results.json": "6683f4727b4c8fdaa72f8e448ed0f43d3ec2cd34423020965895495f44376b1d",
    "reference-tables.csv": "1f5ad9e58d9a33efd295839bf7fb206f1332a1cd6e8366f95d82b7bf9c04fd9e",
}

TRACK_ID = "017-documentation-adoption-v1"


class Track017CloseoutError(ValueError):
    """The Track 017 closeout authorization or lifecycle state escaped scope."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Track017CloseoutError(f"expected mapping in {path}")
    return value


def validate_authorization(root: Path) -> None:
    decision = _mapping(root / DECISION)
    authorization = decision.get("authorization", {})
    claims = decision.get("claims", {})
    expected_claims = {
        "contract_frozen": True,
        "scope_synthetic_assurance_only": True,
        "empirical_activation": False,
        "controlled_data_activation": False,
        "clinical_interpretation": False,
        "independent_review": False,
        "patient_community_approval": False,
        "publication_authority": False,
        "release_authority": False,
    }
    if (
        decision.get("track_id") != TRACK_ID
        or decision.get("decision_type") != "bounded_adoption_reference_disposition"
        or decision.get("decided_by") != "edithatogo"
        or decision.get("accountable_role") != "repository owner and sole accountable human"
        or decision.get("selected_option") != "A"
        or not isinstance(authorization, dict)
        or authorization.get("track_complete") is not False
        or authorization.get("scope")
        != "bounded v1 documentation, adoption, sustainability and single-owner release candidate"
        or claims != expected_claims
    ):
        raise Track017CloseoutError("bounded owner authorization scope drift")

    # Verify panel review
    panel = _mapping(root / PANEL)
    if panel.get("track_id") != TRACK_ID:
        raise Track017CloseoutError("panel track binding drift")
    if panel.get("panel_assurance") != "simulated_role_separated_advisory_panel":
        raise Track017CloseoutError("panel simulation status drift")
    if panel.get("status") != "actual_output_review_passed":
        raise Track017CloseoutError("panel review status not passed")

    # Verify core artifacts exist
    for artifact in (
        REGISTRATION,
        CLOSEOUT,
        MANIFEST,
        ENGINE,
    ):
        if not (root / artifact).exists():
            raise Track017CloseoutError(f"required artifact missing: {artifact}")

    # Verify output files and SHA-256 digests
    for filename, expected_hash in EXPECTED_OUTPUT_HASHES.items():
        output_file = root / OUTPUT_DIR / filename
        if not output_file.exists():
            raise Track017CloseoutError(f"output file missing: {output_file}")
        actual_hash = _sha256(output_file)
        if actual_hash != expected_hash:
            raise Track017CloseoutError(
                f"output file {filename} hash mismatch: expected {expected_hash}, got {actual_hash}"
            )

    # Verify execution manifest
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    if (
        manifest.get("track_id") != TRACK_ID
        or manifest.get("status") != "executed_and_separately_reproduced_synthetic_reference"
    ):
        raise Track017CloseoutError("manifest metadata drift")
    runs = manifest.get("runs", [])
    if len(runs) != 2 or runs[0].get("exit_code") != 0 or runs[1].get("exit_code") != 0:
        raise Track017CloseoutError("manifest runs invalid or unverified")


def validate_plan_and_registry(root: Path) -> None:
    plan_text = (root / PLAN).read_text(encoding="utf-8")
    if re.search(r"^\s*-\s*\[ \]", plan_text, re.MULTILINE):
        raise Track017CloseoutError("Track 017 plan contains unchecked tasks")

    metadata = json.loads((root / METADATA).read_text(encoding="utf-8"))
    if metadata.get("status") != "blocked":
        raise Track017CloseoutError("Track 017 metadata status is not blocked")

    registry_text = (root / REGISTRY).read_text(encoding="utf-8")
    row_match = re.search(r"^\|\s*017\s*\|([^|]+)\|([^|]+)\|", registry_text, re.MULTILINE)
    if not row_match:
        raise Track017CloseoutError("Track 017 row missing from registry")
    status_cell = row_match.group(2).strip()
    if not status_cell.startswith("Blocked"):
        raise Track017CloseoutError(f"Track 017 registry status {status_cell} must be Blocked")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Track 017 reference closeout.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    validate_authorization(args.root)
    validate_plan_and_registry(args.root)
    print("Track 017 reference closeout validated successfully.")


if __name__ == "__main__":
    main()
