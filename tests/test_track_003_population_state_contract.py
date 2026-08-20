from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "track-003-population-state-contract-v0.1.0.yml"


def _contract() -> dict[str, object]:
    document = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def test_population_state_contract_is_non_binding_and_disabled() -> None:
    document = _contract()
    assert document["status"] == "non_binding_synthetic_preparation"
    assert document["track_status"] == "blocked"
    assert document["empirical_activation"] == "disabled"
    assert "approved_or_frozen_protocol" in document["prohibited_claims"]


def test_observed_latent_and_selection_dimensions_are_distinct() -> None:
    document = _contract()
    dimensions = {item["dimension_id"]: item for item in document["state_dimensions"]}
    assert dimensions["monogenic_aetiology_observation"]["type"] == "observable_classification"
    assert dimensions["monogenic_aetiology_latent"]["type"] == "model_latent_state"
    assert dimensions["referral_and_testing_selection"]["type"] == "orthogonal_selection_indicator"


def test_undiagnosed_quantity_is_modelled_not_observed() -> None:
    document = _contract()
    quantities = {item["quantity_id"]: item for item in document["derived_quantities"]}
    undiagnosed = quantities["Q-RBC-P002-MODELLED-UNDIAGNOSED"]
    assert undiagnosed["evidence_status"] == "modelled_difference"
    assert undiagnosed["interpretation"] == "scenario_estimate_not_directly_observed_population"
    assert "observed_undiagnosed_case_count" in document["prohibited_claims"]


def test_partition_rules_prevent_double_counting_and_forced_classification() -> None:
    document = _contract()
    rules = {item["condition"]: item["action"] for item in document["partition_rules"]}
    assert rules["diagnosed_plus_modelled_total_requested"] == "reject_overlapping_quantities"
    assert (
        rules["diagnosed_plus_modelled_undiagnosed_requested"]
        == "allow_only_with_aligned_partition_contract"
    )
    assert rules["unknown_or_unclassified_assigned_to_non_monogenic"] == "reject"
    assert rules["latent_state_reported_as_observed_diagnosis"] == "reject"


def test_modelled_undiagnosed_uncertainty_extends_total_uncertainty() -> None:
    document = _contract()
    requirements = document["uncertainty_requirements"]
    assert "structural_model" in requirements["modelled_total"]
    assert "diagnosis_ascertainment" in requirements["modelled_undiagnosed"]
    assert (
        "dependence_between_total_and_diagnosed_components" in requirements["modelled_undiagnosed"]
    )
