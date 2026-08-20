#!/usr/bin/env python3
"""Resolve Track 007 live records within the approved metadata-only scope."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def resolve(raw: bytes) -> dict[str, Any]:
    source = json.loads(raw)
    decisions = source.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("source decisions must be a non-empty list")

    identifiers: set[str] = set()
    resolutions: list[dict[str, Any]] = []
    for item in decisions:
        identifier = item.get("identifier_key")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("every decision requires identifier_key")
        if identifier in identifiers:
            raise ValueError(f"duplicate identifier_key: {identifier}")
        identifiers.add(identifier)

        evidence_sha256 = item.get("response_sha256") or item.get("evidence_sha256")
        if not isinstance(evidence_sha256, str) or not evidence_sha256.startswith("sha256:"):
            raise ValueError(f"{identifier} lacks a response evidence hash")

        decision = item.get("decision")
        if decision == "include":
            resolution = "include_bounded_adjacency"
            reason = "explicit_public_metadata_scope_or_contribution_signal"
        elif decision == "uncertain":
            resolution = "not_assessable_in_bounded_public_metadata_scope"
            reason = "insufficient_lawful_public_metadata_no_exclusion_or_absence_inference"
        else:
            raise ValueError(f"{identifier} has unsupported decision: {decision}")

        resolutions.append(
            {
                "identifier_key": identifier,
                "identifier": item.get("identifier"),
                "title": item.get("title"),
                "canonical_url": item.get("canonical_url"),
                "evidence_sha256": evidence_sha256,
                "resolution": resolution,
                "reason": reason,
            }
        )

    counts = {
        state: sum(item["resolution"] == state for item in resolutions)
        for state in (
            "include_bounded_adjacency",
            "not_assessable_in_bounded_public_metadata_scope",
        )
    }
    if counts != {
        "include_bounded_adjacency": 54,
        "not_assessable_in_bounded_public_metadata_scope": 90,
    }:
        raise ValueError(f"unexpected bounded resolution counts: {counts}")

    return {
        "schema_version": "RBC-LAND-007-BOUNDED-CONTENT-v0.1.0",
        "source_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
        "scope": "minimal_public_metadata_only",
        "counts": counts,
        "resolutions": resolutions,
        "content_retention": "identifiers_titles_urls_and_hashes_only",
        "interpretation": {
            "include_bounded_adjacency": "eligible only for the bounded adjacency map",
            "not_assessable_in_bounded_public_metadata_scope": (
                "terminal for this bounded pass; not an exclusion, absence, quality, "
                "or novelty finding"
            ),
        },
        "prohibited_claims": [
            "comprehensive_coverage",
            "representativeness",
            "confirmed_novelty",
            "community_approval",
            "partnership_or_endorsement",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rendered = json.dumps(resolve(args.source.read_bytes()), indent=2) + "\n"
    try:
        with args.output.open("x", encoding="utf-8", errors="strict") as stream:
            stream.write(rendered)
    except FileExistsError as exc:
        raise ValueError(f"refusing to overwrite {args.output}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
