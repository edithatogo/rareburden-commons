from __future__ import annotations

from pathlib import Path

import yaml

PLAN = Path(__file__).parents[1] / "docs/downstream-bounded-preparation-plan-2026-08-03.yml"


def test_downstream_plan_is_bounded_and_dependency_ordered() -> None:
    document = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    assert document["mode"] == "dependency_ordered_bounded_preparation"
    assert document["activation_rule"] == "synthetic_public_only_until_upstream_receipts"
    assert document["freeze_order"] == ["008", "009", "010"]
    assert document["governance"] == {
        "panel_status": "advisory",
        "owner_status": "owner_operated_not_independent_review",
    }
    assert {item["track"] for item in document["tracks"]} == {
        "008",
        "009",
        "010",
        "003",
        "004",
        "011",
        "005",
        "012",
        "013",
        "014",
        "015",
        "016",
        "017",
    }
    assert all(item["preparation"] and item["blocked"] for item in document["tracks"])
    assert all(
        item["contract_state"] == "provisional"
        for item in document["tracks"]
        if item["track"] in {"008", "009", "010"}
    )


def test_downstream_plan_has_upstream_revalidation_and_stop_rules() -> None:
    document = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    assert document["revalidation"]["on_critical_finding"].startswith("stop")
    assert "track_002" in document["upstream_gates"]
    assert "track_007" in document["upstream_gates"]
    assert document["cross_cutting_security"]["state"] == "authorized_preparation"
    assert document["cross_cutting_security"]["production_activation"] == "blocked"
