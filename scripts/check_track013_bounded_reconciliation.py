#!/usr/bin/env python3
"""Validate Track 013's bounded synthetic downstream reconciliation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


class ReconciliationError(ValueError):
    """Raised when bounded evidence is missing or overclaimed."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _lookup(value: Any, dotted_path: str) -> Any:
    current = value
    for component in dotted_path.split("."):
        if not isinstance(current, dict) or component not in current:
            raise ReconciliationError(f"missing assertion path: {dotted_path}")
        current = current[component]
    return current


def validate_reconciliation(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    if manifest.get("scope") != "bounded_synthetic_quality_gap_equity_reconciliation":
        raise ReconciliationError("Track 013 scope must remain bounded and synthetic")
    dependencies = manifest.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies:
        raise ReconciliationError("dependencies must be a non-empty list")
    seen_tracks: set[str] = set()
    for dependency in dependencies:
        track = str(dependency.get("track", ""))
        if track in seen_tracks:
            raise ReconciliationError(f"duplicate dependency track: {track}")
        seen_tracks.add(track)
        relative = Path(str(dependency.get("artifact", "")))
        if relative.is_absolute() or ".." in relative.parts:
            raise ReconciliationError(f"unsafe dependency path: {relative}")
        path = root / relative
        if not path.is_file():
            raise ReconciliationError(f"missing dependency artifact: {relative}")
        expected = str(dependency.get("sha256", ""))
        if len(expected) != 64 or _sha256(path) != expected:
            raise ReconciliationError(f"dependency hash mismatch: {relative}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        for dotted_path, expected_value in dependency.get("required_assertions", {}).items():
            if _lookup(payload, str(dotted_path)) != expected_value:
                raise ReconciliationError(f"unsafe dependency assertion: {relative}:{dotted_path}")
    required_tracks = {"008", "009", "010", "011", "012"}
    if seen_tracks != required_tracks:
        raise ReconciliationError("dependency set must bind Tracks 008 through 012 exactly")

    claims = manifest.get("claims", {})
    prohibited_true = sorted(
        key
        for key in (
            "empirical_validation",
            "coverage_sufficiency",
            "representativeness",
            "subgroup_equity_interpretation",
            "independent_reproduction",
            "atlas_release_readiness",
        )
        if claims.get(key) is not False
    )
    if prohibited_true:
        raise ReconciliationError("claims must remain false: " + ", ".join(prohibited_true))
    gates = manifest.get("pending_gates", [])
    required_gates = {
        "real_coverage_and_representativeness",
        "subgroup_and_equity_interpretation",
        "owner_quality_disposition",
        "independent_reproduction",
    }
    if set(gates) != required_gates:
        raise ReconciliationError("all qualifying Track 013 gates must remain pending")
    return {
        "status": "bounded_synthetic_reconciliation_valid",
        "dependency_count": len(dependencies),
        "tracks": sorted(seen_tracks),
        "empirical_rows": 0,
        "pending_gate_count": len(gates),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path())
    args = parser.parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    print(json.dumps(validate_reconciliation(payload, args.root.resolve()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
