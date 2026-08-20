#!/usr/bin/env python3
"""Validate Track 007 community-authority receipt readiness without granting authority."""

from __future__ import annotations

import argparse
from pathlib import Path

from rareburden.schema import SchemaValidationError, load_document, load_mapping, validate_instance

PLACEHOLDERS = {"", "none", "n/a", "na", "pending", "placeholder", "tbd", "todo", "unknown"}
DISALLOWED_AUTHORITY_MARKERS = {"agent panel", "ai panel", "repository owner", "repo owner"}


def _strings(value: object) -> list[str]:
    if isinstance(value, dict):
        return [item for child in value.values() for item in _strings(child)]
    if isinstance(value, list):
        return [item for child in value for item in _strings(child)]
    return [value] if isinstance(value, str) else []


def validate_receipt(path: Path, *, require_qualifying: bool = False) -> None:
    """Validate the receipt profile; qualifying mode rejects preparation artifacts."""
    root = Path(__file__).parents[1]
    document = load_document(path)
    validate_instance(
        document,
        load_mapping(root / "schemas/track-007-community-authority-receipt.schema.json"),
        label="Track 007 community-authority receipt",
    )
    if not require_qualifying:
        return
    if document["synthetic"]:
        raise SchemaValidationError("synthetic receipt cannot qualify as community authority")
    required_text = [
        document["receipt_id"],
        *document["accountable"].values(),
        document["subject"]["manifest_id"],
        *document["review"].values(),
        document["correction_and_withdrawal"]["route"],
        document["correction_and_withdrawal"]["effect_of_correction_or_withdrawal"],
        document["attestation"]["submitted_by"],
        document["attestation"]["signature_or_approval_record"],
    ]
    flattened = _strings(required_text)
    placeholders = sorted({value for value in flattened if value.strip().lower() in PLACEHOLDERS})
    if placeholders:
        raise SchemaValidationError("qualifying receipt contains placeholder values")
    authority_text = " ".join(_strings(document["accountable"])).lower()
    marker = next((item for item in DISALLOWED_AUTHORITY_MARKERS if item in authority_text), None)
    if marker:
        raise SchemaValidationError(f"disallowed substitute for community authority: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--require-qualifying", action="store_true")
    args = parser.parse_args()
    try:
        validate_receipt(args.receipt, require_qualifying=args.require_qualifying)
    except (OSError, KeyError, SchemaValidationError) as exc:
        print(f"Receipt validation failed: {exc}")
        return 1
    print(
        "Receipt profile passed; attribution and authority still require "
        "accountable human verification."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
