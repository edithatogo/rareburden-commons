from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_atlas_accessibility_checklist_preserves_fail_closed_boundaries() -> None:
    text = (ROOT / "docs/track-014-accessibility-checklist.md").read_text(encoding="utf-8")
    for phrase in (
        "missingness",
        "uncertainty",
        "limitations",
        "aggregate-only",
        "read-only",
        "Independent accessibility",
        "patient/community review",
    ):
        assert phrase in text
