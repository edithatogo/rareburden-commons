#!/usr/bin/env python3
"""Deduplicate and title/metadata-screen a bounded Track 007 search snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCOPE_TERMS = ("rare disease", "rare-disease", "orphan disease", "orphanet", "ordo")
SELF_IDENTIFIERS = {"edithatogo/rareburden-commons"}


def _normalize_text(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def _canonical_key(registry: str, record: dict[str, Any]) -> str:
    doi = str(record.get("doi", "")).lower().removeprefix("https://doi.org/")
    if doi:
        return f"doi:{doi}"
    return f"{registry}:{str(record['identifier']).lower()}"


def screen(snapshot: dict[str, Any]) -> dict[str, Any]:
    occurrences: list[dict[str, Any]] = []
    for result in snapshot["records"]:
        for rank, record in enumerate(result["first_page_records"], start=1):
            occurrences.append(
                {
                    "registry": result["registry"],
                    "query_string": result["query_string"],
                    "rank": rank,
                    **record,
                }
            )

    grouped: dict[str, list[dict[str, Any]]] = {}
    for occurrence in occurrences:
        key = _canonical_key(occurrence["registry"], occurrence)
        grouped.setdefault(key, []).append(occurrence)

    decisions: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group = grouped[key]
        representative = group[0]
        combined = _normalize_text(
            " ".join(
                str(item.get(field, ""))
                for item in group
                for field in ("title", "description", "identifier")
            )
        )
        if representative["identifier"] in SELF_IDENTIFIERS:
            decision, reason = "exclude", "self_result"
        elif not representative.get("title"):
            decision, reason = "uncertain", "missing_title_metadata"
        elif any(_normalize_text(term) in combined for term in SCOPE_TERMS):
            decision, reason = "include", "rare_disease_scope_signal_in_public_metadata"
        else:
            decision, reason = "exclude", "no_rare_disease_scope_signal_in_public_metadata"
        decisions.append(
            {
                "canonical_key": key,
                "identifier": representative["identifier"],
                "title": representative.get("title", ""),
                "canonical_url": representative["canonical_url"],
                "decision": decision,
                "reason": reason,
                "occurrences": [
                    {
                        "registry": item["registry"],
                        "query_string": item["query_string"],
                        "rank": item["rank"],
                    }
                    for item in group
                ],
            }
        )

    title_groups: dict[str, list[str]] = {}
    for item in decisions:
        normalized_title = _normalize_text(item["title"])
        if normalized_title:
            title_groups.setdefault(normalized_title, []).append(item["canonical_key"])
    potential_entity_duplicates = [
        {"normalized_title": title, "canonical_keys": keys}
        for title, keys in sorted(title_groups.items())
        if len(keys) > 1
    ]

    counts = {
        "discovered_occurrences": len(occurrences),
        "unique_after_exact_identifier_deduplication": len(decisions),
        "exact_duplicate_occurrences_removed": len(occurrences) - len(decisions),
        "screened": len(decisions),
        "included": sum(item["decision"] == "include" for item in decisions),
        "excluded": sum(item["decision"] == "exclude" for item in decisions),
        "uncertain": sum(item["decision"] == "uncertain" for item in decisions),
        "potential_entity_duplicate_groups": len(potential_entity_duplicates),
    }
    return {
        "protocol_version": snapshot["protocol_version"],
        "screening_version": "RBC-LAND-007-SCREEN-v0.2.0",
        "scope": "bounded_first_pages_title_and_public_metadata",
        "source_snapshot_sha256": "sha256:"
        + hashlib.sha256(
            json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "rules": {
            "exact_deduplication": (
                "lower-cased DOI when present, otherwise registry plus identifier"
            ),
            "cross_index_deduplication": "shared DOI only",
            "entity_resolution": "exact normalized titles are flagged, not automatically merged",
            "include": (
                "public title, description or identifier contains a registered "
                "rare-disease scope term"
            ),
            "exclude": "self-result or no rare-disease scope signal in public metadata",
            "uncertain": "missing title metadata",
        },
        "counts": counts,
        "potential_entity_duplicates": potential_entity_duplicates,
        "decisions": decisions,
        "limitations": [
            "This screens only the bounded first pages returned by the recorded public APIs.",
            "Inclusion is for adjacency/full-text review and is not evidence of eligibility, "
            "quality or novelty.",
            "Exact-title clusters are not automatically merged because releases and similarly "
            "titled works may differ.",
            "Provider ranking, query specificity, pagination, language and public-web bias "
            "remain unresolved.",
            "No completeness, novelty, external registration, independent methods review or "
            "patient/community interpretation is claimed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    snapshot_bytes = args.snapshot.read_bytes()
    snapshot = json.loads(snapshot_bytes)
    result = screen(snapshot)
    result["source_snapshot_sha256"] = "sha256:" + hashlib.sha256(snapshot_bytes).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
