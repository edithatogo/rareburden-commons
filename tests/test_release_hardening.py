from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_lockfile import LockfilePolicyError, validate_lockfile
from scripts.check_release_identity import (
    ReleaseIdentityError,
    canonical_tag,
    validate_release_identity,
)


def _write_project(
    root: Path, *, version: str = "0.3.0rc1", host: str = "files.pythonhosted.org"
) -> None:
    (root / "src" / "rareburden").mkdir(parents=True)
    (root / "src" / "rareburden" / "__init__.py").write_text(
        f'__version__ = "{version}"\n', encoding="utf-8"
    )
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "rareburden"\nversion = "{version}"\n', encoding="utf-8"
    )
    (root / "CHANGELOG.md").write_text(f"# Changelog\n\n## {version}\n", encoding="utf-8")
    (root / "uv.lock").write_text(
        f'''version = 1
revision = 3
requires-python = ">=3.11"

[[package]]
name = "dependency"
version = "1.0"
source = {{ registry = "https://pypi.org/simple" }}
sdist = {{ url = "https://{host}/packages/aa/dependency.tar.gz", hash = "sha256:{"0" * 64}" }}
wheels = [{{ url = "https://{host}/packages/aa/dependency.whl", hash = "sha256:{"1" * 64}" }}]

[[package]]
name = "rareburden"
version = "{version}"
source = {{ editable = "." }}
''',
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("version", "tag"),
    [
        ("1.0.0", "v1.0.0"),
        ("0.3.0rc1", "v0.3.0-rc.1"),
        ("2.0.0a4", "v2.0.0-a.4"),
        ("2.0.0b2", "v2.0.0-b.2"),
    ],
)
def test_canonical_tag(version: str, tag: str) -> None:
    assert canonical_tag(version) == tag


def test_canonical_tag_rejects_unsupported_versions() -> None:
    with pytest.raises(ReleaseIdentityError, match=r"must be X\.Y\.Z"):
        canonical_tag("1.0.dev1")


def test_public_lockfile_and_release_identity_without_git(tmp_path: Path) -> None:
    _write_project(tmp_path)
    summary = validate_lockfile(tmp_path / "uv.lock", tmp_path / "pyproject.toml")
    assert summary.package_count == 2
    assert summary.registry_count == 1
    assert summary.distribution_url_count == 2
    assert summary.project_version == "0.3.0rc1"
    assert validate_release_identity(tmp_path, tag="v0.3.0-rc.1", require_git=False) == "0.3.0rc1"


def test_lockfile_rejects_private_registry_credentials_and_version_drift(tmp_path: Path) -> None:
    _write_project(tmp_path, host="127.0.0.1")
    lock = tmp_path / "uv.lock"
    lock.write_text(
        lock.read_text(encoding="utf-8")
        .replace("https://pypi.org/simple", "https://user:secret@example.internal/simple")
        .replace(
            'version = "0.3.0rc1"\nsource = { editable', 'version = "9.9.9"\nsource = { editable'
        ),
        encoding="utf-8",
    )
    with pytest.raises(LockfilePolicyError) as captured:
        validate_lockfile(lock, tmp_path / "pyproject.toml")
    message = str(captured.value)
    assert "credentials are forbidden" in message
    assert "private or local host" in message
    assert "does not match pyproject" in message


def test_release_identity_rejects_tag_source_and_changelog_mismatch(tmp_path: Path) -> None:
    _write_project(tmp_path)
    with pytest.raises(ReleaseIdentityError, match="canonical tag"):
        validate_release_identity(tmp_path, tag="v0.3.0", require_git=False)

    source = tmp_path / "src" / "rareburden" / "__init__.py"
    source.write_text('__version__ = "0.3.0rc2"\n', encoding="utf-8")
    with pytest.raises(ReleaseIdentityError, match="does not match project"):
        validate_release_identity(tmp_path, tag="v0.3.0-rc.1", require_git=False)

    source.write_text('__version__ = "0.3.0rc1"\n', encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    with pytest.raises(ReleaseIdentityError, match="CHANGELOG"):
        validate_release_identity(tmp_path, tag="v0.3.0-rc.1", require_git=False)


def test_lockfile_rejects_invalid_documents(tmp_path: Path) -> None:
    bad = tmp_path / "uv.lock"
    bad.write_text("not valid = [", encoding="utf-8")
    with pytest.raises(LockfilePolicyError, match="Cannot read"):
        validate_lockfile(bad)

    bad.write_text(json.dumps({"package": []}), encoding="utf-8")
    with pytest.raises(LockfilePolicyError, match="Cannot read"):
        validate_lockfile(bad)
