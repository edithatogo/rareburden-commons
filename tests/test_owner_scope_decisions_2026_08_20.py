from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def _load(path: str) -> dict:
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def test_track_007_scope_is_narrow_and_does_not_claim_authority() -> None:
    decision = _load("docs/track-007-bounded-technical-scope-2026-08-20.yml")
    assert decision["decision"] == "narrow"
    assert decision["community_authority"]["state"] == (
        "non_applicable_to_bounded_technical_scope_not_satisfied"
    )
    assert decision["authority_boundary"]["independent_or_external_approval"] is False
    assert {"global_coverage", "representativeness", "confirmed_novelty"} <= set(
        decision["prohibited_claims"]
    )


def test_track_017_single_owner_decision_is_bounded() -> None:
    decision = _load("docs/track-017-single-owner-continuity-disposition-2026-08-20.yml")
    assert decision["scope"] == "bounded_non_production_synthetic_public_candidate"
    assert decision["backup_owner_requirement"]["current_scope"] == (
        "non_applicable_by_owner_decision"
    )
    assert not any(decision["claims"].values())


def test_private_capacity_route_remains_fail_closed_without_cost_cap() -> None:
    decision = _load("docs/track-002-private-archive-capacity-decision-2026-08-16.yml")
    owner = decision["owner_disposition_2026_08_20"]
    assert owner["selected_route"] == "A"
    assert owner["cost_cap"] is None
    assert owner["while_pending"] == "option_C_fail_closed_pause"
    assert decision["claims"]["capacity_restored"] is False
