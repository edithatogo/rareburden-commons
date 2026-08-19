#!/usr/bin/env python3
"""Reconcile the immutable Track 007 live capture without inventing metadata.

The 2026-08-15 capture predates the screening-metadata retention contract and
contains stable identifiers but no titles.  This workflow therefore reuses an
exact identifier match to the frozen first-page snapshot where possible and
leaves every other identifier pending metadata retrieval.  Rank alone is never
used as an identity key.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REGISTRIES = {"github", "zenodo", "huggingface_datasets"}


def _sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _identifier_key(registry: str, identifier: str) -> str:
    if not identifier or not isinstance(identifier, str):
        raise ValueError("capture identifier must be non-empty text")
    return f"{registry}:{identifier.casefold()}"


def reconcile(
    capture_documents: list[tuple[str, bytes]],
    search_results_raw: bytes,
    screening_raw: bytes,
) -> dict[str, Any]:
    search_results = json.loads(search_results_raw)
    screening = json.loads(screening_raw)

    screened_by_occurrence: dict[tuple[str, str, int], dict[str, Any]] = {}
    for decision in screening["decisions"]:
        for occurrence in decision["occurrences"]:
            key = (
                occurrence["registry"],
                occurrence["query_string"],
                occurrence["rank"],
            )
            if key in screened_by_occurrence:
                raise ValueError(f"duplicate frozen screening occurrence: {key}")
            screened_by_occurrence[key] = decision

    snapshot_by_identifier: dict[str, dict[str, Any]] = {}
    for result in search_results["records"]:
        registry = result["registry"]
        if registry not in REGISTRIES:
            continue
        for rank, record in enumerate(result["first_page_records"], start=1):
            occurrence_key = (registry, result["query_string"], rank)
            decision = screened_by_occurrence.get(occurrence_key)
            if decision is None:
                raise ValueError(f"snapshot record lacks screening decision: {occurrence_key}")
            identifier_key = _identifier_key(registry, str(record["identifier"]))
            candidate = {
                "canonical_key": decision["canonical_key"],
                "identifier": str(record["identifier"]),
                "title": decision["title"],
                "canonical_url": decision["canonical_url"],
                "screening_decision": decision["decision"],
                "screening_reason": decision["reason"],
            }
            existing = snapshot_by_identifier.get(identifier_key)
            if existing is not None and existing != candidate:
                raise ValueError(
                    f"snapshot identifier maps to conflicting records: {identifier_key}"
                )
            snapshot_by_identifier[identifier_key] = candidate

    occurrences: dict[str, list[dict[str, Any]]] = {}
    source_captures: list[dict[str, Any]] = []
    seen_registries: set[str] = set()
    occurrence_total = 0
    for path, raw in capture_documents:
        document = json.loads(raw)
        if document.get("status") != "bounded_capture_only":
            raise ValueError(f"capture is not bounded evidence: {path}")
        registries = {capture["registry"] for capture in document["captures"]}
        if len(registries) != 1 or not registries <= REGISTRIES:
            raise ValueError(f"capture has invalid registry scope: {path}")
        registry = next(iter(registries))
        if registry in seen_registries:
            raise ValueError(f"duplicate registry capture: {registry}")
        seen_registries.add(registry)
        captured_here = 0
        for capture in document["captures"]:
            rank = 0
            query_seen: set[str] = set()
            for page in capture["pages"]:
                if page["item_count"] != len(page["identifiers"]):
                    raise ValueError("page item count does not match retained identifiers")
                for identifier in page["identifiers"]:
                    rank += 1
                    captured_here += 1
                    occurrence_total += 1
                    key = _identifier_key(registry, str(identifier))
                    if key in query_seen:
                        raise ValueError(f"identifier repeats within query capture: {key}")
                    query_seen.add(key)
                    occurrences.setdefault(key, []).append(
                        {
                            "registry": registry,
                            "query_string": capture["query_string"],
                            "rank": rank,
                            "identifier": str(identifier),
                        }
                    )
            if rank != capture["occurrences_captured"]:
                raise ValueError("query occurrence count does not reconcile")
        source_captures.append(
            {
                "path": path,
                "sha256": _sha256(raw),
                "registry": registry,
                "occurrences": captured_here,
            }
        )
    if seen_registries != REGISTRIES:
        raise ValueError("one capture is required for every bounded registry")

    records: list[dict[str, Any]] = []
    for identifier_key in sorted(occurrences):
        match = snapshot_by_identifier.get(identifier_key)
        if match:
            record = {
                **match,
                "identifier_key": identifier_key,
                "reconciliation_state": "reconciled_to_frozen_snapshot",
                "occurrences": occurrences[identifier_key],
            }
        else:
            first = occurrences[identifier_key][0]
            record = {
                "identifier_key": identifier_key,
                "identifier": first["identifier"],
                "canonical_key": None,
                "title": None,
                "canonical_url": None,
                "screening_decision": "pending_metadata_retrieval",
                "screening_reason": (
                    "historical capture retained identifiers only; absence of title metadata "
                    "is not exclusion evidence"
                ),
                "reconciliation_state": "pending_metadata_retrieval",
                "occurrences": occurrences[identifier_key],
            }
        records.append(record)

    matched = sum(r["reconciliation_state"] == "reconciled_to_frozen_snapshot" for r in records)
    return {
        "workflow_version": "RBC-LAND-007-LIVE-RECONCILE-v0.1.0",
        "status": "bounded_identifier_reconciliation_complete_metadata_screening_incomplete",
        "source_captures": source_captures,
        "search_results_sha256": _sha256(search_results_raw),
        "screening_register_sha256": _sha256(screening_raw),
        "deduplication_rule": "registry plus case-folded stable identifier",
        "counts": {
            "captured_occurrences": occurrence_total,
            "unique_registry_identifiers": len(records),
            "exact_duplicate_occurrences_removed": occurrence_total - len(records),
            "reconciled_to_frozen_snapshot": matched,
            "pending_metadata_retrieval": len(records) - matched,
        },
        "records": records,
        "limitations": [
            "The historical live capture retained identifiers but not titles or descriptions.",
            "Only exact registry-identifier matches inherit a frozen snapshot decision.",
            "Live-only identifiers remain pending; they are not excluded or evidence of absence.",
            "Cross-provider entity equivalence, content eligibility, coverage and "
            "novelty remain unresolved.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("captures", nargs="+", type=Path)
    parser.add_argument("--search-results", required=True, type=Path)
    parser.add_argument("--screening", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = reconcile(
        [(str(path), path.read_bytes()) for path in args.captures],
        args.search_results.read_bytes(),
        args.screening.read_bytes(),
    )
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
