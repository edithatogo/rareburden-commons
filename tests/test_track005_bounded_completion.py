from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from scripts.check_track005_bounded_completion import (
    DECISION,
    BoundedCompletionError,
    validate_authorization,
    validate_completion_state,
)

ROOT = Path(__file__).parents[1]


def _copy_authorization_inputs(destination: Path) -> None:
    for relative in (DECISION,):
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


def test_bounded_completion_rejects_empirical_activation(tmp_path: Path) -> None:
    _copy_authorization_inputs(tmp_path)
    decision_path = tmp_path / DECISION
    decision = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
    decision["claims"]["empirical_parameter_activation"] = True
    decision_path.write_text(yaml.safe_dump(decision), encoding="utf-8")
    with pytest.raises(BoundedCompletionError, match="authorization scope drift"):
        validate_authorization(tmp_path)


def test_bounded_completion_rejects_independent_review_claim(tmp_path: Path) -> None:
    _copy_authorization_inputs(tmp_path)
    decision_path = tmp_path / DECISION
    decision = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
    decision["claims"]["independent_review"] = True
    decision_path.write_text(yaml.safe_dump(decision), encoding="utf-8")
    with pytest.raises(BoundedCompletionError, match="authorization scope drift"):
        validate_authorization(tmp_path)


def test_bounded_completion_rejects_scope_drift(tmp_path: Path) -> None:
    _copy_authorization_inputs(tmp_path)
    decision_path = tmp_path / DECISION
    decision = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
    decision["authorization"]["scope"] = "broadened"
    decision_path.write_text(yaml.safe_dump(decision), encoding="utf-8")
    with pytest.raises(BoundedCompletionError, match="authorization scope drift"):
        validate_authorization(tmp_path)


def test_bounded_completion_rejects_track_complete_false(tmp_path: Path) -> None:
    _copy_authorization_inputs(tmp_path)
    decision_path = tmp_path / DECISION
    decision = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
    decision["authorization"]["track_complete"] = False
    decision_path.write_text(yaml.safe_dump(decision), encoding="utf-8")
    with pytest.raises(BoundedCompletionError, match="authorization scope drift"):
        validate_authorization(tmp_path)


def test_bounded_completion_rejects_wrong_decision_maker(tmp_path: Path) -> None:
    _copy_authorization_inputs(tmp_path)
    decision_path = tmp_path / DECISION
    decision = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
    decision["decided_by"] = "someone_else"
    decision_path.write_text(yaml.safe_dump(decision), encoding="utf-8")
    with pytest.raises(BoundedCompletionError, match="authorization scope drift"):
        validate_authorization(tmp_path)
