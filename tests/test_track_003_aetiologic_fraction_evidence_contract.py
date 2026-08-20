from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "track-003-aetiologic-fraction-evidence-contract-v0.1.0.yml"


def _contract() -> dict[str, object]:
    document = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def test_evidence_contract_is_empty_non_binding_preparation() -> None:
    document = _contract()
    assert document["status"] == "non_binding_synthetic_preparation"
    assert document["track_status"] == "blocked"
    assert document["empirical_activation"] == "disabled"
    assert document["registered_source_releases"] == []
    assert document["extracted_empirical_records"] == []


def test_source_registration_preserves_provenance_rights_and_version_state() -> None:
    document = _contract()
    requirements = set(document["source_registration_requirements"])
    assert {
        "source_release_or_version",
        "retrieval_event_and_retrieved_at",
        "access_class",
        "licence_and_redistribution_state",
        "correction_retraction_and_version_status",
        "source_checksum_where_lawful",
    } <= requirements


def test_extraction_requires_aligned_population_and_ascertainment_fields() -> None:
    document = _contract()
    fields = document["eligibility_fields"]
    assert "compatible_diabetes_denominator" in fields["question_alignment"]
    assert "sampling_frame" in fields["design"]
    assert "ancestry_ethnicity_or_population_variable_as_reported" in fields["population"]
    assert "referral_pathway" in fields["ascertainment"]
    assert "variant_classification_standard_and_version" in fields["ascertainment"]


def test_incompatible_or_selection_conditioned_denominators_fail_closed() -> None:
    document = _contract()
    rules = {item["condition"]: item["action"] for item in document["denominator_alignment_rules"]}
    assert rules["denominator_is_total_population_for_within_diabetes_fraction"] == "reject"
    assert rules["referral_cohort_is_interpreted_as_population_representative"] == "reject"
    assert rules["numerator_and_denominator_are_not_from_the_same_aligned_population"] == "reject"
    assert rules["diagnosed_prevalence_is_substituted_for_total_aetiologic_fraction"] == "reject"


def test_quality_domains_remain_separate_without_composite_score() -> None:
    document = _contract()
    quality = document["quality_assessment_mapping"]
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
    assert "Do not calculate a composite quality score" in quality["rule"]
    assert quality["direct_use_status"].startswith("blocked")


def test_ancestry_and_sparse_subgroup_rules_block_essentialism_and_ranking() -> None:
    document = _contract()
    rules = document["stratification_rules"]
    assert "fixed biological categories" in rules["ancestry_ethnicity_population"]["rule"]
    assert "infer unreported identity" in rules["ancestry_ethnicity_population"]["rule"]
    assert "non-estimability" in rules["sparse_subgroups"]["rule"]
    assert "ranking" in rules["sparse_subgroups"]["rule"]


def test_unverified_extraction_cannot_create_a_parameter() -> None:
    document = _contract()
    workflow = document["verification_workflow"]
    assert workflow["automated_extraction"]["default_status"] == "unverified_candidate"
    assert workflow["automated_extraction"]["eligible_for_parameter_synthesis"] is False
    assert workflow["accountable_verification"]["status"] == "pending"
    disposition = document["current_disposition"]
    assert disposition["extraction_executed"] is False
    assert disposition["parameter_created"] is False


def test_conflicts_overlap_and_missingness_do_not_silently_disappear() -> None:
    document = _contract()
    conflicts = " ".join(document["conflict_and_overlap_rules"])
    missingness = " ".join(document["missingness_rules"])
    assert "retain all eligible conflicting estimates" in conflicts
    assert "duplicate participants" in conflicts
    assert "not reported, not collected" in missingness
    assert "absence of difference" in missingness
    assert "unclassified participants" in missingness


def test_contract_prohibits_empirical_and_review_claims() -> None:
    document = _contract()
    claims = set(document["prohibited_claims"])
    assert {
        "systematic_or_complete_evidence_search",
        "empirical_aetiologic_fraction",
        "verified_or_quality_assessed_evidence",
        "directly_transportable_parameter",
        "independent_or_external_review",
        "empirical_activation",
    } <= claims
