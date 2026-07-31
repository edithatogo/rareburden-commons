#!/usr/bin/env python3
"""Check source/package runtime-asset parity and packaged manifest integrity."""

from __future__ import annotations

import argparse
from pathlib import Path

from rareburden.runtime_assets import verify_runtime_assets
from scripts.sync_runtime_assets import RuntimeAssetSyncError, synchronise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path("src/rareburden/resources/repository"),
    )
    args = parser.parse_args()
    try:
        count = synchronise(args.root, args.destination, check=True)
    except RuntimeAssetSyncError as exc:
        print(str(exc))
        return 1
    failures = verify_runtime_assets(args.destination)
    if failures:
        print("Runtime asset integrity failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Runtime assets passed: {count} canonical file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
