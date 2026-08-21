from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_track_008_bounded_completion_scope_is_explicit() -> None:
    decision = yaml.safe_load(
        (ROOT / "docs/decisions/2026-08-21-track-008-bounded-completion.yml").read_text(
            encoding="utf-8"
        )
    )
    assert decision["owner_decision"] == {
        "status": "accepted",
        "selected_option": "A",
        "governance_status": "owner_operated_not_independent_review",
        "rationale": (
            "Complete Track 008 only for its exact bounded, provisional, non-clinical "
            "semantic contract and preserve every excluded-source, clinical-use and "
            "actual-community-authority condition as a future expansion gate."
        ),
    }
    assert decision["effect"]["track_008_status"] == "complete"
    assert decision["effect"]["track_009_dependency"] == "satisfied"
    assert decision["effect"]["release_authority"] is False
    assert decision["external_expansion_gates"]["status"] == ("pending_outside_track_completion")


def test_track_008_lifecycle_records_are_complete() -> None:
    metadata = json.loads(
        (ROOT / "conductor/tracks/008-semantic-backbone/metadata.json").read_text(encoding="utf-8")
    )
    plan = (ROOT / "conductor/tracks/008-semantic-backbone/plan.md").read_text(encoding="utf-8")
    readiness = yaml.safe_load(
        (ROOT / "docs/track-008-freeze-readiness-2026-08-21.yml").read_text(encoding="utf-8")
    )
    assert metadata["status"] == "complete"
    assert "- [ ]" not in plan
    assert "- [~]" not in plan
    assert readiness["status"] == "complete"
    assert readiness["claims"]["track_complete"] is True
    assert readiness["claims"]["naming_authority"] is False
    assert readiness["claims"]["independent_semantic_review"] is False


def test_track_009_remains_blocked_on_its_own_gates() -> None:
    metadata = json.loads(
        (ROOT / "conductor/tracks/009-evidence-parameter-ledger/metadata.json").read_text(
            encoding="utf-8"
        )
    )
    readiness = yaml.safe_load(
        (ROOT / "docs/track-009-freeze-readiness-2026-08-21.yml").read_text(encoding="utf-8")
    )
    assert metadata["status"] == "blocked"
    assert readiness["upstream_dependencies"][1]["state"] == "satisfied"
    assert {row["status"] for row in readiness["blocking_data_contract_issues"]} == {
        "assigned_pending_evidence"
    }
    assert readiness["review_gate"]["state"] == "pending"
    assert readiness["contract_freeze_gate"]["state"] == "pending"
