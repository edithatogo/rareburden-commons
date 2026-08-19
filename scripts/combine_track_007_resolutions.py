#!/usr/bin/env python3
"""Combine non-overlapping Track 007 resolution evidence documents."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def combine(
    paths_and_raw: list[tuple[str, bytes]], *, override_later: bool = False
) -> dict[str, Any]:
    by_key: dict[str, dict[str, Any]] = {}
    sources: list[dict[str, str]] = []
    for path, raw in paths_and_raw:
        document = json.loads(raw)
        sources.append({"path": path, "sha256": "sha256:" + hashlib.sha256(raw).hexdigest()})
        for resolution in document["resolutions"]:
            key = resolution["canonical_key"]
            if key in by_key and not override_later:
                raise ValueError(f"duplicate resolution across inputs: {key}")
            by_key[key] = resolution
    return {
        "resolution_version": "RBC-LAND-007-COMBINED-v0.1.0",
        "scope": "combined_non_overlapping_hash_bound_public_metadata_resolutions",
        "sources": sources,
        "resolutions": sorted(by_key.values(), key=lambda item: item["canonical_key"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--override-later", action="store_true")
    args = parser.parse_args()
    result = combine(
        [(str(path), path.read_bytes()) for path in args.inputs],
        override_later=args.override_later,
    )
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
