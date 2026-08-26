from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
DECISION = ROOT / "docs/decisions/2026-08-22-track-008-bounded-completion.yml"
TRACK009_COMPLETION = (
    ROOT / "docs/decisions/2026-08-26-track-009-bounded-completion-authorization.yml"
)


def test_bounded_completion_is_explicit_and_fail_closed() -> None:
    decision = yaml.safe_load(DECISION.read_text(encoding="utf-8"))
    assert decision["owner_decision"]["selected_option"] == "A"
    assert decision["owner_decision"]["governance_status"] == (
        "owner_operated_not_independent_review"
    )
    assert decision["effect"] == {
        "track_008_status": "complete_for_bounded_scope",
        "track_009_dependency": "satisfied_for_bounded_preparation_only",
        "release_authority": False,
        "external_expansion_authority": False,
        "independent_review_claim": False,
    }
    assert decision["external_expansion_gates"]["status"] == ("pending_outside_bounded_completion")
    assert all(decision["completion_scope"]["prohibited_effects"])


def test_track009_completion_requires_a_separate_bounded_authorization() -> None:
    metadata = json.loads(
        (ROOT / "conductor/tracks/009-evidence-parameter-ledger/metadata.json").read_text(
            encoding="utf-8"
        )
    )
    completion = yaml.safe_load(TRACK009_COMPLETION.read_text(encoding="utf-8"))
    assert metadata["status"] == "complete"
    assert completion["authorization"]["track_complete"] is True
    assert completion["authorization"]["scope"] == (
        "bounded synthetic and exactly-receipted public-aggregate contract only"
    )
    assert completion["claims"] == {
        "contract_frozen": True,
        "scope_synthetic_and_receipted_public_aggregate_only": True,
        "empirical_parameter_activation": False,
        "controlled_data_activation": False,
        "independent_review": False,
        "publication_authority": False,
        "release_authority": False,
    }
