from pathlib import Path

import yaml

from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).resolve().parents[1]
CLOSEOUT = ROOT / "docs/track-013-agent-assurance-closeout-2026-08-21.yml"
DECISION = ROOT / "docs/decisions/2026-08-21-track-013-agent-advice-boundary.yml"
GAP_MAP = ROOT / "docs/track-013-public-data-gap-map-2026-08-21.json"


def test_agent_assurance_closeout_is_bounded_by_real_dependencies() -> None:
    closeout = yaml.safe_load(CLOSEOUT.read_text(encoding="utf-8"))
    assert closeout["status"] == "bounded_repository_assurance_complete_dependencies_blocked"
    assert closeout["scope"] == "synthetic_and_metadata_only"
    assert closeout["agent_panel"]["independent_or_human_review"] is False
    assert closeout["owner_disposition"] == {
        "decided_by": "edithatogo",
        "decision": "narrow_and_continue",
        "accepted_scope": "synthetic_and_metadata_only",
        "empirical_or_global_release_authorized": False,
    }
    assert set(closeout["remaining_dependency_states"].values()) == {"blocked"}


def test_agent_boundary_retains_only_activated_external_facts() -> None:
    decision = yaml.safe_load(DECISION.read_text(encoding="utf-8"))
    assert decision["adopted_model"] == {
        "advice": "role_separated_simulated_agents",
        "decision": "repository_owner",
        "independent_or_additional_human_advice_required": False,
    }
    assert len(decision["repository_advice_lanes"]) == 5
    assert len(decision["external_facts_retained_only_if_activated"]) == 4
    assert decision["current_disposition"] == "narrow_and_continue"


def test_committed_gap_map_is_schema_valid_and_fail_closed() -> None:
    gap_map = load_mapping(GAP_MAP)
    validate_instance(gap_map, load_mapping(ROOT / "schemas/gap-map.schema.json"))
    assert gap_map["summary"]["need_count"] == 6
    assert all(row["sufficiency"] == "not_assessed" for row in gap_map["rows"])
    assert any(row["status"] == "unavailable" for row in gap_map["rows"])
