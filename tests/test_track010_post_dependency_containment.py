from __future__ import annotations

import copy
from pathlib import Path

import pytest

from scripts.check_track010_post_dependency_candidate import (
    Track010PostDependencyError,
    validate,
)

ROOT = Path(__file__).parents[1]


def test_corrected_post_dependency_candidate_is_contained() -> None:
    validate(ROOT)


def test_corrected_candidate_rejects_authority_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    import scripts.check_track010_post_dependency_candidate as checker

    original = checker._load_json

    def drifted(path: Path) -> dict[str, object]:
        document = copy.deepcopy(original(path))
        if path.name == checker.MANIFEST.name:
            document["claims"]["alpha_interface_frozen"] = True  # type: ignore[index]
        return document

    monkeypatch.setattr(checker, "_load_json", drifted)
    with pytest.raises(Track010PostDependencyError, match="claims escaped"):
        validate(ROOT)
