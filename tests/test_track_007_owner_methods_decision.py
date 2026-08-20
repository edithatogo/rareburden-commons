import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
DECISION = ROOT / "docs/track-007-owner-methods-decision-2026-08-20.json"
PRIORITY = ROOT / "docs/track-007-bounded-content-resolution-2026-08-20.json"


def test_owner_methods_decision_is_fail_closed() -> None:
    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    assert decision["track_status"] == "in_review"
    assert decision["authorization"]["external_or_community_approval"] is False
    assert decision["frozen_69_resolution"]["current_counts"] == {
        "include": 66,
        "exclude": 3,
        "uncertain": 0,
    }
    record = decision["frozen_69_resolution"]["resolved_record"]
    assert record["decision"] == "exclude"
    assert record["evidence"]["article_type"] == "editorial"
    assert record["evidence"]["content_retention"] == "no_response_body_or_full_text_retained"
    assert decision["second_provider_gate"]["status"] == "not_activated"
    assert decision["grey_literature"]["status"] == (
        "predeclared_not_executed_and_excluded_from_current_evidence"
    )
    assert decision["remaining_gate"]["status"] == "pending"
    forbidden = set(decision["claim_register"]["forbidden"])
    assert "confirmed_novelty" in forbidden
    assert "global_or_geographic_representativeness" in forbidden
    assert "external_approval" in forbidden


def test_owner_methods_priority_queue_preserves_all_90_uncertain_records() -> None:
    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    priority = json.loads(PRIORITY.read_text(encoding="utf-8"))
    assert decision["live_only_144"]["bounded_counts"] == priority["counts"]
    assert decision["live_only_144"]["evidence"]["sha256"].startswith("sha256:")
    assert priority["future_assessment_priority_counts"] == {
        "tier_1_explicit_safe_metadata_signal": 46,
        "tier_2_no_explicit_safe_metadata_signal": 44,
    }
    assert sum(priority["future_assessment_priority_counts"].values()) == 90
