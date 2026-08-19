#!/usr/bin/env python3
"""Create conservative eligibility resolutions from already-retained metadata.

No network content, abstract, or full-text bytes are fetched or copied.  A
record is resolved only when its retained public description explicitly names
both the rare-disease scope and an allowed contribution type.  Title-only and
ambiguous records remain pending.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCOPE_TERMS = ("rare disease", "rare-disease", "orphanet", "ordo")
CONTRIBUTION_TERMS = (
    "analysis",
    "burden",
    "classification",
    "cost",
    "data",
    "database",
    "dataset",
    "economic",
    "estimate",
    "estimating",
    "infrastructure",
    "measurement",
    "method",
    "model",
    "ontology",
    "platform",
    "prevalence",
    "registries",
    "registry",
    "software",
    "standard",
    "surveillance",
)


def _normalize(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.casefold()).split())


def _evidence_hash(record: dict[str, Any], registry: str, query: str, rank: int) -> str:
    bounded = {
        "registry": registry,
        "query_string": query,
        "rank": rank,
        "identifier": record["identifier"],
        "title": record.get("title", ""),
        "canonical_url": record.get("canonical_url", ""),
        "description": record.get("description", ""),
    }
    raw = json.dumps(bounded, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def resolve(search_results_raw: bytes, screening_raw: bytes) -> dict[str, Any]:
    results = json.loads(search_results_raw)
    screening = json.loads(screening_raw)
    by_occurrence: dict[tuple[str, str, int], dict[str, Any]] = {}
    for result in results["records"]:
        for rank, record in enumerate(result["first_page_records"], start=1):
            key = (result["registry"], result["query_string"], rank)
            if key in by_occurrence:
                raise ValueError(f"duplicate search occurrence: {key}")
            by_occurrence[key] = record

    resolutions: list[dict[str, Any]] = []
    pending_reasons: dict[str, int] = {}
    retained = [item for item in screening["decisions"] if item["decision"] == "include"]
    for decision in retained:
        qualifying: list[tuple[dict[str, Any], dict[str, Any]]] = []
        has_description = False
        for occurrence in decision["occurrences"]:
            key = (
                occurrence["registry"],
                occurrence["query_string"],
                occurrence["rank"],
            )
            record = by_occurrence.get(key)
            if record is None:
                raise ValueError(f"screened occurrence is absent from search results: {key}")
            description = record.get("description", "")
            if description:
                has_description = True
            text = _normalize(str(description))
            if (
                description
                and any(_normalize(term) in text for term in SCOPE_TERMS)
                and any(_normalize(term) in text for term in CONTRIBUTION_TERMS)
            ):
                qualifying.append((occurrence, record))
        if not qualifying:
            reason = "description_insufficient" if has_description else "title_only_metadata"
            pending_reasons[reason] = pending_reasons.get(reason, 0) + 1
            continue
        occurrence, record = qualifying[0]
        resolutions.append(
            {
                "canonical_key": decision["canonical_key"],
                "decision": "include",
                "reason": "public_metadata_explicitly_describes_in_scope_contribution",
                "evidence_sha256": _evidence_hash(
                    record,
                    occurrence["registry"],
                    occurrence["query_string"],
                    occurrence["rank"],
                ),
                "evidence_locator": {
                    "registry": occurrence["registry"],
                    "query_string": occurrence["query_string"],
                    "rank": occurrence["rank"],
                },
            }
        )

    return {
        "resolution_version": "RBC-LAND-007-PUBLIC-METADATA-v0.1.0",
        "scope": "retained_public_description_only_no_new_content_retrieval",
        "search_results_sha256": "sha256:" + hashlib.sha256(search_results_raw).hexdigest(),
        "screening_register_sha256": "sha256:" + hashlib.sha256(screening_raw).hexdigest(),
        "decision_rule": (
            "include only when a retained public description explicitly contains a "
            "registered rare-disease scope term and contribution term"
        ),
        "counts": {
            "retained_records": len(retained),
            "include_resolutions": len(resolutions),
            "pending": len(retained) - len(resolutions),
            "pending_reason": dict(sorted(pending_reasons.items())),
        },
        "resolutions": resolutions,
        "limitations": [
            "No new abstract, description, article body or full-text bytes were "
            "fetched or retained.",
            "A metadata-supported include is an adjacency eligibility decision, "
            "not quality or novelty evidence.",
            "Title-only, ambiguous, restricted and otherwise unassessable records remain pending.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("search_results", type=Path)
    parser.add_argument("screening", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = resolve(args.search_results.read_bytes(), args.screening.read_bytes())
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
