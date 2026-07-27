#!/usr/bin/env python3
"""Check pinned requirements projections against uv.lock."""
from __future__ import annotations

import argparse
import re
import tomllib
from pathlib import Path


class RequirementsExportError(ValueError):
    """Raised when requirements exports are unsafe or stale."""


_NAME_RE = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s;\\]+)")
_HASH_RE = re.compile(r"--hash=sha256:[0-9a-f]{64}")


def _records(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RequirementsExportError(f"Cannot read {path}: {exc}") from exc
    logical: list[str] = []
    buffer = ""
    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        buffer += (" " if buffer else "") + stripped.rstrip("\\").strip()
        if stripped.endswith("\\"):
            continue
        logical.append(buffer)
        buffer = ""
    if buffer:
        logical.append(buffer)
    result: dict[str, str] = {}
    errors: list[str] = []
    for line in logical:
        match = _NAME_RE.match(line)
        if not match:
            errors.append(f"{path}: requirement is not exactly pinned: {line[:80]}")
            continue
        name = re.sub(r"[-_.]+", "-", match.group(1)).lower()
        version = match.group(2)
        if not _HASH_RE.search(line):
            errors.append(f"{path}: {name} has no SHA-256 hash")
        previous = result.get(name)
        if previous is not None and previous != version:
            errors.append(f"{path}: {name} appears with conflicting versions")
        result[name] = version
    if errors:
        raise RequirementsExportError("Requirements export failed:\n- " + "\n- ".join(errors))
    return result


def validate_requirements_exports(root: Path) -> tuple[int, int]:
    try:
        lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RequirementsExportError(f"Cannot read uv.lock: {exc}") from exc
    packages = lock.get("package")
    if not isinstance(packages, list):
        raise RequirementsExportError("uv.lock has no package records")
    locked = {
        re.sub(r"[-_.]+", "-", item["name"]).lower(): item["version"]
        for item in packages
        if isinstance(item, dict) and isinstance(item.get("name"), str) and isinstance(item.get("version"), str)
    }
    production = _records(root / "requirements.txt")
    development = _records(root / "requirements-dev.txt")
    errors: list[str] = []
    for label, records in (("production", production), ("development", development)):
        for name, version in records.items():
            if locked.get(name) != version:
                errors.append(f"{label}: {name}=={version} differs from uv.lock {locked.get(name)!r}")
    if not set(production).issubset(development):
        errors.append("development export does not contain every production dependency")
    if errors:
        raise RequirementsExportError("Requirements export drift:\n- " + "\n- ".join(errors))
    return len(production), len(development)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        prod, dev = validate_requirements_exports(args.root.resolve())
    except RequirementsExportError as exc:
        print(str(exc))
        return 1
    print(f"Requirements exports passed: {prod} production, {dev} development packages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
