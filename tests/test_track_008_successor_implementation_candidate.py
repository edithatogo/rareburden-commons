from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_track_008_successor_implementation_candidate import (
    SuccessorCandidateError,
    validate,
)

ROOT = Path(__file__).parents[1]
CANDIDATE = ROOT / "docs/candidates/track-008-successors/implementation-candidate.yml"


def _document(path: Path) -> dict[str, object]:
    return copy.deepcopy(yaml.safe_load(path.read_text(encoding="utf-8")))


def _write(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "candidate.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_candidate_is_non_operative() -> None:
    validate(CANDIDATE, ROOT)


def test_rejects_live_state_drift(tmp_path: Path) -> None:
    document = _document(CANDIDATE)
    document["live_state_baseline"]["conductor_tracks_sha256"] = "0" * 64
    with pytest.raises(SuccessorCandidateError, match="live programme state drift"):
        validate(_write(tmp_path, document), ROOT)


def test_rejects_premature_completion(tmp_path: Path) -> None:
    document = _document(CANDIDATE)
    document["claims"]["track_019_complete"] = True
    with pytest.raises(SuccessorCandidateError, match="claims must remain false"):
        validate(_write(tmp_path, document), ROOT)


def test_rejects_high_risk_successor_bypass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    modes_path = ROOT / "docs/candidates/track-008-successors/dependency-modes.yml"
    modes = _document(modes_path)
    modes["modes"]["clinical_use"]["required_tracks"].pop()
    original = Path.read_text

    def changed(path: Path, *args: object, **kwargs: object) -> str:
        if path.resolve() == modes_path.resolve():
            return yaml.safe_dump(modes, sort_keys=False)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", changed)
    with pytest.raises(SuccessorCandidateError, match="bypasses a successor"):
        validate(CANDIDATE, ROOT)


def test_rejects_unknown_mode_acceptance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    modes_path = ROOT / "docs/candidates/track-008-successors/dependency-modes.yml"
    modes = _document(modes_path)
    modes["default"] = "allow"
    original = Path.read_text

    def changed(path: Path, *args: object, **kwargs: object) -> str:
        if path.resolve() == modes_path.resolve():
            return yaml.safe_dump(modes, sort_keys=False)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", changed)
    with pytest.raises(SuccessorCandidateError, match="default must fail closed"):
        validate(CANDIDATE, ROOT)
