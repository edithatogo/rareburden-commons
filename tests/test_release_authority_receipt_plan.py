from __future__ import annotations

from pathlib import Path

import yaml

PLAN = Path(__file__).parents[1] / "docs/release-authority-receipt-plan-2026-08-03.yml"


def test_release_plan_is_candidate_bound_and_stable_gate_pending() -> None:
    document = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    assert document["owner_disposition"]["decision"] == "bounded"
    assert document["stable_release_receipt"]["status"] == "pending"
    assert document["candidate"]["tag"] == "candidate-2026-08-03"
    assert document["candidate"]["manifest_id"] == "rel-b213c531a6b754940f80ab70"


def test_release_plan_requires_supersession_and_stop_triggers() -> None:
    document = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    assert document["candidate_change"]["action"] == "supersede_and_reissue"
    assert "critical_security" in document["stop_triggers"]
    assert "recovery_failure" in document["stop_triggers"]
