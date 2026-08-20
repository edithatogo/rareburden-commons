from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.schema import SchemaValidationError, load_mapping, validate_instance

ROOT = Path(__file__).resolve().parents[1]
MATRIX = load_mapping(ROOT / "examples/node/wheelhouse-verification-matrix.yml")
SCHEMA = load_mapping(ROOT / "schemas/node-wheelhouse-matrix.schema.json")


def test_reference_matrix_records_only_current_platform_candidate() -> None:
    validate_instance(MATRIX, SCHEMA)
    passed = [row for row in MATRIX["rows"] if row["status"].endswith("_passed")]
    assert len(passed) == 1
    assert passed[0]["status"] == "candidate_passed"
    assert passed[0]["operator_independence"] == "same_operator"


def test_not_run_row_cannot_carry_evidence() -> None:
    invalid = deepcopy(MATRIX)
    invalid["rows"][1]["evidence"] = ["invented-receipt.json"]
    with pytest.raises(SchemaValidationError):
        validate_instance(invalid, SCHEMA)


def test_approved_pass_requires_independent_operator() -> None:
    invalid = deepcopy(MATRIX)
    invalid["rows"][0]["status"] = "approved_passed"
    with pytest.raises(SchemaValidationError):
        validate_instance(invalid, SCHEMA)


def test_python_311_is_outside_the_wheelhouse_contract() -> None:
    invalid = deepcopy(MATRIX)
    invalid["rows"][0]["python_version"] = "3.11"
    with pytest.raises(SchemaValidationError):
        validate_instance(invalid, SCHEMA)
