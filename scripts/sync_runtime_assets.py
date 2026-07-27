#!/usr/bin/env python3
"""Synchronise the installable reference-asset projection from canonical files."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


class RuntimeAssetSyncError(ValueError):
    """Raised when runtime assets cannot be projected safely."""


_DIRECTORIES = (
    "catalog",
    "conductor",
    "docs",
    "examples",
    "schemas",
)
_FILES = (
    "pyproject.toml",
    "uv.lock",
)
_EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".git"}
_EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def _source_files(root: Path) -> list[tuple[Path, str]]:
    records: list[tuple[Path, str]] = []
    for relative in _FILES:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise RuntimeAssetSyncError(f"Required runtime source is missing or unsafe: {path}")
        records.append((path, relative))
    for directory in _DIRECTORIES:
        source_root = root / directory
        if source_root.is_symlink() or not source_root.is_dir():
            raise RuntimeAssetSyncError(f"Required runtime source directory is missing or unsafe: {source_root}")
        for path in sorted(source_root.rglob("*"), key=lambda item: item.as_posix()):
            if path.is_symlink() or not path.is_file():
                continue
            relative = path.relative_to(root)
            if any(part in _EXCLUDED_PARTS for part in relative.parts):
                continue
            if path.suffix in _EXCLUDED_SUFFIXES:
                continue
            records.append((path, relative.as_posix()))
    logicals = [logical for _path, logical in records]
    if len(logicals) != len(set(logicals)):
        raise RuntimeAssetSyncError("Runtime source projection contains duplicate paths")
    return sorted(records, key=lambda pair: pair[1])


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_projection(root: Path) -> tuple[dict[str, bytes], dict[str, object]]:
    """Build the exact byte projection and manifest without writing it."""
    projected: dict[str, bytes] = {}
    files: list[dict[str, object]] = []
    for path, logical in _source_files(root):
        data = path.read_bytes()
        projected[logical] = data
        files.append({"path": logical, "sha256": _digest(data), "size_bytes": len(data)})
    manifest: dict[str, object] = {
        "schema_version": "1.0.0",
        "purpose": "Installable, read-only reference assets for offline assurance workflows",
        "file_count": len(files),
        "files": files,
    }
    projected["runtime-assets.json"] = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    return projected, manifest


def _existing_projection(destination: Path) -> dict[str, bytes]:
    if not destination.exists():
        return {}
    return {
        path.relative_to(destination).as_posix(): path.read_bytes()
        for path in destination.rglob("*")
        if path.is_file() and not path.is_symlink()
    }


def synchronise(root: Path, destination: Path, *, check: bool) -> int:
    root = root.resolve()
    destination = destination.resolve()
    projected, manifest = build_projection(root)
    existing = _existing_projection(destination)
    if check:
        missing = sorted(projected.keys() - existing.keys())
        extra = sorted(existing.keys() - projected.keys())
        changed = sorted(
            logical for logical in projected.keys() & existing.keys() if projected[logical] != existing[logical]
        )
        if missing or extra or changed:
            detail = []
            if missing:
                detail.append("missing=" + ",".join(missing))
            if extra:
                detail.append("extra=" + ",".join(extra))
            if changed:
                detail.append("changed=" + ",".join(changed))
            raise RuntimeAssetSyncError("Runtime asset projection has drifted: " + "; ".join(detail))
        return int(manifest["file_count"])

    temporary = destination.with_name(f".{destination.name}.partial")
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir(parents=True)
    try:
        for logical, data in projected.items():
            target = temporary / logical
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        if destination.exists():
            shutil.rmtree(destination)
        temporary.replace(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return int(manifest["file_count"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path("src/rareburden/resources/repository"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    count = synchronise(args.root, args.destination, check=args.check)
    verb = "Verified" if args.check else "Synchronised"
    print(f"{verb} {count} runtime asset(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
