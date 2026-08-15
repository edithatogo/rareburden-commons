from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.check_track017_bounded_readiness import ReleaseReadinessError, validate_readiness

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/release/track-017-bounded-readiness-2026-08-16.json"


def _payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_prepared_readiness_contract_is_bounded() -> None:
    assert validate_readiness(_payload(), ROOT) == {
        "status": "bounded_readiness_preparation_valid",
        "track_016_status": "bound",
        "open_gate_count": 4,
        "prohibited_claim_count": 10,
    }


@pytest.mark.parametrize(
    "claim",
    [
        "independent_reproduction",
        "external_approval",
        "stable_release_authorized",
        "v1_tag_created",
    ],
)
def test_authority_and_release_overclaims_fail_closed(claim: str) -> None:
    payload = _payload()
    payload["claims"][claim] = True
    with pytest.raises(ReleaseReadinessError, match="claims must remain false"):
        validate_readiness(payload, ROOT)


def test_backup_attestation_cannot_be_promoted_to_continuity() -> None:
    payload = _payload()
    payload["owner_and_continuity"]["continuity_evidence_complete"] = True
    with pytest.raises(ReleaseReadinessError, match="cannot be complete"):
        validate_readiness(payload, ROOT)


def test_evidence_drift_fails_closed() -> None:
    payload = _payload()
    payload["evidence_bindings"][0]["sha256"] = "0" * 64
    with pytest.raises(ReleaseReadinessError, match="evidence hash mismatch"):
        validate_readiness(payload, ROOT)


def test_track_016_cannot_be_bound_prematurely() -> None:
    payload = copy.deepcopy(_payload())
    payload["integration_dependency"]["sha256"] = "0" * 64
    with pytest.raises(ReleaseReadinessError, match="dependency hash mismatch"):
        validate_readiness(payload, ROOT)


def test_stable_gate_cannot_close_during_preparation() -> None:
    payload = _payload()
    payload["stable_release_gates"]["public_artifact_verification"] = True
    with pytest.raises(ReleaseReadinessError, match="only executed repository-evidence"):
        validate_readiness(payload, ROOT)
