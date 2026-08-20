from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "track-003-framing-interpretation-guard-v0.1.0.yml"


def _contract() -> dict[str, object]:
    document = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def test_framing_guard_is_non_binding_and_has_no_external_authority() -> None:
    document = _contract()
    assert document["status"] == "non_binding_synthetic_preparation"
    assert document["track_status"] == "blocked"
    assert document["empirical_activation"] == "disabled"
    gates = document["review_gates"]
    assert gates["clinical_methods"]["status"] == "pending"
    assert gates["community_harm"]["status"] == "pending"
    assert gates["repository_owner"]["status"] == "pending"
    assert "not independent" in gates["authority_statement"]


def test_quantitative_claims_require_scientific_context_and_uncertainty() -> None:
    document = _contract()
    qualifiers = set(document["required_quantitative_qualifiers"])
    assert {
        "population",
        "geography",
        "period",
        "case_definition_and_semantic_release",
        "denominator_definition",
        "evidence_status",
        "uncertainty",
        "ascertainment_and_referral_limitations",
        "overlap_and_double_counting_limitations",
    } <= qualifiers


def test_modelled_scenario_and_unknown_states_cannot_be_overstated() -> None:
    document = _contract()
    language = document["evidence_status_language"]
    assert language["modelled"]["required_label"] == "modelled_estimate"
    assert language["scenario"]["required_label"] == "scenario_not_empirical_estimate"
    assert (
        language["unknown_or_unclassified"]["interpretation"]
        == "not_evidence_of_absence_or_non_monogenic_aetiology"
    )


def test_headline_failures_suppress_or_reject_unsafe_outputs() -> None:
    document = _contract()
    actions = {
        item["rule_id"]: item["failure_action"] for item in document["headline_output_rules"]
    }
    assert actions["H-001"] == "suppress_output"
    assert actions["H-002"] == "suppress_output"
    assert actions["H-003"] == "suppress_output"
    assert actions["H-006"] == "reject_combined_claim"


def test_interpretation_boundaries_block_clinical_and_shortcut_claims() -> None:
    document = _contract()
    boundaries = document["interpretation_boundaries"]
    assert "individual diagnosis" in boundaries["diagnosis"]["prohibited"]
    assert "case composition" in boundaries["treatment"]["prohibited"]
    assert "case fraction alone" in boundaries["outcomes"]["prohibited"]
    assert "realised savings" in boundaries["economics"]["prohibited"]
    assert "rationing" in boundaries["policy"]["prohibited"]


def test_harm_challenges_and_stop_triggers_cover_equity_and_authority() -> None:
    document = _contract()
    risks = " ".join(item["risk"] for item in document["harm_and_equity_challenges"])
    triggers = " ".join(document["stop_triggers"])
    assert "biological prevalence differences" in risks
    assert "worth of people" in risks
    assert "community consent or endorsement" in risks
    assert "stigmatizing" in triggers
    assert "patient/community endorsement" in triggers


def test_prohibited_uses_and_claims_keep_empirical_release_blocked() -> None:
    document = _contract()
    assert "clinical decision support" in document["prohibited_uses"]
    assert "public empirical burden reporting" in document["prohibited_uses"]
    assert "patient_or_community_endorsement" in document["prohibited_claims"]
    assert "approved_or_frozen_protocol" in document["prohibited_claims"]
    assert "empirical_activation" in document["prohibited_claims"]
