from __future__ import annotations

from pathlib import Path

from rareburden.schema import validate_document_files

ROOT = Path(__file__).parents[1]


def test_external_gate_receipt_template_matches_schema_and_remains_blank() -> None:
    receipt = validate_document_files(
        ROOT / "docs/external-gate-receipt-template.yml",
        ROOT / "schemas/external-gate-receipt.schema.json",
    )
    assert receipt["receipt_id"] == ""
    assert receipt["accountable"]["person_or_body"] == ""
    assert receipt["subject"]["commit_or_tag"] == ""
    assert receipt["attestation"]["signature_or_approval_record"] == ""
