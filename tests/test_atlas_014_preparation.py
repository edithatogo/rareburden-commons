from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_atlas_review_packet_is_non_binding_and_keeps_publication_disabled() -> None:
    text = (ROOT / "docs/track-014-atlas-api-review-packet.md").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "non-binding preparation" in lowered
    assert "does not activate an atlas, api, beta release" in lowered
    for gate in (
        "custodian/data-governance",
        "patient/community",
        "independent operator",
        "release authority",
    ):
        assert gate in lowered
    assert "synthetic fixtures" in lowered
    assert "cannot satisfy" in lowered
