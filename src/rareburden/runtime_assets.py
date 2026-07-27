"""Read-only integrity verification for packaged repository reference assets."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


def verify_runtime_assets(root: Path) -> list[str]:
    failures: list[str] = []
    requested = root.expanduser()
    if requested.is_symlink() or not requested.is_dir():
        return [f"runtime asset root is missing or unsafe: {root}"]
    resolved = requested.resolve()
    manifest_path = resolved / "runtime-assets.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        return ["runtime-assets.json is missing or unsafe"]
    try:
        manifest: Any = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"runtime asset manifest cannot be read: {exc}"]
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        return ["runtime asset manifest is malformed"]
    expected: set[str] = {"runtime-assets.json"}
    seen: set[str] = set()
    for index, record in enumerate(manifest["files"]):
        if not isinstance(record, dict):
            failures.append(f"runtime asset record {index} is malformed")
            continue
        logical = record.get("path")
        if not isinstance(logical, str):
            failures.append(f"runtime asset record {index} lacks path")
            continue
        pure = PurePosixPath(logical)
        if pure.is_absolute() or ".." in pure.parts or not pure.parts:
            failures.append(f"unsafe runtime asset path: {logical}")
            continue
        if logical in seen:
            failures.append(f"duplicate runtime asset path: {logical}")
        seen.add(logical)
        expected.add(logical)
        candidate = resolved.joinpath(*pure.parts)
        if candidate.is_symlink() or not candidate.is_file():
            failures.append(f"runtime asset is missing or unsafe: {logical}")
            continue
        try:
            candidate.resolve().relative_to(resolved)
        except ValueError:
            failures.append(f"runtime asset escapes root: {logical}")
            continue
        data = candidate.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if record.get("sha256") != digest:
            failures.append(f"runtime asset checksum mismatch: {logical}")
        if record.get("size_bytes") != len(data):
            failures.append(f"runtime asset size mismatch: {logical}")
    actual = {
        path.relative_to(resolved).as_posix()
        for path in resolved.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    for logical in sorted(expected - actual):
        failures.append(f"runtime asset missing from projection: {logical}")
    for logical in sorted(actual - expected):
        failures.append(f"unexpected runtime asset: {logical}")
    if manifest.get("file_count") != len(seen):
        failures.append("runtime asset file_count differs from manifest records")
    return sorted(set(failures))


__all__ = ["verify_runtime_assets"]
