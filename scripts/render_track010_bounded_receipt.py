#!/usr/bin/env python3
"""Render the exact dependency-bound Track 010 synthetic assurance receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rareburden.burden_assurance import run_bounded_synthetic_analysis
from rareburden.ledger import load_ledger
from rareburden.schema import load_mapping


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--created-at", default="2026-08-16T00:00:00Z")
    args = parser.parse_args()
    root = args.root
    result = run_bounded_synthetic_analysis(
        load_mapping(root / "examples/analyses/expected-population-synthetic.yml"),
        load_ledger(
            root / "examples/ledger/public-foundation-synthetic.yml",
            root / "schemas/parameter-ledger.schema.json",
        ),
        load_mapping(root / "manifests/ledger/track-009-source-release-bindings-2026-08-16.json"),
        load_mapping(root / "docs/track-010-bounded-quality-disposition-2026-08-16.yml"),
        created_at=args.created_at,
    )
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
