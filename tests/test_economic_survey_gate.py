from __future__ import annotations

import pytest

from rareburden.economic_survey import (
    EconomicSurveyGateError,
    check_collection_gate,
    get_survey_core_specifications,
)


def test_collection_gate_passes_when_fully_authorized() -> None:
    valid_packet = {
        "hrec_irb_approval_id": "HREC-2026-ETH-9941",
        "informed_consent_protocol": {"withdrawal_supported": True, "consent_form_version": "v1.2"},
        "participant_remuneration": {
            "compensated": True,
            "rate_per_hour": 75.0,
            "currency": "AUD",
        },
        "accessibility_and_adaptation_plan": {"approved": True, "plain_language_reviewed": True},
        "custodian_authorization": {"agreement_id": "CUSTODIAN-AGR-2026-08"},
    }
    result = check_collection_gate(valid_packet)
    assert result["gate_status"] == "authorized"
    assert result["hrec_id"] == "HREC-2026-ETH-9941"
    assert result["remuneration_rate"] == 75.0


@pytest.mark.parametrize(
    "missing_or_invalid_field",
    [
        "hrec_irb_approval_id",
        "informed_consent_protocol",
        "participant_remuneration",
        "accessibility_and_adaptation_plan",
        "custodian_authorization",
    ],
)
def test_collection_gate_fails_closed_on_missing_requirements(
    missing_or_invalid_field: str,
) -> None:
    valid_packet = {
        "hrec_irb_approval_id": "HREC-2026-ETH-9941",
        "informed_consent_protocol": {"withdrawal_supported": True},
        "participant_remuneration": {"compensated": True, "rate_per_hour": 75.0},
        "accessibility_and_adaptation_plan": {"approved": True},
        "custodian_authorization": {"agreement_id": "CUSTODIAN-AGR-2026-08"},
    }
    invalid_packet = {k: v for k, v in valid_packet.items() if k != missing_or_invalid_field}
    with pytest.raises(EconomicSurveyGateError, match="Fail-closed collection gate"):
        check_collection_gate(invalid_packet)


def test_collection_gate_rejects_uncompensated_community_labour() -> None:
    packet = {
        "hrec_irb_approval_id": "HREC-2026-ETH-9941",
        "informed_consent_protocol": {"withdrawal_supported": True},
        "participant_remuneration": {"compensated": False, "rate_per_hour": 0.0},
        "accessibility_and_adaptation_plan": {"approved": True},
        "custodian_authorization": {"agreement_id": "CUSTODIAN-AGR-2026-08"},
    }
    with pytest.raises(
        EconomicSurveyGateError, match="uncompensated community labour is strictly prohibited"
    ):
        check_collection_gate(packet)


def test_survey_core_specifications_contains_standard_domains() -> None:
    specs = get_survey_core_specifications()
    assert len(specs) == 5
    domains = {item["domain"] for item in specs}
    assert domains == {
        "out_of_pocket_healthcare",
        "transport_and_travel",
        "informal_caregiver_time",
        "employment_and_productivity",
        "education_impact",
    }
