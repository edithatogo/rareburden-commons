from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "docs/decisions/2026-08-21-track-002-bounded-completion.yml"


def test_bounded_completion_preserves_fail_closed_external_boundaries() -> None:
    decision = yaml.safe_load(DECISION.read_text(encoding="utf-8"))

    assert decision["decision"] == "complete_bounded_scope"
    assert decision["publication"]["status"] == "deferred"
    assert decision["publication"]["authorized"] is False
    assert decision["source_dispositions"]["who_ghe"]["payload_redistribution"] is False
    assert decision["source_dispositions"]["panelapp"]["automated_detail_capture"] is False
    assert decision["scientific_and_data_use_disposition"]["independent_review_claimed"] is False
    assert not any(decision["external_actions_authorized"].values())


def test_open_licence_reliance_is_exact_and_conditioned() -> None:
    decision = yaml.safe_load(DECISION.read_text(encoding="utf-8"))
    reliance = decision["publisher_licence_reliance"]

    assert reliance["orphadata"]["status"] == "passed_for_exact_allowlist"
    assert reliance["mondo"]["status"] == "passed_for_exact_allowlist"
    assert "chain-of-title" in reliance["reliance_limit"]
    assert "attribution" in reliance["orphadata"]["conditions"]
    assert "preserve_applicable_notices" in reliance["mondo"]["conditions"]
