from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_governance_tabletop_template_is_non_binding_and_covers_reserved_scenarios() -> None:
    text = (ROOT / "docs/governance-015-tabletop-template.md").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "non-binding" in lowered or "non binding" in lowered
    for scenario in ("withdrawal", "funder", "veto", "stigmatizing", "disclosure"):
        assert scenario in lowered
    assert "accountable" in lowered
