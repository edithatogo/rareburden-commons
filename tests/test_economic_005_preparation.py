from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_economic_review_packet_keeps_cost_claims_non_binding() -> None:
    text = (ROOT / "docs/track-005-economic-review-packet.md").read_text(encoding="utf-8")
    normalized = " ".join(text.lower().split())
    assert "non-binding preparation" in normalized
    assert "do not freeze cost contracts" in normalized
    assert "or collect patient/family data" in normalized
    for term in (
        "perspectives",
        "valuation",
        "overlap/missingness",
        "distributional reporting",
        "co-design",
    ):
        assert term in normalized
    assert "no patient/family data" in normalized
    assert "do not" in normalized
