from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_external_gate_register_is_pending_and_fail_closed() -> None:
    text = (ROOT / "docs/external-gate-register-017.md").read_text(encoding="utf-8")
    assert "**Status:** template; all gates are pending." in text
    for gate in (
        "Scientific methods",
        "Patient/community",
        "Data governance/custodian",
        "Independent operator",
        "Operational ownership",
        "Release authority",
    ):
        assert f"| {gate} |" in text
    assert text.count("`pending`") >= 6
    assert "stable-v1 publication" in text
