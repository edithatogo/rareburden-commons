#!/usr/bin/env python3
"""Resolve Track 007 live records within the approved metadata-only scope."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == len("sha256:") + 64
        and value.startswith("sha256:")
        and all(character in "0123456789abcdef" for character in value[7:])
    )


def resolve(raw: bytes) -> dict[str, Any]:
    source = json.loads(raw)
    if not isinstance(source, dict):
        raise ValueError("source must be a JSON object")
    decisions = source.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("source decisions must be a non-empty list")

    identifiers: set[str] = set()
    resolutions: list[dict[str, Any]] = []
    for item in decisions:
        if not isinstance(item, dict):
            raise ValueError("every decision must be a JSON object")
        identifier = item.get("identifier_key")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("every decision requires identifier_key")
        if identifier in identifiers:
            raise ValueError(f"duplicate identifier_key: {identifier}")
        identifiers.add(identifier)

        evidence_sha256 = item.get("response_sha256") or item.get("evidence_sha256")
        if not _is_sha256(evidence_sha256):
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

        resolved = {
            "identifier_key": identifier,
            "identifier": item.get("identifier"),
            "title": item.get("title"),
            "canonical_url": item.get("canonical_url"),
            "evidence_sha256": evidence_sha256,
            "resolution": resolution,
            "reason": reason,
        }
        if decision == "uncertain":
            has_signal = bool(item.get("scope_signal") or item.get("contribution_signal"))
            resolved["future_assessment_priority"] = (
                "tier_1_explicit_safe_metadata_signal"
                if has_signal
                else "tier_2_no_explicit_safe_metadata_signal"
            )
            resolved["future_assessment_basis"] = (
                "scope_or_contribution_signal_requires_lawful_substantive_confirmation"
                if has_signal
                else "no_safe_metadata_signal_requires_lawful_substantive_evidence"
            )
        resolutions.append(resolved)

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

    priority_counts = {
        tier: sum(item.get("future_assessment_priority") == tier for item in resolutions)
        for tier in (
            "tier_1_explicit_safe_metadata_signal",
            "tier_2_no_explicit_safe_metadata_signal",
        )
    }
    if priority_counts != {
        "tier_1_explicit_safe_metadata_signal": 46,
        "tier_2_no_explicit_safe_metadata_signal": 44,
    }:
        raise ValueError(f"unexpected future-assessment priority counts: {priority_counts}")

    return {
        "schema_version": "RBC-LAND-007-BOUNDED-CONTENT-v0.2.0",
        "source_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
        "scope": "minimal_public_metadata_only",
        "counts": counts,
        "future_assessment_priority_counts": priority_counts,
        "resolutions": resolutions,
        "content_retention": "identifiers_titles_urls_and_hashes_only",
        "interpretation": {
            "include_bounded_adjacency": "eligible only for the bounded adjacency map",
            "not_assessable_in_bounded_public_metadata_scope": (
                "terminal for this bounded pass; not an exclusion, absence, quality, "
                "or novelty finding; uncertainty remains eligible for a later lawful "
                "substantive assessment"
            ),
        },
        "priority_policy": {
            "purpose": "order later lawful substantive assessment without changing decisions",
            "tier_1": "records with an explicit safe-metadata scope or contribution signal",
            "tier_2": "records without either explicit safe-metadata signal",
            "not_used_as_proxies": [
                "repository_programming_language_as_content_language",
                "title_language_as_study_language",
                "author_or_publisher_affiliation_as_study_geography",
                "provider_presence_as_representativeness",
            ],
        },
        "prohibited_claims": [
            "systematic_or_comprehensive_search",
            "global_or_geographic_representativeness",
            "comprehensive_coverage",
            "representativeness",
            "confirmed_novelty",
            "community_approval",
            "patient_or_community_endorsement",
            "partnership_or_endorsement",
            "programme_operation_or_effectiveness",
            "access_or_clinical_validity",
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
