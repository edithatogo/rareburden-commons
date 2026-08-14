from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_external_gate_receipt_template_is_blank_and_non_approving() -> None:
    receipt = yaml.safe_load(
        (ROOT / "docs/external-gate-receipt-template.yml").read_text(encoding="utf-8")
    )
    assert receipt["receipt_schema_version"] == "0.1.0"
    assert receipt["receipt_id"] == ""
    assert "|" in receipt["gate"]
    assert "|" in receipt["decision"]
    assert receipt["accountable"]["person_or_body"] == ""
    assert receipt["accountable"]["independence_or_authority_basis"] == ""
    assert receipt["subject"]["commit_or_tag"] == ""
    assert receipt["attestation"]["signature_or_approval_record"] == ""
