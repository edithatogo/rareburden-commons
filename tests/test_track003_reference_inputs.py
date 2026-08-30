"""Contract tests for the full-scope synthetic reference input candidate."""

import json
from pathlib import Path

import pytest

from rareburden.ledger import validate_ledger
from rareburden.quality import (
    build_quality_disposition,
    validate_evidence_assessment,
    validate_transportability_assessment,
    verify_parameter_assessment_closure,
)
from scripts.track003_reference_inputs import (
    ASSUMPTIONS,
    build_reference_inputs,
    validate_reference_inputs,
)

ROOT = Path(__file__).resolve().parents[1]


def schema(name):
    return json.loads((ROOT / "schemas" / f"{name}.schema.json").read_text())


def test_existing_contracts_and_complete_parameter_metadata():
    candidate = build_reference_inputs(ROOT)
    ledger = validate_ledger(candidate["ledger"], schema("parameter-ledger"))
    assert len(ledger.records) == len(ASSUMPTIONS) == 18
    evidence = {
        record["assessment_id"]: validate_evidence_assessment(record, schema("evidence-assessment"))
        for record in candidate["evidence_assessments"]
    }
    transport = {
        record["assessment_id"]: validate_transportability_assessment(
            record, schema("transportability-assessment")
        )
        for record in candidate["transportability_assessments"]
    }
    for identifier, record in ledger.records.items():
        assert record["evidence_status"] == "assumed"
        assert record["source_release_ids"] == []
        assert record["transformation_ids"] == []
        assert evidence[record["evidence_assessment_ids"][0]]["subject"]["subject_id"] == identifier
        assert transport[record["transportability_assessment_ids"][0]]["parameter_id"] == identifier
        assert record["assumption_rationale"] and record["limitations"]
    disposition = build_quality_disposition(
        analysis_id="reference-input-assurance",
        created_at=candidate["ledger"]["created_at"],
        intended_use="synthetic_assurance",
        evidence_assessments=list(evidence.values()),
        transportability_assessments=list(transport.values()),
    )
    assert disposition["eligible_for_synthetic_assurance"]
    assert not disposition["eligible_for_primary_analysis"]
    assert (
        verify_parameter_assessment_closure(
            parameters=list(ledger.records.values()),
            parameter_ids=list(ledger.records),
            evidence_assessments=list(evidence.values()),
            transportability_assessments=list(transport.values()),
            disposition=disposition,
        )
        == []
    )


def test_no_execution_or_external_claim_and_required_breadth():
    candidate = build_reference_inputs(ROOT)
    assert all(value is False for value in candidate["claims"].values())
    assert candidate["status"] == "inputs_only_execution_not_authorized"
    assert len(candidate["required_scenarios"]) == 12
    assert len(set(candidate["required_scenarios"])) == 12
    assert {
        "diagnosis-delay",
        "treatment-change",
        "annual-complication",
        "annual-person-cost",
    } <= set(ASSUMPTIONS)


def test_deterministic_detached_generation():
    first = build_reference_inputs(ROOT)
    second = build_reference_inputs(ROOT)
    assert first == second
    first["ledger"]["parameters"][0]["distribution"]["mean"] = 1
    assert second == build_reference_inputs(ROOT)


def test_delay_endpoints_and_annual_exposure_are_explicit():
    definition = build_reference_inputs(ROOT)["definition"]
    assert "first joint synthetic D=1/E=1 state" in definition["diagnosis_delay"]
    assert "first synthetic detection" in definition["diagnosis_delay"]
    assert "one full case-year" in definition["annual_exposure"]
    assert "no entry, exit, death" in definition["annual_exposure"]
    assert "free of the hypothetical composite" in definition["complication_eligibility"]


def test_committed_candidate_regenerates_exactly():
    candidate = json.loads(
        (ROOT / "examples/demonstrators/track-003-reference-inputs.json").read_text()
    )
    validate_reference_inputs(candidate, ROOT)


@pytest.mark.parametrize("name", ASSUMPTIONS)
def test_parameter_provenance_cannot_be_relabelled_empirical(name):
    candidate = build_reference_inputs(ROOT)
    record = next(
        item
        for item in candidate["ledger"]["parameters"]
        if item["parameter_id"] == f"rbc-p002-reference-{name}"
    )
    record["evidence_status"] = "observed"
    with pytest.raises(ValueError, match="drift"):
        validate_reference_inputs(candidate, ROOT)


@pytest.mark.parametrize("field", build_reference_inputs(ROOT)["claims"])
def test_candidate_cannot_grant_authority(field):
    candidate = build_reference_inputs(ROOT)
    candidate["claims"][field] = True
    with pytest.raises(ValueError, match="drift"):
        validate_reference_inputs(candidate, ROOT)
