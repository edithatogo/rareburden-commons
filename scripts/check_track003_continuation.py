#!/usr/bin/env python3
"""Validate exact Track 003 continuation evidence without network access."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

EXPECTED = {
    "track-003-licensed-pathway-evidence-2026-08-30.yml": (
        "f09530090f6179ac6ec85ebb5cf2e4433ffe346854a93b43045947d71b63b619"
    ),
    "track-003-transport-sensitivity-contract-2026-08-30.yml": (
        "f5c64fe243a9be72b712581c188bd9c7a84ca8d3c16ce27030b781fcf6dda1cd"
    ),
    "track-003-evidence-gap-register-2026-08-30.yml": (
        "7cfe48bb60afb59d0ccff5a2ad12c47efea3a00a28346bafab7b940dcb79e58a"
    ),
}


def validate(path: Path) -> None:
    """Pin every fact, source term, mechanism, gap and authority boundary."""
    if path.name not in EXPECTED:
        raise ValueError("unregistered continuation document")
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("continuation document must be a mapping")
    payload = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if hashlib.sha256(payload.encode("utf-8")).hexdigest() != EXPECTED[path.name]:
        raise ValueError("continuation evidence or boundary drift; exact review required")
    if any(value is not False for value in document["authority_boundaries"].values()):
        raise ValueError("continuation authority escalation")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root
    for name in EXPECTED:
        validate(root / "docs" / name)
    print("Track 003 continuation evidence passed; parameters and execution remain disabled")


if __name__ == "__main__":
    main()
