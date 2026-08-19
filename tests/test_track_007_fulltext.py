from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "assess_track_007_fulltext", ROOT / "scripts" / "assess_track_007_fulltext.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _documents() -> tuple[bytes, bytes]:
    decisions = []
    observations = []
    for index in range(69):
        key = f"synthetic:{index:02d}"
        url = f"https://example.invalid/{index}"
        decisions.append(
            {
                "canonical_key": key,
                "identifier": key,
                "title": f"Synthetic record {index}",
                "canonical_url": url,
                "decision": "include",
            }
        )
        status = 200 if index < 67 else (403 if index == 67 else 404)
        observations.append(
            {
                "canonical_key": key,
                "requested_url": url,
                "method": "HEAD",
                "checked_at": "2026-08-15T00:00:00+00:00",
                "http_status": status,
                "final_url": url,
                "content_type": "text/html",
                "error": None,
            }
        )
    return (
        json.dumps({"decisions": decisions}).encode(),
        json.dumps({"observations": observations}).encode(),
    )


def test_state_machine_is_fail_closed() -> None:
    screening, observations = _documents()
    result = MODULE.assess(screening, observations)
    assert result["counts"]["eligibility_state"] == {
        "pending_content_assessment": 67,
        "pending_lawful_access": 1,
        "pending_locator_resolution": 1,
    }
    assert result["counts"]["final_decisions"] == 0
    assert result["content_retention"] == "metadata_only_no_abstract_or_full_text_bytes"


def test_hash_bound_resolution_can_exclude_with_registered_reason() -> None:
    screening, observations = _documents()
    resolutions = json.dumps(
        {
            "resolutions": [
                {
                    "canonical_key": "synthetic:00",
                    "decision": "exclude",
                    "exclusion_reason": "not_rare_disease_scope",
                    "evidence_sha256": "sha256:" + "a" * 64,
                }
            ]
        }
    ).encode()
    result = MODULE.assess(screening, observations, resolutions)
    assert result["counts"]["final_decisions"] == 1
    assert result["decisions"][0]["eligibility_state"] == "exclude"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("copyrighted_content", "prohibited copyrighted-content"),
        ("missing_record", "missing locator observations"),
        ("wrong_url", "locator URL does not match"),
    ],
)
def test_invalid_observations_fail_closed(mutation: str, message: str) -> None:
    screening, observations_raw = _documents()
    observations = json.loads(observations_raw)
    if mutation == "copyrighted_content":
        observations["observations"][0]["full_text"] = "synthetic prohibited field"
    elif mutation == "missing_record":
        observations["observations"].pop()
    else:
        observations["observations"][0]["requested_url"] = "https://example.invalid/wrong"
    with pytest.raises(ValueError, match=message):
        MODULE.assess(screening, json.dumps(observations).encode())


def test_invalid_resolution_hash_and_reason_fail_closed() -> None:
    screening, observations = _documents()
    bad_hash = json.dumps(
        {"resolutions": [{"canonical_key": "synthetic:00", "decision": "include"}]}
    ).encode()
    with pytest.raises(ValueError, match="lacks a SHA-256"):
        MODULE.assess(screening, observations, bad_hash)
    bad_reason = json.dumps(
        {
            "resolutions": [
                {
                    "canonical_key": "synthetic:00",
                    "decision": "exclude",
                    "exclusion_reason": "convenience",
                    "evidence_sha256": "sha256:" + "b" * 64,
                }
            ]
        }
    ).encode()
    with pytest.raises(ValueError, match="unsupported exclusion reason"):
        MODULE.assess(screening, observations, bad_reason)


def test_committed_register_is_schema_valid_hash_bound_and_content_free() -> None:
    document = json.loads(
        (ROOT / "docs" / "track-007-fulltext-eligibility-2026-08-15.json").read_text()
    )
    schema = json.loads(
        (ROOT / "schemas" / "track-007-fulltext-eligibility.schema.json").read_text()
    )
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(document)
    assert document["counts"]["retained_input"] == 69
    assert document["counts"]["final_decisions"] == 0
    serialized = json.dumps(document).lower()
    assert '"full_text"' not in serialized
    assert '"abstract"' not in serialized
