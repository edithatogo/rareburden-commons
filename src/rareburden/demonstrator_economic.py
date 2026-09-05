"""Reference demonstrator economic integration for monogenic diabetes and paediatric burden."""

from __future__ import annotations

from typing import Any

from rareburden.economic_engine import (
    calculate_perspective_burden,
    evaluate_economic_scenarios,
)


def evaluate_monogenic_diabetes_economic_reference(
    synthetic_case_count: float = 8520.0,
    currency: str = "AUD",
    price_year: int = 2024,
) -> dict[str, Any]:
    """Run reference synthetic economic scenario for monogenic diabetes demonstrator.

    Integrates case estimates with explicit synthetic cost components:
    - Specialist outpatient diabetes consults
    - Diagnostic genetic confirmation panels
    - Specialized consumables and glucose monitoring
    - Informal caregiver coordination time
    """
    params = [
        {
            "parameter_id": "mgd_specialist_consults",
            "category": "direct_medical",
            "perspective": "health_system",
            "roles": {
                "payer": {"status": "declared", "entity_label": "Public Health System"},
                "bearer": {"status": "declared", "entity_label": "Specialist Outpatient Clinic"},
                "recipient": {"status": "declared", "entity_label": "Healthcare Providers"},
                "time_provider": {"status": "not_applicable", "entity_label": "N/A"},
                "beneficiary": {"status": "declared", "entity_label": "Monogenic Diabetes Cohort"},
            },
            "population": {
                "id": "australia_modi_cohort",
                "label": "Australian monogenic diabetes cohort",
            },
            "geography": {"id": "aus", "label": "Australia"},
            "observation_period": {"start": "2024-01-01", "end": "2024-12-31"},
            "quantity": {
                "kind": "resource_count",
                "unit": "consultations",
                "denominator_basis": "person_year",
                "measurement_status": "explicit_value",
                "value": synthetic_case_count * 2.0,
            },
            "valuation": {
                "status": "valued",
                "is_transfer": False,
                "currency": currency,
                "price_year": price_year,
                "unit_value": 250.0,
                "total_monetary_value": synthetic_case_count * 2.0 * 250.0,
                "rate_source": "MBS Schedule synthetic analogue 2024",
                "discount_rate": 0.0,
                "discount_convention": "undiscounted",
            },
            "overlap": {
                "assessment_status": "assessed_no_overlap",
                "overlapping_parameter_ids": [],
                "rationale": "Discrete outpatient consultations distinct from genetic testing.",
            },
            "missingness": {
                "status": "complete",
                "rationale": "Synthetic reference scenario values.",
            },
        },
        {
            "parameter_id": "mgd_genetic_sequencing",
            "category": "direct_medical",
            "perspective": "health_system",
            "roles": {
                "payer": {"status": "declared", "entity_label": "Public Health System"},
                "bearer": {"status": "declared", "entity_label": "Genomic Diagnostic Laboratories"},
                "recipient": {"status": "declared", "entity_label": "Laboratory Providers"},
                "time_provider": {"status": "not_applicable", "entity_label": "N/A"},
                "beneficiary": {"status": "declared", "entity_label": "Monogenic Diabetes Cohort"},
            },
            "population": {
                "id": "australia_modi_cohort",
                "label": "Australian monogenic diabetes cohort",
            },
            "geography": {"id": "aus", "label": "Australia"},
            "observation_period": {"start": "2024-01-01", "end": "2024-12-31"},
            "quantity": {
                "kind": "resource_count",
                "unit": "tests",
                "denominator_basis": "incident_cases",
                "measurement_status": "explicit_value",
                "value": synthetic_case_count * 0.1,
            },
            "valuation": {
                "status": "valued",
                "is_transfer": False,
                "currency": currency,
                "price_year": price_year,
                "unit_value": 1200.0,
                "total_monetary_value": synthetic_case_count * 0.1 * 1200.0,
                "rate_source": "Targeted gene panel diagnostic fee 2024",
                "discount_rate": 0.0,
                "discount_convention": "undiscounted",
            },
            "overlap": {
                "assessment_status": "assessed_no_overlap",
                "overlapping_parameter_ids": [],
                "rationale": "One-off diagnostic sequencing.",
            },
            "missingness": {"status": "complete", "rationale": "Synthetic incident testing rate."},
        },
        {
            "parameter_id": "mgd_household_oop_monitoring",
            "category": "direct_non_medical",
            "perspective": "household",
            "roles": {
                "payer": {"status": "declared", "entity_label": "Patient Household"},
                "bearer": {"status": "declared", "entity_label": "Patient Household"},
                "recipient": {"status": "declared", "entity_label": "Pharmacy Retailers"},
                "time_provider": {"status": "not_applicable", "entity_label": "N/A"},
                "beneficiary": {"status": "declared", "entity_label": "Individual Patient"},
            },
            "population": {
                "id": "australia_modi_cohort",
                "label": "Australian monogenic diabetes cohort",
            },
            "geography": {"id": "aus", "label": "Australia"},
            "observation_period": {"start": "2024-01-01", "end": "2024-12-31"},
            "quantity": {
                "kind": "monetary_expenditure",
                "unit": "out_of_pocket_aud",
                "denominator_basis": "person_year",
                "measurement_status": "explicit_value",
                "value": synthetic_case_count * 600.0,
            },
            "valuation": {
                "status": "valued",
                "is_transfer": False,
                "currency": currency,
                "price_year": price_year,
                "total_monetary_value": synthetic_case_count * 600.0,
                "rate_source": "Household monitoring survey synthetic fixture",
                "discount_rate": 0.0,
                "discount_convention": "undiscounted",
            },
            "overlap": {
                "assessment_status": "assessed_no_overlap",
                "overlapping_parameter_ids": [],
                "rationale": "Direct out-of-pocket supplies not reimbursed by PBS.",
            },
            "missingness": {"status": "complete", "rationale": "Synthetic average OOP cost."},
        },
        {
            "parameter_id": "mgd_caregiver_coordination_time",
            "category": "caregiver_time",
            "perspective": "household",
            "roles": {
                "payer": {"status": "not_applicable", "entity_label": "N/A"},
                "bearer": {"status": "declared", "entity_label": "Family Caregivers"},
                "recipient": {
                    "status": "declared",
                    "entity_label": "Monogenic Diabetes Individuals",
                },
                "time_provider": {"status": "declared", "entity_label": "Family Caregivers"},
                "beneficiary": {
                    "status": "declared",
                    "entity_label": "Monogenic Diabetes Individuals",
                },
            },
            "population": {
                "id": "australia_modi_cohort",
                "label": "Australian monogenic diabetes cohort",
            },
            "geography": {"id": "aus", "label": "Australia"},
            "observation_period": {"start": "2024-01-01", "end": "2024-12-31"},
            "quantity": {
                "kind": "time_hours",
                "unit": "hours_per_year",
                "denominator_basis": "person_year",
                "measurement_status": "explicit_value",
                "value": synthetic_case_count * 52.0,
            },
            "valuation": {
                "status": "valued",
                "is_transfer": False,
                "currency": currency,
                "price_year": price_year,
                "unit_value": 35.0,
                "total_monetary_value": synthetic_case_count * 52.0 * 35.0,
                "rate_source": "Opportunity cost wage rate benchmark 2024",
                "discount_rate": 0.0,
                "discount_convention": "undiscounted",
            },
            "overlap": {
                "assessment_status": "assessed_no_overlap",
                "overlapping_parameter_ids": [],
                "rationale": (
                    "Unpaid informal caregiving hours separate from formal clinical appointments."
                ),
            },
            "missingness": {
                "status": "complete",
                "rationale": "Synthetic 1 hour per week caregiving model.",
            },
        },
    ]

    hs_burden = calculate_perspective_burden(params, "health_system")
    hh_burden = calculate_perspective_burden(params, "household")
    soc_burden = calculate_perspective_burden(params, "societal")

    scenarios = evaluate_economic_scenarios(
        params,
        "societal",
        [
            {
                "scenario_id": "high_care_cost",
                "title": "20% higher diagnostic and care coordination costs",
                "cost_multiplier": 1.20,
            },
            {
                "scenario_id": "low_care_cost",
                "title": "20% lower diagnostic and care coordination costs",
                "cost_multiplier": 0.80,
            },
        ],
    )

    return {
        "analysis_id": "monogenic_diabetes_economic_reference",
        "intended_use": "synthetic_demonstrator_reference",
        "synthetic_case_count": synthetic_case_count,
        "currency": currency,
        "price_year": price_year,
        "health_system_burden": hs_burden,
        "household_burden": hh_burden,
        "societal_burden": soc_burden,
        "scenario_sensitivity": scenarios,
    }
