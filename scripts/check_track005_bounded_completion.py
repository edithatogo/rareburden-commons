#!/usr/bin/env python3
"""Validate Track 005 bounded completion authorization and lifecycle state."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

DECISION = Path("docs/decisions/2026-09-05-track-005-owner-completion-disposition.yml")
PANEL = Path("docs/track-005-agent-panel-review-2026-09-05.yml")
PROTOCOL = Path("docs/track-005-rbc-p001d-protocol.md")
COMPLETION_DECISION = Path("docs/track-005-completion-decision-2026-09-05.md")
PLAN = Path("conductor/tracks/005-economic-social-burden/plan.md")
METADATA = Path("conductor/tracks/005-economic-social-burden/metadata.json")
REVIEW = Path("conductor/tracks/005-economic-social-burden/review.md")
REGISTRY = Path("conductor/tracks.md")
SETUP_STATE = Path("conductor/setup_state.json")
SCHEMA = Path("schemas/economic-parameters.schema.json")
ENGINE = Path("src/rareburden/economic_engine.py")
SURVEY_GATE = Path("src/rareburden/economic_survey.py")
DEMONSTRATOR = Path("src/rareburden/demonstrator_economic.py")
SURVEY_PROTOCOL = Path("docs/economic-survey-core-protocol.md")
PAEDIATRIC_SPEC = Path("docs/paediatric-economic-input-specification.md")
DATA_GAP_PLAN = Path("docs/economic-data-gap-plan.md")
EXAMPLE_PARAMETERS = Path("examples/economics/economic-reference-parameters.yml")
TRACK_ID = "005-economic-social-burden"


class BoundedCompletionError(ValueError):
    """The Track 005 completion authorization or lifecycle state escaped scope."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BoundedCompletionError(f"expected mapping in {path}")
    return value


def validate_authorization(root: Path) -> None:
    decision = _mapping(root / DECISION)
    authorization = decision.get("authorization", {})
    claims = decision.get("claims", {})
    expected_claims = {
        "contract_frozen": True,
        "scope_reference_methods_and_software_only": True,
        "empirical_parameter_activation": False,
        "controlled_data_activation": False,
        "human_survey_collection_active": False,
        "independent_review": False,
        "publication_authority": False,
        "release_authority": False,
    }
    if (
        decision.get("track_id") != TRACK_ID
        or decision.get("decision_type") != "bounded_track_completion_authorization"
        or decision.get("decided_by") != "edithatogo"
        or decision.get("accountable_role") != "repository owner and sole accountable human"
        or not isinstance(authorization, dict)
        or authorization.get("track_complete") is not True
        or authorization.get("scope") != "bounded reference methods and software contracts only"
        or claims != expected_claims
    ):
        raise BoundedCompletionError("bounded owner authorization scope drift")

    if not (root / PROTOCOL).exists():
        raise BoundedCompletionError("RBC-P001D protocol document missing")
    if not (root / COMPLETION_DECISION).exists():
        raise BoundedCompletionError("completion decision document missing")
    if not (root / PANEL).exists():
        raise BoundedCompletionError("agent panel review document missing")

    panel = _mapping(root / PANEL)
    if panel.get("track_id") != TRACK_ID:
        raise BoundedCompletionError("panel track binding drift")
    if panel.get("simulation_status") != "simulated_role_separated_advisory_panel":
        raise BoundedCompletionError("panel simulation status drift")

    # Verify core implementation evidence exists
    for evidence_path in (
        SCHEMA,
        ENGINE,
        SURVEY_GATE,
        DEMONSTRATOR,
        SURVEY_PROTOCOL,
        PAEDIATRIC_SPEC,
        DATA_GAP_PLAN,
        EXAMPLE_PARAMETERS,
    ):
        if not (root / evidence_path).exists():
            raise BoundedCompletionError(f"required evidence file missing: {evidence_path}")


def validate_completion_state(root: Path) -> None:
    validate_authorization(root)
    plan = (root / PLAN).read_text(encoding="utf-8")
    if re.search(r"^- \[ \]", plan, flags=re.MULTILINE):
        raise BoundedCompletionError("Track 005 plan still has pending tasks")
    metadata = json.loads((root / METADATA).read_text(encoding="utf-8"))
    setup_state = json.loads((root / SETUP_STATE).read_text(encoding="utf-8"))
    registry = (root / REGISTRY).read_text(encoding="utf-8")
    review = (root / REVIEW).read_text(encoding="utf-8")
    expected_registry = (
        "| 005 | [Patient, family, economic and social burden module]"
        "(./tracks/005-economic-social-burden/index.md) | Complete "
        "(bounded reference methods and software contracts) |"
    )
    if metadata.get("status") != "complete":
        raise BoundedCompletionError("Track 005 metadata is not complete")
    if expected_registry not in registry:
        raise BoundedCompletionError("Track 005 registry completion scope drift")
    if TRACK_ID not in setup_state.get("completed_tracks", []):
        raise BoundedCompletionError("Track 005 missing from completed tracks")
    if TRACK_ID in setup_state.get("blocked_tracks", []):
        raise BoundedCompletionError("Track 005 remains in blocked tracks")
    if DECISION.as_posix() not in review and DECISION.name not in review:
        raise BoundedCompletionError("Track 005 review lacks completion authorization reference")


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
        print(f"Track 005 bounded completion failed: {exc}")
        return 1
    print(
        "Track 005 bounded completion authorization passed; empirical, "
        "controlled-data, independent-review, publication and release claims "
        "remain false."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
