#!/usr/bin/env python3
"""Validate the qualifying-receipts register without approving any gate."""

from __future__ import annotations

import argparse
from pathlib import Path

from rareburden.schema import SchemaValidationError, load_document, load_mapping, validate_instance

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
    for entry in gates:
        if entry["status"] == "verified":
            required = (entry["receipt_id"], entry["locator"], entry["verified_at_utc"])
            if not all(isinstance(value, str) and value.strip() for value in required):
                raise SchemaValidationError(
                    f"verified gate {entry['gate']} lacks receipt identity, "
                    "locator or verification time"
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("register", type=Path)
    args = parser.parse_args()
    try:
        validate_register(args.register)
    except (OSError, KeyError, SchemaValidationError) as exc:
        print(f"Qualifying receipts register failed: {exc}")
        return 1
    print("Qualifying receipts register passed; pending gates remain pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
