#!/usr/bin/env python3
"""Finalize only explicit live public-metadata signals; retain uncertainty."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def finalize(raw: bytes) -> dict:
    source = json.loads(raw)
    decisions = []
    for item in source["observations"]:
        supported = (
            item["screening_decision"] == "include_for_content_assessment"
            and item["scope_signal"] is True
            and item["contribution_signal"] is True
        )
        decisions.append(
            {
                "identifier_key": item["identifier_key"],
                "identifier": item["identifier"],
                "title": item["title"],
                "canonical_url": item["canonical_url"],
                "evidence_sha256": item["response_sha256"],
                "decision": "include" if supported else "uncertain",
                "reason": "explicit_public_metadata_scope_and_contribution_signals"
                if supported
                else "public_metadata_insufficient_for_final_eligibility",
            }
        )
    counts = {
        state: sum(d["decision"] == state for d in decisions) for state in ("include", "uncertain")
    }
    return {
        "workflow_version": "RBC-LAND-007-LIVE-FINAL-v0.1.0",
        "source_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
        "content_retention": "minimal_metadata_and_hashes_only",
        "counts": counts,
        "decisions": decisions,
        "limitations": [
            "Include is adjacency eligibility only, not quality or novelty.",
            "Uncertain records are not excluded.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(finalize(args.source.read_bytes()), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
