from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from scripts.check_track015_bounded_governance import (
    GovernanceReconciliationError,
    validate_governance,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/governance/track-015-bounded-reconciliation-2026-08-16.json"
PATIENT_COMMUNITY_SCOPE = (
    ROOT / "manifests/governance/track-015-patient-community-review-scope-2026-08-20.json"
)
PATIENT_COMMUNITY_ADVICE = (
    ROOT / "docs/track-015-patient-community-governance-advice-2026-08-20.yml"
)
EXTERNAL_GATE_CLOSURE = ROOT / "docs/track-015-external-gate-closure-2026-08-21.yml"
TRACK_METADATA = ROOT / "conductor/archive/015-governance-partnership-policy/metadata.json"


def _payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_single_owner_agent_panel_model_is_bounded() -> None:
    assert validate_governance(_payload(), ROOT) == {
        "status": "bounded_governance_valid",
        "owner_count": 1,
        "relationship_count": 7,
        "pending_acceptance_count": 5,
        "track_014_status": "bound",
    }


def test_agent_panel_cannot_be_promoted_to_independent_authority() -> None:
    payload = _payload()
    payload["operating_model"]["agent_panels_are_advisory"] = False
    with pytest.raises(GovernanceReconciliationError, match="must remain advisory"):
        validate_governance(payload, ROOT)


def test_owner_authority_declaration_is_attributable_and_unpaid() -> None:
    payload = _payload()
    declarations = payload["owner_declarations"]
    assert declarations["repository_data_custodian"] is True
    assert declarations["applicable_indigenous_authority"] is True
    assert declarations["additional_human_review_planned"] is False
    assert declarations["remuneration"] == {"model": "unpaid", "amount": 0}
    declarations["basis"] = "independent_verification"
    with pytest.raises(GovernanceReconciliationError, match="must remain attributable"):
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


def test_patient_community_advice_keeps_non_self_attestable_gates_pending() -> None:
    scope_bytes = PATIENT_COMMUNITY_SCOPE.read_bytes()
    scope = json.loads(scope_bytes)
    advice = yaml.safe_load(PATIENT_COMMUNITY_ADVICE.read_text(encoding="utf-8"))

    assert advice["panel_assurance"] == (
        "advisory_agent_perspective_not_independent_or_human_approval"
    )
    assert advice["reviewed_candidate"]["commit"] == scope["reviewed_commit"]
    assert advice["reviewed_candidate"]["tree"] == scope["reviewed_tree"]
    assert (
        advice["reviewed_candidate"]["scope_manifest_sha256"]
        == hashlib.sha256(scope_bytes).hexdigest()
    )
    assert all(
        gate["status"] == "pending" and gate["self_attestable"] is False
        for gate in advice["external_or_factual_gates_retained"]
    )
    assert advice["owner_disposition"] == {
        "disposition": "accept_narrow_and_defer",
        "authority": "repository_scope_and_implementation_only",
        "recorded_at": "2026-08-20",
        "evidence": "docs/decisions/2026-08-20-owner-patient-community-governance-disposition.md",
        "release_authorized": False,
        "real_or_controlled_data_authorized": False,
        "external_gate_status_changed": False,
    }


def test_historical_dependency_scope_is_preserved_after_bounded_completion() -> None:
    closure = yaml.safe_load(EXTERNAL_GATE_CLOSURE.read_text(encoding="utf-8"))
    metadata = json.loads(TRACK_METADATA.read_text(encoding="utf-8"))

    assert metadata["status"] == "complete"
    assert closure["status"] == "blocked_dependency_only_external_activation_excluded"
    assert closure["track_completion_authorized"] is False
    assert closure["dependency_blockers"] == [
        {
            "track": "013-quality-validation-gap-equity",
            "required_state": "complete",
            "current_state": "blocked",
        }
    ]
    completed = closure["repository_governance_gates_completed"]
    assert len(completed) == 6
    assert all(
        gate["status"].startswith("not_applicable") and gate["self_attestable"] is False
        for gate in closure["conditional_external_fact_gates"]
    )
    assert "independent human review" in closure["prohibited_activation_claims"]
    supersession = closure["bounded_scope_supersession"]
    assert supersession["status"] == "superseded_for_bounded_repository_track_completion"
    assert supersession["conditional_register"] == (
        "docs/track-015-external-activation-register-2026-08-21.yml"
    )


def test_agent_advice_boundary_keeps_only_genuine_external_facts() -> None:
    decision = yaml.safe_load(
        (ROOT / "docs/decisions/2026-08-21-track-015-agent-advice-boundary.yml").read_text(
            encoding="utf-8"
        )
    )
    assert decision["adopted_model"] == {
        "advice": "role_separated_simulated_agents",
        "decision": "repository_owner",
        "independent_or_additional_human_advice_required": False,
        "constituted_governance_body_required": False,
    }
    assert len(decision["repository_gates_reclassified_as_agent_advice"]) == 6
    assert set(decision["external_facts_retained_only_if_activated"]) == {
        "publisher_or_licensor_rights",
        "controlled_data_custodian_permission",
        "confirmed_partnership_or_endorsement",
        "country_node_or_jurisdictional_authority",
        "unrelated_community_or_indigenous_consent_or_representation",
        "unqualified_global_or_representative_claim",
    }
