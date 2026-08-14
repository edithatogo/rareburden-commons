#!/usr/bin/env python3
"""Fail-closed validation of release artifact size budgets and optional hashes."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from rareburden.schema import load_document


class PackageSizePolicyError(RuntimeError):
    """Raised when package-size evidence is missing, stale or over budget."""


def _file(path: Path, label: str) -> tuple[int, str]:
    if path.is_symlink() or not path.is_file():
        raise PackageSizePolicyError(f"{label} is not a regular file: {path}")
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def validate_policy(policy_path: Path, *, root: Path) -> dict[str, Any]:
    policy = load_document(policy_path)
    if (
        policy.get("schema_version") != "0.1.0"
        or policy.get("policy_type") != "synthetic_release_package_size"
    ):
        raise PackageSizePolicyError("unsupported package-size policy schema")
    limits = policy.get("limits")
    measurement = policy.get("measurement")
    if not isinstance(limits, dict) or not isinstance(measurement, dict):
        raise PackageSizePolicyError("policy limits and measurement are required")
    paths = measurement.get("archive_paths")
    hashes = measurement.get("required_hashes")
    if not isinstance(paths, dict) or (hashes is not None and not isinstance(hashes, dict)):
        raise PackageSizePolicyError("archive paths are required and hashes must be a mapping")
    results: dict[str, Any] = {
        "schema_version": "0.1.0",
        "policy": policy_path.name,
        "artifacts": {},
    }
    for kind, limit_key in (("wheel", "wheel_bytes"), ("sdist", "sdist_bytes")):
        relative = paths.get(kind)
        expected = hashes.get(kind) if isinstance(hashes, dict) else None
        limit = limits.get(limit_key)
        if not isinstance(relative, str) or not isinstance(limit, int):
            raise PackageSizePolicyError(f"invalid {kind} policy entry")
        if expected is not None and not isinstance(expected, str):
            raise PackageSizePolicyError(f"invalid {kind} hash entry")
        path = (root / relative).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError as exc:
            raise PackageSizePolicyError(f"{kind} path escapes repository") from exc
        size, digest = _file(path, kind)
        if expected is not None and digest != expected:
            raise PackageSizePolicyError(f"{kind} sha256 does not match policy")
        if size > limit:
            raise PackageSizePolicyError(f"{kind} exceeds package-size budget")
        results["artifacts"][kind] = {
            "path": relative,
            "bytes": size,
            "sha256": digest,
            "limit_bytes": limit,
        }
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("policy", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        print(validate_policy(args.policy, root=args.root.resolve()))
    except (OSError, KeyError, PackageSizePolicyError) as exc:
        print(f"Package-size policy failed: {exc}")
        return 1
    print("Package-size policy passed; installed and wheelhouse budgets are measured separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
