from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.check_track010_candidate_containment import (
    COMPATIBILITY,
    COMPATIBILITY_SHA256,
    DECISION,
    MANIFEST,
    MANIFEST_SHA256,
    Track010ContainmentError,
    validate,
)

ROOT = Path(__file__).parents[1]


def test_exact_candidate_operational_containment_passes() -> None:
    validate(ROOT)


def test_stable_adapter_claim_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    compatibility = json.loads((ROOT / COMPATIBILITY).read_text(encoding="utf-8"))
    compatibility["adapter"]["stable_surface"] = True
    paths = [MANIFEST, DECISION]
    for relative in paths:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    target = tmp_path / COMPATIBILITY
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(compatibility), encoding="utf-8")
    monkeypatch.setattr(
        "scripts.check_track010_candidate_containment.COMPATIBILITY_SHA256",
        hashlib.sha256(target.read_bytes()).hexdigest(),
    )
    monkeypatch.setattr(
        "scripts.check_track010_candidate_containment._git_tree",
        lambda *_: "eda9bbcc46a3a63fd1ee5999dae1b2de32d8f3e8",
    )
    with pytest.raises(Track010ContainmentError, match="adapter boundary escaped"):
        validate(tmp_path)


def test_missing_blocked_claim_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    del manifest["claims"]["release_authority"]
    for relative in (COMPATIBILITY, DECISION):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    target = tmp_path / MANIFEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(
        "scripts.check_track010_candidate_containment.MANIFEST_SHA256",
        hashlib.sha256(target.read_bytes()).hexdigest(),
    )
    monkeypatch.setattr(
        "scripts.check_track010_candidate_containment._git_tree",
        lambda *_: "eda9bbcc46a3a63fd1ee5999dae1b2de32d8f3e8",
    )
    with pytest.raises(Track010ContainmentError, match="blocked claims escaped"):
        validate(tmp_path)


def test_checked_in_hash_constants_match() -> None:
    assert hashlib.sha256((ROOT / MANIFEST).read_bytes()).hexdigest() == MANIFEST_SHA256
    assert hashlib.sha256((ROOT / COMPATIBILITY).read_bytes()).hexdigest() == (COMPATIBILITY_SHA256)
