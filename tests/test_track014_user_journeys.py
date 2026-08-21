from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
JOURNEYS = ROOT / "docs/track-014-bounded-user-journeys-2026-08-21.yml"


def _payload() -> dict:
    return yaml.safe_load(JOURNEYS.read_text(encoding="utf-8"))


def test_user_journeys_cover_required_audiences_and_remain_non_authorizing() -> None:
    payload = _payload()
    assert payload["status"] == "repository_design_hypotheses_not_user_research"
    assert payload["publication_authorized"] is False
    assert payload["hosted_api_authorized"] is False
    assert payload["external_validation_observed"] is False
    assert {journey["audience"] for journey in payload["journeys"]} == {
        "patient",
        "policy",
        "research",
        "custodian",
        "funder",
    }


def test_each_user_journey_has_evidence_and_fail_closed_decision_support() -> None:
    payload = _payload()
    assert len(payload["shared_requirements"]) >= 5
    for journey in payload["journeys"]:
        for field in (
            "goal",
            "entry_point",
            "decisions",
            "outputs",
            "required_evidence",
            "stop_conditions",
        ):
            assert journey[field]
        assert len(journey["stop_conditions"]) >= 2

    remaining = payload["validation_boundary"]["still_required"]
    assert "real-user usability evidence" in remaining
    assert "release authority and explicit publication decision" in remaining
