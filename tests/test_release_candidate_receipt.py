from __future__ import annotations

from pathlib import Path

from rareburden.schema import validate_document_files

ROOT = Path(__file__).parents[1]


def test_synthetic_release_candidate_receipt_is_schema_valid_and_non_authorizing() -> None:
    receipt = validate_document_files(
        ROOT / "examples/fixtures/release-candidate-receipt-synthetic.json",
        ROOT / "schemas/release-candidate-receipt.schema.json",
    )
    assert receipt["run"]["outcome"] == "qualified"
    assert "not an independent reproduction" in receipt["run"]["discrepancies"][0]
    assert "stable-release authority remains pending" in receipt["review"]["notes"]
