from __future__ import annotations

from pathlib import Path

from rareburden.schema import validate_document_files

ROOT = Path(__file__).parents[1]


def test_synthetic_operations_receipt_is_schema_valid_and_non_authorizing() -> None:
    receipt = validate_document_files(
        ROOT / "examples/fixtures/synthetic-operations-receipt.json",
        ROOT / "schemas/synthetic-operations-receipt.schema.json",
    )
    assert receipt["outcome"] == "qualified"
    assert receipt["production_authorized"] is False
