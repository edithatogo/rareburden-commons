from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "track-003-estimand-denominator-contract-v0.1.0.yml"


def _contract() -> dict[str, object]:
    document = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def test_contract_is_non_binding_and_empirically_disabled() -> None:
    document = _contract()
    assert document["status"] == "non_binding_synthetic_preparation"
    assert document["track_status"] == "blocked"
    assert document["empirical_activation"] == "disabled"
    assert "approved_or_frozen_protocol" in document["prohibited_claims"]
    assert "independent_or_external_review" in document["prohibited_claims"]


def test_each_estimand_uses_a_declared_denominator_role() -> None:
    document = _contract()
    denominator_roles = {option["role"] for option in document["denominator_options"]}
    estimands = document["estimands"]
    assert len({estimand["estimand_id"] for estimand in estimands}) == len(estimands)
    assert all(estimand["denominator_role"] in denominator_roles for estimand in estimands)


def test_incompatible_and_selection_conditioned_denominators_fail_closed() -> None:
    document = _contract()
    rules = {rule["condition"]: rule["action"] for rule in document["compatibility_rules"]}
    assert rules["within_diabetes_fraction_with_total_population_denominator"] == "reject"
    assert rules["referral_cohort_fraction_interpreted_as_population_fraction"] == "reject"
    assert rules["geography_period_age_or_case_definition_mismatch"] == "reject"
    assert (
        rules["outcome_or_cost_envelope_allocated_by_case_fraction_alone"]
        == "reject_without_subgroup_specific_model"
    )


def test_existing_engine_fixture_is_not_promoted_to_protocol_evidence() -> None:
    document = _contract()
    disposition = document["current_fixture_disposition"]
    assert disposition["fixture"] == "examples/analyses/monogenic-diabetes-synthetic.yml"
    assert disposition["status"] == "engine_assurance_only"
    assert disposition["protocol_compatible"] is False


def test_uncertainty_covers_parameter_structural_and_transport_domains() -> None:
    document = _contract()
    domains = set(document["uncertainty_domains"])
    assert {
        "denominator_measurement",
        "aetiologic_fraction_parameter",
        "ascertainment_and_referral",
        "transportability",
        "dependence_between_model_components",
        "structural_model_choice",
    } <= domains
