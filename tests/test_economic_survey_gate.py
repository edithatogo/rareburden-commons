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
    assert result["gate_status"] == "prerequisites_declared"
    assert result["collection_authorized"] is False
    assert result["approval_authenticity_verified"] is False
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


@pytest.mark.parametrize(
    "field,value",
    [
        ("withdrawal", "false"),
        ("compensated", "false"),
        ("approved", "false"),
        ("rate", float("nan")),
        ("rate", float("inf")),
        ("rate", True),
        ("rate", "75"),
        ("rate", 10**1000),
        ("currency", None),
        ("agreement", " "),
    ],
)
def test_collection_declarations_reject_malformed_values(field, value):
    packet = {
        "hrec_irb_approval_id": "HREC-reference",
        "informed_consent_protocol": {"withdrawal_supported": True},
        "participant_remuneration": {"compensated": True, "rate_per_hour": 75, "currency": "AUD"},
        "accessibility_and_adaptation_plan": {"approved": True},
        "custodian_authorization": {"agreement_id": "reference-only"},
    }
    location = {
        "withdrawal": ("informed_consent_protocol", "withdrawal_supported"),
        "compensated": ("participant_remuneration", "compensated"),
        "rate": ("participant_remuneration", "rate_per_hour"),
        "currency": ("participant_remuneration", "currency"),
        "approved": ("accessibility_and_adaptation_plan", "approved"),
        "agreement": ("custodian_authorization", "agreement_id"),
    }
    group, key = location[field]
    packet[group][key] = value
    with pytest.raises(EconomicSurveyGateError):
        check_collection_gate(packet)
