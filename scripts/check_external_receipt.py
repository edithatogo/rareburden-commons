#!/usr/bin/env python3
"""Validate an external gate receipt without accepting or registering it."""

from __future__ import annotations

import argparse
from pathlib import Path

from rareburden.schema import SchemaValidationError, load_document, load_mapping, validate_instance


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
            "accountable.person_or_body": accountable["person_or_body"],
            "accountable.role": accountable["role"],
            "accountable.independence_or_authority_basis": accountable[
                "independence_or_authority_basis"
            ],
            "subject.commit_or_tag": subject["commit_or_tag"],
            "subject.manifest_id": subject["manifest_id"],
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
