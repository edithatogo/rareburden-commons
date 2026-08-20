from pathlib import Path

from rareburden.schema import load_mapping

ROOT = Path(__file__).parents[1]
PACKET = ROOT / "docs/track-007-v021-scope-decision-packet-2026-08-20.yml"


def test_scope_decision_packet_is_pending_and_recommends_bounded_pilot() -> None:
    data = load_mapping(PACKET)
    assert data["status"] == "awaiting_owner_selection"
    assert data["owner_decision_fields"]["selected_option"] is None
    assert data["recommendation"] == "select_A_then_reconcile_before_any_expansion"
    assert data["options"][0]["recommended"] is True
    assert data["options"][0]["scope"]["planned_cells"] == 48


def test_scope_options_remain_fail_closed() -> None:
    data = load_mapping(PACKET)
    assert {option["id"] for option in data["options"]} == {"A", "B", "C"}
    assert "no_global_or_representative_claim" in data["required_acknowledgements"]
    assert "community_authority_remains_pending" in data["required_acknowledgements"]
    assert "missingness_is_not_exclusion_or_absence" in data["required_acknowledgements"]
