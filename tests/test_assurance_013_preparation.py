from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_assurance_packet_uses_agent_advice_and_keeps_empirical_claims_bounded() -> None:
    text = (ROOT / "docs/track-013-assurance-review-packet.md").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "bounded repository assurance complete" in lowered
    assert "do not approve empirical atlas-beta outputs" in lowered
    for term in ("triangulation", "equity", "agent scientific report", "release language"):
        assert term in lowered
    assert "not_assessed" in lowered
    assert "do not infer global representativeness" in lowered
    assert "external receipts apply only" in lowered
