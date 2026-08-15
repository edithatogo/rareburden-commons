from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.check_track015_bounded_governance import (
    GovernanceReconciliationError,
    validate_governance,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/governance/track-015-bounded-reconciliation-2026-08-16.json"


def _payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_single_owner_agent_panel_model_is_bounded() -> None:
    assert validate_governance(_payload(), ROOT) == {
        "status": "bounded_governance_valid",
        "owner_count": 1,
        "relationship_count": 7,
        "pending_acceptance_count": 6,
        "track_014_status": "bound",
    }


def test_agent_panel_cannot_be_promoted_to_independent_authority() -> None:
    payload = _payload()
    payload["operating_model"]["agent_panels_are_advisory"] = False
    with pytest.raises(GovernanceReconciliationError, match="must remain advisory"):
        validate_governance(payload, ROOT)
    payload = _payload()
    payload["operating_model"]["prohibited_agent_authority_claims"].remove("human_review")
    with pytest.raises(GovernanceReconciliationError, match="all prohibited"):
        validate_governance(payload, ROOT)


def test_relationship_and_governance_overclaims_fail_closed() -> None:
    payload = _payload()
    payload["relationship_register"][0]["state"] = "confirmed"
    with pytest.raises(GovernanceReconciliationError, match="cannot be confirmed"):
        validate_governance(payload, ROOT)
    payload = _payload()
    payload["claims"]["patient_or_community_authority"] = True
    with pytest.raises(GovernanceReconciliationError, match="claims must remain false"):
        validate_governance(payload, ROOT)


def test_rights_evidence_and_withdrawal_triggers_cannot_drift() -> None:
    payload = _payload()
    payload["evidence_bindings"][0]["sha256"] = "0" * 64
    with pytest.raises(GovernanceReconciliationError, match="evidence hash mismatch"):
        validate_governance(payload, ROOT)
    payload = _payload()
    payload["correction_withdrawal_triggers"].remove("source rights or terms change")
    with pytest.raises(GovernanceReconciliationError, match="all correction"):
        validate_governance(payload, ROOT)


def test_track_014_cannot_be_marked_bound_without_exact_hash() -> None:
    payload = copy.deepcopy(_payload())
    payload["integration_dependency"]["sha256"] = "0" * 64
    with pytest.raises(GovernanceReconciliationError, match="Track 014 dependency hash mismatch"):
        validate_governance(payload, ROOT)
