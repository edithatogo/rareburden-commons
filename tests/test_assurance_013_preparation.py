from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_assurance_packet_keeps_equity_and_release_claims_non_binding() -> None:
    text = (ROOT / "docs/track-013-assurance-review-packet.md").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "non-binding preparation" in lowered
    assert "do not approve atlas-beta outputs" in lowered
    for term in ("triangulation", "equity", "independent assurance", "release language"):
        assert term in lowered
    assert "not_assessed" in lowered
    assert "do not infer global representativeness" in lowered
