from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_atlas_accessibility_checklist_preserves_fail_closed_boundaries() -> None:
    text = (ROOT / "docs/track-014-accessibility-checklist.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    for phrase in (
        "missingness",
        "uncertainty",
        "limitations",
        "aggregate-only",
        "read-only",
        "meaningful heading and descriptive link text",
        "avoid colour-only, hover-only or visual-only meaning",
        "not an accessibility or community acceptance decision or accessibility certification",
        "advisory accessibility/usability challenge and "
        "repository-owner disposition remain pending",
        "does not satisfy either gate",
        "no actual community participation",
        "consent or independent review",
        "real-user usability are not established",
        "no public API or beta publication enabled",
    ):
        assert phrase in normalized
    assert "Independent accessibility and patient/community review remain pending" not in normalized
