from pathlib import Path

import pytest

from rareburden.catalog import load_yaml
from rareburden.schema import SchemaValidationError, load_mapping, validate_instance

ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_equity_gap_review_is_schema_valid_and_fail_closed() -> None:
    schema = load_mapping(ROOT / "schemas/equity-gap-review.schema.json")
    review = load_yaml(ROOT / "examples/quality/equity-gap-review-synthetic.yml")
    validate_instance(review, schema, label="equity gap review")
    assert review["status"] == "draft"
    assert all(item["coverage_status"] in {"metadata_only", "not_assessed"} for item in review["populations"])
    invalid = {**review, "limitations": []}
    with pytest.raises(SchemaValidationError):
        validate_instance(invalid, schema, label="equity gap review")
