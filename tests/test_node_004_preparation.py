from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_node_review_packet_keeps_controlled_pilot_disabled() -> None:
    text = (ROOT / "docs/track-004-node-review-packet.md").read_text(encoding="utf-8")
    lowered = text.lower()
    normalized = " ".join(lowered.split())
    assert "non-binding preparation" in lowered
    assert "do not activate a real node or controlled-data pilot" in lowered
    for gate in (
        "custodian disclosure policy",
        "data governance and pilot",
        "patient/community",
        "independent operation",
    ):
        assert gate in lowered
    assert "same-operator only" in lowered
    assert "never commit participant rows" in normalized
