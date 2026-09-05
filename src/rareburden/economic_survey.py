"""Survey core specifications and fail-closed collection gate protocol."""

from __future__ import annotations

from typing import Any


class EconomicSurveyGateError(PermissionError):
    """Raised when survey administration or collection is attempted without verified governance."""


def check_collection_gate(authorization_packet: dict[str, Any] | None) -> dict[str, Any]:
    """Fail-closed gate ensuring survey items cannot be collected without verified governance.

    Requires:
    1. Institutional human research ethics committee (HREC / IRB) approval reference.
    2. Documented participant informed consent and withdrawal protocol.
    3. Fair participant remuneration schedule (no uncompensated community labour).
    4. Accessibility and cultural/linguistic adaptation plan.
    5. Authorized data custodian agreement.

    Raises EconomicSurveyGateError if any required condition is missing or unverified.
    """
    if authorization_packet is None or not isinstance(authorization_packet, dict):
        raise EconomicSurveyGateError(
            "Fail-closed collection gate: "
            "survey collection requires a verified authorization packet."
        )

    hrec = authorization_packet.get("hrec_irb_approval_id")
    if not hrec or not isinstance(hrec, str) or len(hrec.strip()) < 3:
        raise EconomicSurveyGateError(
            "Fail-closed collection gate: missing or invalid HREC / IRB approval identifier."
        )

    consent = authorization_packet.get("informed_consent_protocol")
    if not consent or not isinstance(consent, dict) or not consent.get("withdrawal_supported"):
        raise EconomicSurveyGateError(
            "Fail-closed collection gate: "
            "informed consent protocol with withdrawal support is required."
        )

    remuneration = authorization_packet.get("participant_remuneration")
    if (
        not remuneration
        or not isinstance(remuneration, dict)
        or not remuneration.get("compensated")
        or remuneration.get("rate_per_hour", 0.0) <= 0.0
    ):
        raise EconomicSurveyGateError(
            "Fail-closed collection gate: uncompensated community labour is strictly prohibited."
        )

    accessibility = authorization_packet.get("accessibility_and_adaptation_plan")
    if (
        not accessibility
        or not isinstance(accessibility, dict)
        or not accessibility.get("approved")
    ):
        raise EconomicSurveyGateError(
            "Fail-closed collection gate: "
            "approved accessibility and linguistic adaptation plan required."
        )

    custodian = authorization_packet.get("custodian_authorization")
    if not custodian or not isinstance(custodian, dict) or not custodian.get("agreement_id"):
        raise EconomicSurveyGateError(
            "Fail-closed collection gate: verified data custodian authorization required."
        )

    return {
        "gate_status": "authorized",
        "hrec_id": hrec.strip(),
        "remuneration_rate": remuneration.get("rate_per_hour"),
        "currency": remuneration.get("currency", "AUD"),
        "custodian_agreement_id": custodian.get("agreement_id"),
    }


def get_survey_core_specifications() -> list[dict[str, Any]]:
    """Return the reference patient/family economic and social burden survey core items."""
    return [
        {
            "item_id": "SURV_OOP_01",
            "domain": "out_of_pocket_healthcare",
            "prompt": (
                "In the past 12 months, how much out-of-pocket expenditure did your "
                "household incur for specialist consultations, medications, and diagnostic tests?"
            ),
            "response_type": "currency_amount_bracket",
            "perspective": "household",
            "burden_category": "direct_medical",
        },
        {
            "item_id": "SURV_TRN_02",
            "domain": "transport_and_travel",
            "prompt": (
                "In the past 12 months, what were the total travel, transport, and "
                "accommodation costs associated with attending specialised clinical centres?"
            ),
            "response_type": "currency_amount_bracket",
            "perspective": "household",
            "burden_category": "direct_non_medical",
        },
        {
            "item_id": "SURV_TIME_03",
            "domain": "informal_caregiver_time",
            "prompt": (
                "On an average week, how many hours do family members or unpaid caregivers "
                "spend assisting with daily living, medical therapies, and care coordination?"
            ),
            "response_type": "hours_per_week",
            "perspective": "household",
            "burden_category": "caregiver_time",
        },
        {
            "item_id": "SURV_PROD_04",
            "domain": "employment_and_productivity",
            "prompt": (
                "Have family caregivers reduced work hours, taken unpaid leave, or left "
                "employment due to caregiving responsibilities?"
            ),
            "response_type": "categorical_employment_impact",
            "perspective": "societal",
            "burden_category": "productivity_loss",
        },
        {
            "item_id": "SURV_EDU_05",
            "domain": "education_impact",
            "prompt": (
                "Approximately how many school or vocational training days were missed in "
                "the past academic year due to illness, clinical attendances, or hospitalisations?"
            ),
            "response_type": "days_per_year",
            "perspective": "societal",
            "burden_category": "education_impact",
        },
    ]
