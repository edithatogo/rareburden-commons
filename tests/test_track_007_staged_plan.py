from __future__ import annotations

from pathlib import Path

import yaml

PLAN = (
    Path(__file__).parents[1] / "docs/track-007-staged-registration-challenge-plan-2026-08-03.yml"
)


def test_track_007_staged_plan_keeps_external_gates_pending() -> None:
    document = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    assert document["status"] == "registration_and_challenge_preparation"
    assert document["gates"]["external_registration"]["status"] == "pending"
    assert document["gates"]["independent_methods_challenge"]["status"] == "pending"
    assert document["gates"]["patient_community_interpretation"]["status"] == "pending"


def test_track_007_plan_disables_unqualified_claims() -> None:
    document = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    claims = set(document["claims_disabled_until_gates"])
    assert "global completeness" in claims
    assert "novelty confirmed by independent challenge" in claims
