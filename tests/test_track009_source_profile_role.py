from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any

import pytest
import yaml

from scripts.check_track009_candidate_containment import MANIFEST, MANIFEST_SHA256
from scripts.check_track009_source_profile_role import (
    LEDGER_SCHEMA,
    PROFILE_SCHEMA,
    SourceProfileRoleError,
    validate,
)

ROOT = Path(__file__).parents[1]
MATRIX = Path("examples/ledger/source-profile-role-structural-synthetic.yml")
SCHEMA = Path("schemas/source-profile-role-structural-assessment.schema.json")


def _document() -> dict[str, Any]:
    return yaml.safe_load((ROOT / MATRIX).read_text(encoding="utf-8"))


def _case_root(tmp_path: Path, document: dict[str, Any]) -> Path:
    paths = [
        SCHEMA,
        LEDGER_SCHEMA,
        PROFILE_SCHEMA,
        Path(document["ledger"]),
        *(Path(value) for value in document["profiles"]),
    ]
    for relative in paths:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        source = ROOT / relative
        if source.exists():
            target.write_bytes(source.read_bytes())
    target = tmp_path / MATRIX
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return tmp_path


def test_reference_matrix_covers_every_bound_profile_role_fail_closed() -> None:
    validate(ROOT, MATRIX, SCHEMA)
    document = _document()
    bindings = {
        (
            row["demonstrator_id"],
            row["protocol_id"],
            row["role"],
            row["parameter_id"],
        )
        for row in document["assessments"]
    }
    assert len(bindings) == len(document["assessments"]) == 4
    dispositions = {
        row["assessment_id"]: row["overall_disposition"] for row in document["assessments"]
    }
    assert dispositions == {
        "spr-003-denominator": "incompatible",
        "spr-003-aetiologic-fraction": "unassessed",
        "spr-011-denominator": "incompatible",
        "spr-012-population-context": "unassessed",
    }
    assert set(document["claims"].values()) == {False}
    assert hashlib.sha256((ROOT / MANIFEST).read_bytes()).hexdigest() == MANIFEST_SHA256


def test_missing_bound_role_is_rejected(tmp_path: Path) -> None:
    document = _document()
    document["assessments"].pop()
    with pytest.raises(SourceProfileRoleError, match="missing assessment bindings"):
        validate(_case_root(tmp_path, document), MATRIX, SCHEMA)


@pytest.mark.parametrize("field", ["measure", "metric", "unit", "population", "geography"])
def test_parameter_dimension_drift_is_rejected(tmp_path: Path, field: str) -> None:
    document = _document()
    document["assessments"][0][field] = "drifted"
    with pytest.raises(SourceProfileRoleError, match=f"{field} drift"):
        validate(_case_root(tmp_path, document), MATRIX, SCHEMA)


def test_retained_incomplete_alternative_group_is_rejected(tmp_path: Path) -> None:
    document = _document()
    retained = document["assessments"][-1]
    retained["alternative_group"]["selection_state"] = "retained_for_contract_test"
    retained["alternative_group"]["completeness"] = "incomplete"
    retained["overall_disposition"] = "synthetic_structural_compatibility"
    for value in retained["dimension_dispositions"].values():
        value["disposition"] = "compatible"
    with pytest.raises(SourceProfileRoleError, match="retained incomplete group"):
        validate(_case_root(tmp_path, document), MATRIX, SCHEMA)


def test_empirical_or_restricted_source_cannot_enter_matrix(tmp_path: Path) -> None:
    document = _document()
    document["assessments"][0]["source_release_id"] = "snomed-ct-uts-current"
    with pytest.raises(ValueError, match="Schema validation failed"):
        validate(_case_root(tmp_path, document), MATRIX, SCHEMA)


def test_profile_removal_cannot_shrink_required_coverage(tmp_path: Path) -> None:
    document = _document()
    document["profiles"].pop()
    with pytest.raises(SourceProfileRoleError, match="canonical demonstrator profile set drift"):
        validate(_case_root(tmp_path, document), MATRIX, SCHEMA)


def test_profile_substitution_cannot_change_required_coverage(tmp_path: Path) -> None:
    document = _document()
    document["profiles"][0] = "examples/demonstrators/999-ledger-profile.yml"
    with pytest.raises(SourceProfileRoleError, match="canonical demonstrator profile set drift"):
        validate(_case_root(tmp_path, document), MATRIX, SCHEMA)


def test_required_scientific_dimension_cannot_be_renamed(tmp_path: Path) -> None:
    document = _document()
    dimensions = document["assessments"][0]["dimension_dispositions"]
    dimensions["renamed_population"] = dimensions.pop("population")
    with pytest.raises(ValueError, match="Schema validation failed"):
        validate(_case_root(tmp_path, document), MATRIX, SCHEMA)


def test_proposed_role_must_match_bound_profile_role(tmp_path: Path) -> None:
    document = _document()
    document["assessments"][0]["proposed_role"] = "context_only"
    with pytest.raises(SourceProfileRoleError, match="proposed-role drift"):
        validate(_case_root(tmp_path, document), MATRIX, SCHEMA)


def test_synthetic_prefix_cannot_launder_private_source(tmp_path: Path) -> None:
    document = _document()
    document["assessments"][0]["source_release_id"] = "synthetic-hpo-private"
    with pytest.raises(ValueError, match="Schema validation failed"):
        validate(_case_root(tmp_path, document), MATRIX, SCHEMA)


def test_restricted_licence_state_cannot_receive_synthetic_rights(tmp_path: Path) -> None:
    document = _document()
    root = _case_root(tmp_path, document)
    ledger_path = root / document["ledger"]
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    ledger["parameters"][0]["licence_state"] = "restricted"
    ledger_path.write_text(yaml.safe_dump(ledger, sort_keys=False), encoding="utf-8")
    with pytest.raises(SourceProfileRoleError, match="non-synthetic licence state"):
        validate(root, MATRIX, SCHEMA)


def test_authority_or_resolution_claim_cannot_escape(tmp_path: Path) -> None:
    document = copy.deepcopy(_document())
    document["claims"]["epi_med_01_resolved"] = True
    with pytest.raises(ValueError, match="Schema validation failed"):
        validate(_case_root(tmp_path, document), MATRIX, SCHEMA)
