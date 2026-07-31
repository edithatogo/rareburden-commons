from __future__ import annotations

from pathlib import Path

import pytest

from rareburden.paths import (
    PathDiscoveryError,
    discover_repository_root,
    is_repository_root,
    packaged_repository_root,
)

ROOT = Path(__file__).resolve().parents[1]


def test_repository_root_is_detected_from_nested_path() -> None:
    assert discover_repository_root(ROOT / "src" / "rareburden") == ROOT
    assert is_repository_root(ROOT)


def test_explicit_environment_root_is_honoured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAREBURDEN_ROOT", str(ROOT))
    assert discover_repository_root(Path("/")) == ROOT


def test_missing_root_has_actionable_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RAREBURDEN_ROOT", raising=False)
    with pytest.raises(PathDiscoveryError, match="--root"):
        discover_repository_root(tmp_path)


def test_packaged_repository_projection_is_valid() -> None:
    packaged = packaged_repository_root()
    assert packaged is not None
    assert is_repository_root(packaged)
