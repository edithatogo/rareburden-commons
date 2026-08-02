from __future__ import annotations

import json
from pathlib import Path

import pytest

from rareburden.schema import SchemaValidationError
from scripts.check_external_receipt import validate_receipt

ROOT = Path(__file__).parents[1]
TEMPLATE = ROOT / "docs/external-gate-receipt-template.yml"


def test_receipt_validator_accepts_shape_but_rejects_blank_attribution() -> None:
    validate_receipt(TEMPLATE)
    with pytest.raises(SchemaValidationError, match="not attributable"):
        validate_receipt(TEMPLATE, require_attributable=True)


def test_receipt_validator_rejects_unknown_gate_after_attribution(tmp_path: Path) -> None:
    receipt = {
        "receipt_schema_version": "0.1.0",
        "receipt_id": "receipt-1",
        "gate": "unknown",
        "decision": "approve",
        "accountable": {
            "person_or_body": "Panel",
            "role": "Accountable authority",
            "organisation_or_constituency": "Organisation",
            "independence_or_authority_basis": "Mandate",
        },
        "decision_date_utc": "2026-08-03T00:00:00Z",
        "subject": {
            "repository": "edithatogo/rareburden-commons",
            "commit_or_tag": "v0.3.0-rc.2",
            "manifest_id": "manifest-1",
            "input_manifest_sha256": "sha256:abc",
        },
        "evidence": {
            "references": [],
            "protocol_versions": [],
            "commands": [],
            "environment": "clean",
            "retained_outputs": [],
            "discrepancy_log": "none",
        },
        "attestation": {
            "submitted_by": "Panel secretary",
            "submitted_at_utc": "2026-08-03T00:00:00Z",
            "signature_or_approval_record": "record-1",
            "supersedes_receipt_id": "",
        },
    }
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(SchemaValidationError, match="unsupported gate"):
        validate_receipt(path, require_attributable=True)
