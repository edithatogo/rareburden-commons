#!/usr/bin/env python3
"""Validate bounded Track 017 usability/build/reproduction receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class BoundedExerciseError(ValueError):
    """Raised when an exercise receipt overclaims or loses exact identity."""


def validate_exercises(receipt: dict[str, Any]) -> dict[str, Any]:
    commit = receipt.get("candidate_commit", "")
    if len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
        raise BoundedExerciseError("candidate commit must be exact")
    assessments = receipt.get("usability_assessments", [])
    required_roles = {
        "first_time_user_accessibility_agent",
        "node_operator_documentation_agent",
    }
    if {item.get("role") for item in assessments} != required_roles or any(
        item.get("classification") != "agent_advisory_non_independent"
        or item.get("authority_claimed") is not False
        for item in assessments
    ):
        raise BoundedExerciseError("two advisory non-independent agent roles are required")
    candidates = receipt.get("clean_candidates", [])
    if len(candidates) != 2 or {item.get("id") for item in candidates} != {
        "candidate-a",
        "candidate-b",
    }:
        raise BoundedExerciseError("exactly two clean candidate receipts are required")
    output_hashes = {item.get("output_manifest_sha256") for item in candidates}
    verification_hashes = {item.get("verification_report_sha256") for item in candidates}
    if len(output_hashes) != 1 or len(verification_hashes) != 1:
        raise BoundedExerciseError("clean candidate outputs must be equivalent")
    owner = receipt.get("owner_operated_reproduction", {})
    if owner.get("classification") != "repository_owner_operated_non_independent":
        raise BoundedExerciseError("owner reproduction must remain non-independent")
    if owner.get("equivalent_to_clean_candidates") is not True:
        raise BoundedExerciseError("owner reproduction equivalence is required")
    if owner.get("output_manifest_sha256") not in output_hashes:
        raise BoundedExerciseError("owner reproduction output hash differs")
    unsafe = sorted(key for key, value in receipt.get("claims", {}).items() if value is not False)
    if unsafe:
        raise BoundedExerciseError("all unavailable authority and release claims must remain false")
    return {
        "candidate_commit": commit,
        "usability_assessment_count": len(assessments),
        "clean_candidate_count": len(candidates),
        "owner_reproduction": "passed_non_independent",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.receipt.read_text(encoding="utf-8"))
    print(json.dumps(validate_exercises(payload), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
