#!/usr/bin/env python3
"""Validate Track 014 dependency bindings and fail-closed release claims."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


class ReleaseSurfaceError(ValueError):
    """Raised when Track 014's bounded release contract is unsafe."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_release_surface_manifest(payload: dict[str, Any], root: Path) -> dict[str, Any]:
    if payload.get("scope") != "synthetic_static_package_api_lifecycle_reconciliation":
        raise ReleaseSurfaceError("release surface scope must remain synthetic")
    dependencies = payload.get("dependency_artifacts", [])
    tracks: set[str] = set()
    for item in dependencies:
        track = str(item.get("track", ""))
        if track in tracks:
            raise ReleaseSurfaceError(f"duplicate dependency track: {track}")
        tracks.add(track)
        relative = Path(str(item.get("artifact", "")))
        if relative.is_absolute() or ".." in relative.parts:
            raise ReleaseSurfaceError(f"unsafe dependency path: {relative}")
        path = root / relative
        if not path.is_file() or _sha256(path) != item.get("sha256"):
            raise ReleaseSurfaceError(f"dependency hash mismatch: {relative}")
    if tracks != {"008", "009", "010", "011", "012", "013"}:
        raise ReleaseSurfaceError("release surface must bind Tracks 008 through 013 exactly")
    claims = payload.get("claims", {})
    prohibited = {
        "real_source_activation",
        "accessibility_approved",
        "independent_reproduction",
        "release_authority_approval",
        "public_release",
        "stable_release",
    }
    unsafe = sorted(key for key in prohibited if claims.get(key) is not False)
    if unsafe:
        raise ReleaseSurfaceError("release claims must remain false: " + ", ".join(unsafe))
    required_gates = {
        "real_source_activation",
        "accessibility_review",
        "independent_reproduction",
        "release_authority",
        "public_and_stable_release",
    }
    if set(payload.get("pending_gates", [])) != required_gates:
        raise ReleaseSurfaceError("all release gates must remain pending")
    return {
        "status": "bounded_release_surface_valid",
        "tracks": sorted(tracks),
        "publication_authorized": False,
        "pending_gate_count": len(required_gates),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path())
    args = parser.parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    print(
        json.dumps(validate_release_surface_manifest(payload, args.root.resolve()), sort_keys=True)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
