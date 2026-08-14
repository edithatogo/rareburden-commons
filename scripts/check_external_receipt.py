#!/usr/bin/env python3
"""Validate an external gate receipt without accepting or registering it."""

from __future__ import annotations

import argparse
from pathlib import Path

from rareburden.schema import SchemaValidationError, load_document, load_mapping, validate_instance

ALLOWED_GATES = {
    "scientific",
    "patient_community",
    "custodian_data_governance",
    "independent_operator",
    "operational_owners",
    "release",
}
ALLOWED_DECISIONS = {
    "approve",
    "pass",
    "accept",
    "bounded",
    "revise",
    "reject",
    "fail",
    "stop",
    "defer",
}


def validate_receipt(path: Path, *, require_attributable: bool = False) -> None:
    """Validate receipt shape; optionally require accountable attribution fields."""
    root = Path(__file__).parents[1]
    document = load_document(path)
    validate_instance(
        document,
        load_mapping(root / "schemas/external-gate-receipt.schema.json"),
        label="receipt",
    )
    if require_attributable:
        accountable = document["accountable"]
        attestation = document["attestation"]
        subject = document["subject"]
        required = {
            "receipt_id": document["receipt_id"],
            "gate": document["gate"],
            "decision": document["decision"],
            "decision_date_utc": document["decision_date_utc"],
            "accountable.person_or_body": accountable["person_or_body"],
            "accountable.role": accountable["role"],
            "accountable.independence_or_authority_basis": accountable[
                "independence_or_authority_basis"
            ],
            "subject.repository": subject["repository"],
            "subject.commit_or_tag": subject["commit_or_tag"],
            "subject.manifest_id": subject["manifest_id"],
            "subject.input_manifest_sha256": subject["input_manifest_sha256"],
            "attestation.submitted_by": attestation["submitted_by"],
            "attestation.submitted_at_utc": attestation["submitted_at_utc"],
            "attestation.signature_or_approval_record": attestation["signature_or_approval_record"],
        }
        missing = [
            name
            for name, value in required.items()
            if not isinstance(value, str) or not value.strip()
        ]
        if missing:
            raise SchemaValidationError(
                "receipt is not attributable; missing: " + ", ".join(missing)
            )
        if document["gate"] not in ALLOWED_GATES:
            raise SchemaValidationError(f"receipt has unsupported gate: {document['gate']}")
        if document["decision"] not in ALLOWED_DECISIONS:
            raise SchemaValidationError(f"receipt has unsupported decision: {document['decision']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--require-attributable", action="store_true")
    args = parser.parse_args()
    try:
        validate_receipt(args.receipt, require_attributable=args.require_attributable)
    except (OSError, KeyError, SchemaValidationError) as exc:
        print(f"Receipt validation failed: {exc}")
        return 1
    print("Receipt shape passed; gate registration remains a separate action.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
