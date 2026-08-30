#!/usr/bin/env python3
"""Check the immutable first outcome/service evidence tranche, offline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

EXPECTED_SHA256 = "12d6efe981913934e92de2f28957b8b4632b3763be2702ebfe229612afa7f10c"


def validate(path: Path) -> None:
    """Reject drift in any provenance, fact, context, gap or authority field."""
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("outcome/service ledger must be a mapping")
    payload = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(
            "outcome/service evidence or boundary drift; exact review and re-pinning required"
        )
    if any(value is not False for value in document["authority_boundaries"].values()):
        raise ValueError("outcome/service authority escalation")
    if {record["family"] for record in document["records"]} != {
        "diagnosis_delay",
        "treatment_change",
    }:
        raise ValueError("extracted evidence family drift")
    if any(record["reported_result"] is not None for record in document["held_candidates"]):
        raise ValueError("held source has been promoted to quantitative evidence")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    validate(parser.parse_args().path)
    print("Track 003 outcome/service partial ledger passed; execution remains disabled")


if __name__ == "__main__":
    main()
