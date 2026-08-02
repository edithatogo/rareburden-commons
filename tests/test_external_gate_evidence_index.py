from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_external_gate_evidence_index_retains_all_accountable_lanes() -> None:
    text = (ROOT / "docs/external-gate-evidence-index.md").read_text(encoding="utf-8")
    for lane in (
        "Scientific methods authority",
        "Patient/community authority",
        "Custodian/data-governance authority",
        "Independent operator",
        "Named operational owners",
        "Release authority",
    ):
        assert f"| {lane} |" in text
    assert "does not record\napproval" in text
    assert "subagent panels remain" in text
