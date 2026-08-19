from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_track017_bounded_exercises import BoundedExerciseError, validate_exercises

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "manifests/release/track-017-bounded-exercises-2026-08-16.json"


def _payload() -> dict:
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_exact_bounded_exercises_validate() -> None:
    result = validate_exercises(_payload())
    assert result["usability_assessment_count"] == 2
    assert result["clean_candidate_count"] == 2
    assert result["owner_reproduction"] == "passed_non_independent"


@pytest.mark.parametrize(
    "claim",
    [
        "independent_usability",
        "independent_reproduction",
        "backup_continuity",
        "stable_release_authorized",
    ],
)
def test_unavailable_authority_and_release_claims_fail_closed(claim: str) -> None:
    payload = _payload()
    payload["claims"][claim] = True
    with pytest.raises(BoundedExerciseError, match="must remain false"):
        validate_exercises(payload)


def test_agent_assessment_cannot_be_promoted_to_independent() -> None:
    payload = _payload()
    payload["usability_assessments"][0]["classification"] = "independent"
    with pytest.raises(BoundedExerciseError, match="advisory non-independent"):
        validate_exercises(payload)


def test_candidate_hash_mismatch_fails_closed() -> None:
    payload = _payload()
    payload["clean_candidates"][1]["output_manifest_sha256"] = "0" * 64
    with pytest.raises(BoundedExerciseError, match="must be equivalent"):
        validate_exercises(payload)


def test_owner_reproduction_hash_mismatch_fails_closed() -> None:
    payload = _payload()
    payload["owner_operated_reproduction"]["output_manifest_sha256"] = "0" * 64
    with pytest.raises(BoundedExerciseError, match="output hash differs"):
        validate_exercises(payload)
