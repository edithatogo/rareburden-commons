#!/usr/bin/env python3
"""Render the deterministic Track 012 bounded synthetic receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rareburden.demonstrators import reconcile_paediatric_synthetic_linkage
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    bindings = load_mapping(ROOT / "docs/track-012-dependency-bindings-2026-08-16.yml")
    for item in bindings["dependencies"]:
        observed = hashlib.sha256((ROOT / item["artifact"]).read_bytes()).hexdigest()
        if observed != item["sha256"]:
            raise SystemExit(f"dependency hash mismatch: {item['artifact']}")
    receipt = reconcile_paediatric_synthetic_linkage(
        load_mapping(ROOT / "examples/paediatric/linked-data-synthetic.yml"),
        bindings,
        disclosure_threshold=2,
        created_at="2026-08-16T00:00:00Z",
    )
    output = ROOT / "manifests/demonstrators/track-012-bounded-synthetic-receipt-2026-08-16.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
