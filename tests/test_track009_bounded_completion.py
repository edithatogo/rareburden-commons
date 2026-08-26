from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from scripts.check_track009_bounded_completion import (
    DECISION,
    FREEZE_DISPOSITION,
    FREEZE_MANIFEST,
    BoundedCompletionError,
    validate_authorization,
    validate_completion_state,
)

ROOT = Path(__file__).parents[1]


def _copy_authorization_inputs(destination: Path) -> None:
    for relative in (DECISION, FREEZE_MANIFEST, FREEZE_DISPOSITION):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)


def test_bounded_completion_authorization_passes() -> None:
    validate_authorization(ROOT)


def test_bounded_completion_lifecycle_state_passes() -> None:
    validate_completion_state(ROOT)


def test_bounded_completion_rejects_release_authority(tmp_path: Path) -> None:
    _copy_authorization_inputs(tmp_path)
    decision_path = tmp_path / DECISION
    decision = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
    decision["claims"]["release_authority"] = True
    decision_path.write_text(yaml.safe_dump(decision), encoding="utf-8")
    with pytest.raises(BoundedCompletionError, match="authorization scope drift"):
        validate_authorization(tmp_path)


def test_bounded_completion_rejects_freeze_binding_drift(tmp_path: Path) -> None:
    _copy_authorization_inputs(tmp_path)
    manifest_path = tmp_path / FREEZE_MANIFEST
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["scope"] = "broadened"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(BoundedCompletionError, match="freeze_manifest binding drift"):
        validate_authorization(tmp_path)
