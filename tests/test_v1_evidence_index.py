from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_v1_evidence_index import V1EvidenceIndexError, validate_v1_index

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "manifests/release/v1-evidence-index-2026-08-16.json"


def _payload() -> dict:
    return json.loads(INDEX.read_text(encoding="utf-8"))


def test_all_v1_criteria_are_indexed_without_release_acceptance() -> None:
    assert validate_v1_index(_payload(), ROOT) == {
        "criterion_count": 67,
        "group_count": 12,
        "index_complete": True,
        "release_acceptance_complete": False,
        "pending_release_action_count": 2,
    }


def test_missing_criterion_fails_closed() -> None:
    payload = _payload()
    payload["criterion_groups"][0]["criteria"].pop()
    with pytest.raises(V1EvidenceIndexError, match="coverage mismatch"):
        validate_v1_index(payload, ROOT)


def test_duplicate_criterion_fails_closed() -> None:
    payload = _payload()
    payload["criterion_groups"][0]["criteria"].append("V1-PROD-01")
    with pytest.raises(V1EvidenceIndexError, match="must not be duplicated"):
        validate_v1_index(payload, ROOT)


def test_evidence_hash_drift_fails_closed() -> None:
    payload = _payload()
    payload["evidence_bindings"][0]["sha256"] = "0" * 64
    with pytest.raises(V1EvidenceIndexError, match="evidence hash mismatch"):
        validate_v1_index(payload, ROOT)


def test_unbound_group_evidence_fails_closed() -> None:
    payload = _payload()
    payload["criterion_groups"][0]["evidence"] = ["docs/unbound.md"]
    with pytest.raises(V1EvidenceIndexError, match="must be hash-bound"):
        validate_v1_index(payload, ROOT)


@pytest.mark.parametrize("field", ["release_acceptance_complete", "all_v1_criteria_satisfied"])
def test_index_cannot_be_promoted_to_release_acceptance(field: str) -> None:
    payload = _payload()
    if field in payload:
        payload[field] = True
    else:
        payload["claims"][field] = True
    with pytest.raises(V1EvidenceIndexError, match="must remain"):
        validate_v1_index(payload, ROOT)
