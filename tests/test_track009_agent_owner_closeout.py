from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
PACKET = ROOT / "docs/decisions/2026-08-22-track-009-agent-owner-closeout.yml"


def test_track009_bounded_agent_owner_closeout_keeps_external_gates_pending() -> None:
    packet = yaml.safe_load(PACKET.read_text(encoding="utf-8"))
    assert packet["dependency_state"] == {
        "track_002": "archived",
        "track_008": "complete_for_bounded_scope",
    }
    assert packet["panel"]["status"] == "role_separated_agent_advice"
    assert packet["panel"]["independent_review"] is False
    assert packet["owner_disposition"]["status"] == "bounded_preparation_retained"
    assert {finding["status"] for finding in packet["pending_findings"]} == {"pending"}
    assert packet["claims"] == {
        "track_009_complete": False,
        "contract_frozen": False,
        "empirical_activation": False,
        "controlled_data_activation": False,
        "independent_review": False,
        "release_authority": False,
    }
