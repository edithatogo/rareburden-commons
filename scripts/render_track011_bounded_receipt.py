#!/usr/bin/env python3
"""Render the deterministic Track 011 bounded synthetic receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rareburden.demonstrators import reconcile_bronchiectasis_synthetic_profile
from rareburden.schema import load_mapping
from rareburden.semantics import load_hierarchy

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    bindings = load_mapping(ROOT / "docs/track-011-dependency-bindings-2026-08-16.yml")
    for item in bindings["dependencies"]:
        observed = hashlib.sha256((ROOT / item["artifact"]).read_bytes()).hexdigest()
        if observed != item["sha256"]:
            raise SystemExit(f"dependency hash mismatch: {item['artifact']}")
    result = reconcile_bronchiectasis_synthetic_profile(
        load_mapping(ROOT / "examples/demonstrators/011-bounded-synthetic-profile.yml"),
        load_hierarchy(
            ROOT / "examples/semantics/bronchiectasis-synthetic.yml",
            ROOT / "schemas/disease-hierarchy.schema.json",
        ),
        bindings,
        created_at="2026-08-16T00:00:00Z",
    )
    output = ROOT / "manifests/demonstrators/track-011-bounded-synthetic-receipt-2026-08-16.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
