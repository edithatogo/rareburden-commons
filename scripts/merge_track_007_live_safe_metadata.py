#!/usr/bin/env python3
"""Merge prior hash-bound signals with a safe-metadata enrichment pass."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def merge(prior_raw: bytes, enrichment_raw: bytes) -> dict:
    prior = json.loads(prior_raw)
    enrichment = json.loads(enrichment_raw)
    prior_by_key = {item["identifier_key"]: item for item in prior["observations"]}
    if set(prior_by_key) != {item["identifier_key"] for item in enrichment["decisions"]}:
        raise ValueError("prior and enrichment identifier sets differ")
    decisions = []
    for item in enrichment["decisions"]:
        prior_supported = (
            prior_by_key[item["identifier_key"]]["screening_decision"]
            == "include_for_content_assessment"
        )
        safe_supported = item["decision"] == "include"
        decisions.append(
            {
                **item,
                "decision": "include" if prior_supported or safe_supported else "uncertain",
                "reason": "prior_hash_bound_public_signal_preserved"
                if prior_supported
                else item["reason"],
            }
        )
    counts = {
        state: sum(item["decision"] == state for item in decisions)
        for state in ("include", "uncertain")
    }
    return {
        "workflow_version": "RBC-LAND-007-LIVE-SAFE-MERGED-v0.1.0",
        "prior_sha256": "sha256:" + hashlib.sha256(prior_raw).hexdigest(),
        "enrichment_sha256": "sha256:" + hashlib.sha256(enrichment_raw).hexdigest(),
        "counts": counts,
        "content_retention": enrichment["content_retention"],
        "decisions": decisions,
        "limitations": enrichment["limitations"]
        + [
            "Earlier hash-bound public signals are preserved; safe fields may upgrade "
            "but never downgrade them."
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prior", type=Path)
    parser.add_argument("enrichment", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = merge(args.prior.read_bytes(), args.enrichment.read_bytes())
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
