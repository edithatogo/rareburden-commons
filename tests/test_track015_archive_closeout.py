from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_track015_archive_closeout import (
    Track015ArchiveCloseoutError,
    validate,
)

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "docs/decisions/2026-08-21-track-015-bounded-closeout.yml"
REGISTER = ROOT / "docs/track-015-external-activation-register-2026-08-21.yml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_bounded_track_015_archive_is_valid() -> None:
    assert validate(DECISION, REGISTER, ROOT) == {
        "status": "track_015_bounded_archive_valid",
        "conditional_gate_count": 5,
        "external_activation": False,
        "track_status": "complete",
        "track_location": "conductor/archive/015-governance-partnership-policy",
    }


def test_archive_cannot_activate_external_scope(tmp_path: Path) -> None:
    payload = _load(REGISTER)
    payload["default_activation"] = True
    with pytest.raises(Track015ArchiveCloseoutError, match="fail closed"):
        validate(DECISION, _write(tmp_path, "register.yml", payload), ROOT)


def test_archive_cannot_drop_a_conditional_gate(tmp_path: Path) -> None:
    payload = _load(REGISTER)
    payload["conditions"].pop()
    with pytest.raises(Track015ArchiveCloseoutError, match="incomplete"):
        validate(DECISION, _write(tmp_path, "register.yml", payload), ROOT)


def test_archive_decision_cannot_claim_third_party_rights(tmp_path: Path) -> None:
    payload = copy.deepcopy(_load(DECISION))
    payload["effects"]["third_party_rights_changed"] = True
    with pytest.raises(Track015ArchiveCloseoutError, match="overclaim"):
        validate(_write(tmp_path, "decision.yml", payload), REGISTER, ROOT)
