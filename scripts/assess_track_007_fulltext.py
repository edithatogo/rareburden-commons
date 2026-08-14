#!/usr/bin/env python3
"""Build a fail-closed Track 007 full-text eligibility register.

The workflow consumes public locator observations and optional hash-bound
eligibility resolutions.  It never downloads or stores article full text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ALLOWED_DECISIONS = {"include", "exclude", "uncertain"}
EXCLUSION_REASONS = {
    "not_rare_disease_scope",
    "not_initiative_dataset_software_standard_mandate_or_method",
    "duplicate_entity_or_release",
    "insufficient_public_evidence_for_eligibility",
    "retracted_or_withdrawn",
}
PROHIBITED_OBSERVATION_FIELDS = {"body", "content", "full_text", "abstract"}


def _sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _locator_status(observation: dict[str, Any]) -> str:
    status = observation.get("http_status")
    if observation.get("error"):
        return "observation_error"
    if status in {401, 403, 451}:
        return "access_restricted"
    if status in {404, 410}:
        return "not_found"
    if isinstance(status, int) and 200 <= status < 400:
        return "reachable"
    if isinstance(status, int) and (status == 429 or status >= 500):
        return "transient_failure"
    return "unexpected_status"


def assess(
    screening_raw: bytes, observations_raw: bytes, resolutions_raw: bytes | None = None
) -> dict[str, Any]:
    screening = json.loads(screening_raw)
    observations_doc = json.loads(observations_raw)
    retained = {
        item["canonical_key"]: item
        for item in screening["decisions"]
        if item["decision"] == "include"
    }
    if len(retained) != 69:
        raise ValueError(f"expected 69 retained records, found {len(retained)}")

    observations: dict[str, dict[str, Any]] = {}
    for observation in observations_doc["observations"]:
        forbidden = PROHIBITED_OBSERVATION_FIELDS.intersection(observation)
        if forbidden:
            raise ValueError(
                "locator observation contains prohibited copyrighted-content field(s): "
                + ", ".join(sorted(forbidden))
            )
        key = observation["canonical_key"]
        if key in observations:
            raise ValueError(f"duplicate locator observation: {key}")
        if key not in retained:
            raise ValueError(f"locator observation is not a retained record: {key}")
        if observation["requested_url"] != retained[key]["canonical_url"]:
            raise ValueError(f"locator URL does not match screening record: {key}")
        observations[key] = observation
    missing = sorted(set(retained) - set(observations))
    if missing:
        raise ValueError(f"missing locator observations: {', '.join(missing)}")

    resolutions: dict[str, dict[str, Any]] = {}
    if resolutions_raw is not None:
        resolution_doc = json.loads(resolutions_raw)
        for resolution in resolution_doc["resolutions"]:
            key = resolution["canonical_key"]
            if key in resolutions:
                raise ValueError(f"duplicate eligibility resolution: {key}")
            if key not in retained:
                raise ValueError(f"eligibility resolution is not a retained record: {key}")
            decision = resolution["decision"]
            if decision not in ALLOWED_DECISIONS:
                raise ValueError(f"unsupported eligibility decision: {decision}")
            evidence_hash = resolution.get("evidence_sha256", "")
            if re.fullmatch(r"sha256:[0-9a-f]{64}", evidence_hash) is None:
                raise ValueError(f"eligibility resolution lacks a SHA-256 evidence binding: {key}")
            if (
                decision == "exclude"
                and resolution.get("exclusion_reason") not in EXCLUSION_REASONS
            ):
                raise ValueError(f"unsupported exclusion reason: {key}")
            if decision != "exclude" and resolution.get("exclusion_reason"):
                raise ValueError(f"exclusion reason supplied for non-exclusion: {key}")
            resolutions[key] = resolution

    decisions: list[dict[str, Any]] = []
    for key in sorted(retained):
        source = retained[key]
        observation = observations[key]
        locator_status = _locator_status(observation)
        resolution = resolutions.get(key)
        if resolution:
            eligibility_state = resolution["decision"]
            reason = resolution.get("exclusion_reason") or resolution.get("reason")
        elif locator_status == "reachable":
            eligibility_state = "pending_content_assessment"
            reason = "public_locator_reachable_but_content_not_assessed"
        elif locator_status == "access_restricted":
            eligibility_state = "pending_lawful_access"
            reason = "locator_requires_access_not_circumvented"
        else:
            eligibility_state = "pending_locator_resolution"
            reason = "single_bounded_locator_observation_is_not_exclusion_evidence"
        decisions.append(
            {
                "canonical_key": key,
                "identifier": source["identifier"],
                "title": source["title"],
                "canonical_url": source["canonical_url"],
                "locator_status": locator_status,
                "http_status": observation.get("http_status"),
                "final_url": observation.get("final_url"),
                "content_type": observation.get("content_type"),
                "checked_at": observation["checked_at"],
                "eligibility_state": eligibility_state,
                "reason": reason,
                "evidence_sha256": resolution.get("evidence_sha256") if resolution else None,
            }
        )

    states: dict[str, int] = {}
    locators: dict[str, int] = {}
    for decision in decisions:
        states[decision["eligibility_state"]] = states.get(decision["eligibility_state"], 0) + 1
        locators[decision["locator_status"]] = locators.get(decision["locator_status"], 0) + 1
    return {
        "workflow_version": "RBC-LAND-007-FULLTEXT-v0.1.0",
        "scope": "bounded_69_record_locator_and_full_text_eligibility_workflow",
        "source_screening_sha256": _sha256(screening_raw),
        "locator_observations_sha256": _sha256(observations_raw),
        "eligibility_resolutions_sha256": _sha256(resolutions_raw) if resolutions_raw else None,
        "content_retention": "metadata_only_no_abstract_or_full_text_bytes",
        "state_machine": {
            "reachable": "pending_content_assessment",
            "access_restricted": "pending_lawful_access",
            "not_found_or_failure": "pending_locator_resolution",
            "hash_bound_resolution": "include_exclude_or_uncertain",
        },
        "allowed_exclusion_reasons": sorted(EXCLUSION_REASONS),
        "counts": {
            "retained_input": len(retained),
            "locator_status": dict(sorted(locators.items())),
            "eligibility_state": dict(sorted(states.items())),
            "final_decisions": sum(
                states.get(state, 0) for state in ("include", "exclude", "uncertain")
            ),
        },
        "decisions": decisions,
        "limitations": [
            "URL reachability is not content eligibility, scientific quality or novelty evidence.",
            "No abstract or copyrighted full-text bytes are retained in this register.",
            "A failed or restricted locator remains pending and is never automatically excluded.",
            "Final novelty, pagination/completeness, external registration, independent methods "
            "challenge and patient/community interpretation remain pending.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("screening", type=Path)
    parser.add_argument("observations", type=Path)
    parser.add_argument("--resolutions", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    resolutions_raw = args.resolutions.read_bytes() if args.resolutions else None
    result = assess(args.screening.read_bytes(), args.observations.read_bytes(), resolutions_raw)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
