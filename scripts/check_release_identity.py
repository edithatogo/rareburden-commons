#!/usr/bin/env python3
"""Validate consistent software version, canonical tag and release identity."""

from __future__ import annotations

import argparse
import re
import subprocess
import tomllib
from pathlib import Path


class ReleaseIdentityError(ValueError):
    """Raised when release identifiers drift."""


_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:(a|b|rc)(\d+))?$")


def canonical_tag(version: str) -> str:
    match = _VERSION_RE.fullmatch(version)
    if not match:
        raise ReleaseIdentityError("version must be X.Y.Z with optional aN, bN or rcN suffix")
    major, minor, patch, kind, serial = match.groups()
    base = f"v{major}.{minor}.{patch}"
    return base if kind is None else f"{base}-{kind}.{serial}"


def _project_version(root: Path) -> str:
    try:
        data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        value = data["project"]["version"]
    except (OSError, tomllib.TOMLDecodeError, KeyError, TypeError) as exc:
        raise ReleaseIdentityError(f"Cannot read project version: {exc}") from exc
    if not isinstance(value, str):
        raise ReleaseIdentityError("project.version must be a string")
    return value


def _source_version(root: Path) -> str:
    path = root / "src/rareburden/__init__.py"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReleaseIdentityError(f"Cannot read source version: {exc}") from exc
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    if not match:
        raise ReleaseIdentityError("Source __version__ is missing")
    return match.group(1)


def validate_release_identity(
    root: Path, *, tag: str | None = None, require_git: bool = True
) -> str:
    root = root.resolve()
    project = _project_version(root)
    source = _source_version(root)
    if source != project:
        raise ReleaseIdentityError(f"Source version {source} does not match project {project}")
    expected_tag = canonical_tag(project)
    if tag is not None and tag != expected_tag:
        raise ReleaseIdentityError(f"Tag {tag} does not match canonical tag {expected_tag}")
    changelog = root / "CHANGELOG.md"
    try:
        text = changelog.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReleaseIdentityError(f"Cannot read CHANGELOG: {exc}") from exc
    if not re.search(rf"^##\s+\[?{re.escape(project)}\]?\b", text, re.MULTILINE):
        raise ReleaseIdentityError(f"CHANGELOG does not contain release {project}")
    if require_git:
        try:
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
            ).stdout.strip()
            if len(head) != 40:
                raise ReleaseIdentityError("Git HEAD is unavailable")
            status = subprocess.run(
                ["git", "status", "--porcelain=v1"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise ReleaseIdentityError(f"Git identity cannot be verified: {exc}") from exc
        if status:
            raise ReleaseIdentityError("Git work tree is not clean")
        if tag is not None:
            try:
                tagged = subprocess.run(
                    ["git", "rev-list", "-n", "1", tag],
                    cwd=root,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            except (OSError, subprocess.CalledProcessError) as exc:
                raise ReleaseIdentityError(f"Git tag cannot be resolved: {tag}") from exc
            if tagged != head:
                raise ReleaseIdentityError(f"Git tag {tag} does not identify HEAD")
    return project


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--tag")
    parser.add_argument("--no-git", action="store_true")
    args = parser.parse_args()
    try:
        version = validate_release_identity(args.root, tag=args.tag, require_git=not args.no_git)
    except ReleaseIdentityError as exc:
        print(str(exc))
        return 1
    print(f"Release identity passed: {version} ({canonical_tag(version)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
