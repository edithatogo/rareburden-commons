#!/usr/bin/env python3
"""Validate the qualifying-receipts register without approving any gate."""

from __future__ import annotations

import argparse
from pathlib import Path

from rareburden.schema import SchemaValidationError, load_document, load_mapping, validate_instance
from scripts.check_external_receipt import validate_receipt

REQUIRED_GATES = {
    "scientific",
    "patient_community",
    "custodian_data_governance",
    "independent_operator",
    "operational_owners",
    "release",
}


def validate_register(path: Path) -> None:
    root = Path(__file__).parents[1]
    document = load_document(path)
    validate_instance(
        document,
        load_mapping(root / "schemas/qualifying-receipts-register.schema.json"),
        label="qualifying receipts register",
    )
    gates = document["gates"]
    names = {entry["gate"] for entry in gates}
    if names != REQUIRED_GATES:
        raise SchemaValidationError("register must contain each required gate exactly once")
    if len(gates) != len(names):
        raise SchemaValidationError("register contains duplicate gate entries")
    candidate = document["candidate"]
    for entry in gates:
        if entry["status"] == "verified":
            required = (entry["receipt_id"], entry["locator"], entry["verified_at_utc"])
            if not all(isinstance(value, str) and value.strip() for value in required):
                raise SchemaValidationError(
                    f"verified gate {entry['gate']} lacks receipt identity, "
                    "locator or verification time"
                )
            if any(
                not isinstance(value, str)
                or not value.strip()
                or value.strip().lower() in {"pending", "pending-candidate-manifest"}
                for value in candidate.values()
            ):
                raise SchemaValidationError(
                    f"verified gate {entry['gate']} is bound to a placeholder candidate"
                )


def validate_receipt_binding(register_path: Path, receipt_path: Path) -> None:
    """Validate an attributable receipt against the register's frozen candidate."""
    validate_register(register_path)
    validate_receipt(receipt_path, require_attributable=True)
    register = load_document(register_path)
    receipt = load_document(receipt_path)
    candidate = register["candidate"]
    subject = receipt["subject"]
    expected = {
        "commit_or_tag": candidate["commit_or_tag"],
        "manifest_id": candidate["manifest_id"],
        "input_manifest_sha256": candidate["input_manifest_sha256"],
    }
    actual = {
        "commit_or_tag": subject["commit_or_tag"],
        "manifest_id": subject["manifest_id"],
        "input_manifest_sha256": subject["input_manifest_sha256"],
    }
    mismatches = [key for key in expected if actual[key] != expected[key]]
    if mismatches:
        raise SchemaValidationError(
            "receipt is not bound to the frozen candidate: " + ", ".join(mismatches)
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("register", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    try:
        if args.receipt is None:
            validate_register(args.register)
        else:
            validate_receipt_binding(args.register, args.receipt)
    except (OSError, KeyError, SchemaValidationError) as exc:
        print(f"Qualifying receipts register failed: {exc}")
        return 1
    print("Qualifying receipts register passed; pending gates remain pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
