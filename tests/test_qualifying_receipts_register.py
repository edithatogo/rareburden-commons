from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from rareburden.schema import SchemaValidationError, load_document
from scripts.check_qualifying_receipts_register import validate_register

ROOT = Path(__file__).parents[1]
REGISTER = ROOT / "docs/qualifying-receipts-register.yml"


def test_qualifying_receipts_register_is_complete_and_pending() -> None:
    document = load_document(REGISTER)
    validate_register(REGISTER)
    assert {entry["status"] for entry in document["gates"]} == {"pending"}


def test_verified_gate_requires_receipt_metadata(tmp_path: Path) -> None:
    document = load_document(REGISTER)
    document = copy.deepcopy(document)
    document["gates"][0]["status"] = "verified"
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
