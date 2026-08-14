from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_synthetic_checklist_is_non_authorizing_and_has_fail_closed_checks() -> None:
    document = yaml.safe_load(
        (ROOT / "docs/track-016-synthetic-recovery-security-checklist.yml").read_text()
    )
    assert document["production_authorized"] is False
    assert document["independence"] == "not_independent"
    ids = {check["id"] for check in document["checks"]}
    assert ids == {
        "clean_environment_restore",
        "tamper_detection",
        "correction_withdrawal",
        "rollback",
        "security_scan_boundary",
    }
    assert all(check["stop_on"] for check in document["checks"])


def test_synthetic_checklist_keeps_external_gates_open() -> None:
    text = (ROOT / "docs/track-016-synthetic-recovery-security-checklist.yml").read_text()
    assert "not an independent operator" in text
    assert "does not assign a backup owner" in text
