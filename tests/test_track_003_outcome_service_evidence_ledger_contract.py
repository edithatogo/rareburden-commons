from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "track-003-outcome-service-evidence-ledger-contract-v0.1.0.yml"


def _contract() -> dict[str, object]:
    document = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def test_ledger_contract_is_empty_non_binding_preparation() -> None:
    document = _contract()
    assert document["status"] == "non_binding_synthetic_preparation"
    assert document["track_status"] == "blocked"
    assert document["empirical_activation"] == "disabled"
    assert document["registered_source_releases"] == []
    assert document["extracted_empirical_records"] == []
    assert document["ledger_parameters"] == []


def test_record_unit_separates_evidence_transformations_models_and_assumptions() -> None:
    document = _contract()
    required = set(document["record_unit"]["required_separation"])
    assert {
        "reported_result",
        "repository_transformation",
        "modelled_scenario",
        "assumption",
    } <= required
    prohibited = " ".join(document["record_unit"]["prohibited_units"])
    assert "participant-level" in prohibited
    assert "small-cell" in prohibited


def test_all_required_evidence_families_have_measure_specific_guards() -> None:
    families = _contract()["evidence_families"]
    assert set(families) == {"diagnosis_delay", "treatment_change", "complications", "service_use"}
    delay = " ".join(families["diagnosis_delay"]["fail_closed_rules"])
    treatment = " ".join(families["treatment_change"]["fail_closed_rules"])
    complications = " ".join(families["complications"]["fail_closed_rules"])
    service = " ".join(families["service_use"]["fail_closed_rules"])
    assert "time origins" in delay
    assert "treatment benefit" in treatment
    assert "case fraction alone" in complications
    assert "encounters as unique people" in service


def test_comparisons_default_to_descriptive_and_causal_shortcuts_fail_closed() -> None:
    rules = _contract()["comparison_and_causal_rules"]
    assert rules["descriptive_default"] is True
    assert rules["causal_claim_status"].startswith("blocked")
    shortcuts = " ".join(rules["prohibited_shortcuts"])
    assert "counterfactual" in shortcuts
    assert "confounding control" in shortcuts
    assert "case fraction applied" in shortcuts


def test_alignment_fields_preserve_population_setting_and_missingness() -> None:
    fields = set(_contract()["common_alignment_fields"])
    assert {
        "comparison_group_definition",
        "diagnosis_and_aetiology_ascertainment",
        "clinical_setting_and_referral_pathway",
        "follow_up_or_observation_window",
        "missing_unclassified_and_lost_to_follow_up_counts",
    } <= fields


def test_quality_domains_remain_separate_and_direct_use_is_blocked() -> None:
    quality = _contract()["quality_assessment_mapping"]
    assert {
        "construct_validity",
        "selection_bias",
        "ascertainment",
        "measurement_error",
        "missingness",
        "precision",
        "representativeness",
        "diagnostic_validity",
        "conflict_of_interest",
        "computational_reproducibility",
    } <= set(quality["mandatory_domains"])
    assert "do not calculate a composite quality score" in quality["rule"]
    assert quality["direct_use_status"].startswith("blocked")


def test_overlap_missingness_and_uncertainty_cannot_silently_disappear() -> None:
    document = _contract()
    overlap = " ".join(document["overlap_and_missingness_rules"])
    uncertainty = " ".join(document["uncertainty_requirements"])
    assert "publication-overlap" in overlap
    assert "structural zero, observed zero" in overlap
    assert "loss to follow-up" in overlap
    assert "zero-width interval" in uncertainty
    assert "structural uncertainty separately" in uncertainty


def test_unverified_records_cannot_create_parameters_or_empirical_claims() -> None:
    document = _contract()
    release = document["verification_and_release"]
    assert release["automated_extraction_status"] == "unverified_candidate"
    assert release["automated_candidate_eligible_for_parameter_synthesis"] is False
    assert release["ledger_parameter_creation"] == "blocked"
    assert document["current_disposition"]["parameter_created"] is False
    assert {
        "empirical_diagnosis_delay",
        "causal_treatment_effect",
        "empirical_complication_difference",
        "empirical_service_use_difference",
        "independent_or_external_review",
        "empirical_activation",
    } <= set(document["prohibited_claims"])
