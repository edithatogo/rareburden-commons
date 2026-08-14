from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from rareburden.schema import SchemaValidationError, load_document
from scripts.check_qualifying_receipts_register import validate_receipt_binding, validate_register

ROOT = Path(__file__).parents[1]
REGISTER = ROOT / "docs/qualifying-receipts-register.yml"


def test_qualifying_receipts_register_is_complete_and_pending() -> None:
    document = load_document(REGISTER)
    validate_register(REGISTER)
    assert document["gates"][0]["status"] == "verified"
    assert {entry["status"] for entry in document["gates"][1:]} == {"pending"}


def test_verified_gate_requires_receipt_metadata(tmp_path: Path) -> None:
    document = load_document(REGISTER)
    document = copy.deepcopy(document)
    document["gates"][1]["status"] = "verified"
    path = tmp_path / "register.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    with pytest.raises(SchemaValidationError, match="lacks receipt identity"):
        validate_register(path)


def test_verified_gate_rejects_placeholder_candidate(tmp_path: Path) -> None:
    document = load_document(REGISTER)
    document["candidate"]["manifest_id"] = "pending-candidate-manifest"
    document["gates"][0].update(
        {
            "status": "verified",
            "receipt_id": "receipt-1",
            "locator": "secure://receipt-1",
            "verified_at_utc": "2026-08-03T00:00:00Z",
        }
    )
    path = tmp_path / "register.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    with pytest.raises(SchemaValidationError, match="placeholder candidate"):
        validate_register(path)


def test_receipt_binding_rejects_digest_mismatch(tmp_path: Path) -> None:
    receipt = {
        "receipt_schema_version": "0.1.0",
        "receipt_id": "receipt-1",
        "gate": "scientific",
        "decision": "bounded",
        "accountable": {
            "person_or_body": "Authority",
            "role": "Methods authority",
            "organisation_or_constituency": "Organisation",
            "independence_or_authority_basis": "Mandate",
        },
        "decision_date_utc": "2026-08-03T00:00:00Z",
        "subject": {
            "repository": "edithatogo/rareburden-commons",
            "commit_or_tag": "candidate-2026-08-03",
            "manifest_id": "rel-b213c531a6b754940f80ab70",
            "input_manifest_sha256": "wrong",
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
            "submitted_by": "Authority",
            "submitted_at_utc": "2026-08-03T00:00:00Z",
            "signature_or_approval_record": "record-1",
            "supersedes_receipt_id": "",
        },
    }
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(SchemaValidationError, match="input_manifest_sha256"):
        validate_receipt_binding(REGISTER, path)
