from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_script() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts/check_package_size_policy.py"
    spec = importlib.util.spec_from_file_location("check_package_size_policy", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = _load_script()


def _policy(tmp_path: Path, *, limit: int = 10, digest: str | None = None) -> Path:
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist/wheel.whl").write_bytes(b"wheel")
    (tmp_path / "dist/source.tar.gz").write_bytes(b"source")
    wheel_hash = digest or hashlib.sha256(b"wheel").hexdigest()
    source_hash = hashlib.sha256(b"source").hexdigest()
    policy = tmp_path / "policy.yml"
    policy.write_text(
        f"""schema_version: '0.1.0'
policy_type: synthetic_release_package_size
limits:
  wheel_bytes: {limit}
  sdist_bytes: {limit}
measurement:
  archive_paths:
    wheel: dist/wheel.whl
    sdist: dist/source.tar.gz
  required_hashes:
    wheel: {wheel_hash}
    sdist: {source_hash}
"""
    )
    return policy


def test_policy_accepts_hash_bound_artifacts(tmp_path: Path) -> None:
    result = CHECKER.validate_policy(_policy(tmp_path), root=tmp_path)
    assert result["artifacts"]["wheel"]["bytes"] == 5


def test_policy_accepts_size_only_policy_with_external_hash_binding(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    text = policy.read_text()
    start = text.index("  required_hashes:\n")
    policy.write_text(text[:start])
    result = CHECKER.validate_policy(policy, root=tmp_path)
    assert result["artifacts"]["wheel"]["sha256"] == hashlib.sha256(b"wheel").hexdigest()


def test_policy_rejects_stale_hash(tmp_path: Path) -> None:
    with pytest.raises(CHECKER.PackageSizePolicyError, match="sha256"):
        CHECKER.validate_policy(_policy(tmp_path, digest="f" * 64), root=tmp_path)


def test_policy_rejects_over_budget(tmp_path: Path) -> None:
    with pytest.raises(CHECKER.PackageSizePolicyError, match="exceeds"):
        CHECKER.validate_policy(_policy(tmp_path, limit=4), root=tmp_path)
