from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from rareburden.ledger import load_ledger
from scripts.check_track003_synthetic_denominator_candidate import (
    FALSE_CLAIMS,
    Track003SyntheticCandidateError,
    validate,
    validate_required_alignment,
)

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "docs/track-003-rbc-p002-synthetic-denominator-candidate-2026-08-29.yml"


def _document() -> dict[str, object]:
    value = yaml.safe_load(CANDIDATE.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _candidate(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "candidate.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_current_synthetic_denominator_candidate_is_valid_without_execution() -> None:
    validate(CANDIDATE, ROOT)


def test_candidate_binds_the_primary_diabetes_denominator_and_expected_cases() -> None:
    scope = _document()["registered_scope"]
    assert scope == {
        "estimand_id": "E-RBC-P002-EXPECTED-CASES",
        "denominator_id": "D-RBC-P002-PRIMARY-DIABETES",
        "denominator_parameter_id": "rbc-p002-diabetes-denominator-synthetic",
        "aetiologic_fraction_parameter_id": "rbc-p002-aetiologic-fraction-synthetic",
        "output_unit": "people",
    }


def test_candidate_rejects_binding_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(_document())
    document["bindings"]["ledger"]["sha256"] = "0" * 64
    with pytest.raises(Track003SyntheticCandidateError, match="binding drift"):
        validate(_candidate(tmp_path, document), ROOT)


@pytest.mark.parametrize("claim", sorted(FALSE_CLAIMS))
def test_candidate_rejects_every_activation_or_authority_claim(tmp_path: Path, claim: str) -> None:
    document = copy.deepcopy(_document())
    document["claims"][claim] = True
    with pytest.raises(Track003SyntheticCandidateError, match="activation or authority"):
        validate(_candidate(tmp_path, document), ROOT)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("exact_candidate_review_complete", True),
        ("owner_disposition_complete", True),
        ("executable", True),
    ],
)
def test_candidate_rejects_premature_qualification(tmp_path: Path, field: str, value: bool) -> None:
    document = copy.deepcopy(_document())
    document["qualification"][field] = value
    with pytest.raises(Track003SyntheticCandidateError, match="qualification state drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_candidate_rejects_scope_relabelling(tmp_path: Path) -> None:
    document = copy.deepcopy(_document())
    document["registered_scope"]["denominator_id"] = "D-RBC-P002-TOTAL-POPULATION"
    with pytest.raises(Track003SyntheticCandidateError, match="registered scope drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_candidate_rejects_next_gate_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(_document())
    document["next_gate"] = "execute now"
    with pytest.raises(Track003SyntheticCandidateError, match="next gate drift"):
        validate(_candidate(tmp_path, document), ROOT)


@pytest.mark.parametrize(
    ("location", "field", "value", "message"),
    [
        ("population", "geography_id", "other", "population alignment"),
        ("population", "age_max", 99, "population alignment"),
        ("period", "end", "2024-12-31", "period alignment"),
        ("disease_definition", "diabetes_case_definition", "other", "required alignment"),
        ("disease_definition", "ascertainment_target", "other", "required alignment"),
    ],
)
def test_every_required_alignment_dimension_fails_closed(
    location: str, field: str, value: object, message: str
) -> None:
    ledger = load_ledger(
        ROOT / "examples/ledger/track-003-rbc-p002-synthetic.yml",
        ROOT / "schemas/parameter-ledger.schema.json",
    )
    denominator = copy.deepcopy(ledger.get("rbc-p002-diabetes-denominator-synthetic"))
    fraction = copy.deepcopy(ledger.get("rbc-p002-aetiologic-fraction-synthetic"))
    fraction[location][field] = value
    with pytest.raises(Track003SyntheticCandidateError, match=message):
        validate_required_alignment(denominator, fraction)
