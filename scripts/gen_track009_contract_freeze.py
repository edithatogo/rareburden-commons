#!/usr/bin/env python3
"""Generate or verify the Track 009 v0.4 ledger contract freeze manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "8285d868fe25c056eed1f2ce37bd64e4baa7a4b5"
OUTPUT = Path("manifests/ledger/track-009-v0.4-contract-freeze.json")
OWNER_DISPOSITION = Path("docs/decisions/2026-08-22-track-009-owner-v04-freeze-disposition.yml")


def h(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def _owner_disposition() -> dict[str, Any]:
    value = yaml.safe_load((ROOT / OWNER_DISPOSITION).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Track 009 owner disposition must be a mapping")
    claims = value.get("claims", {})
    authorization = value.get("freeze_authorization", {})
    if (
        value.get("track_id") != "009-evidence-parameter-ledger"
        or value.get("decision_type") != "owner_v04_contract_freeze_disposition"
        or value.get("decided_by") != "edithatogo"
        or value.get("independent_review") is not False
        or not isinstance(authorization, dict)
        or authorization.get("authorized") is not True
        or authorization.get("freeze_manifest") != OUTPUT.as_posix()
        or not isinstance(claims, dict)
        or claims.get("contract_frozen") is not True
        or claims.get("track_complete") is not False
        or claims.get("release_authority") is not False
    ):
        raise ValueError("Track 009 owner disposition escaped its bounded authority")
    return value


def build_manifest() -> dict[str, Any]:
    _owner_disposition()
    schemas = [
        "schemas/parameter-ledger.schema.json",
        "schemas/evidence-assessment.schema.json",
        "schemas/assumption.schema.json",
        "schemas/analysis-specification.schema.json",
    ]
    advisory = [
        "docs/decisions/2026-08-22-track-009-panel-packet-epi-med-01.yml",
        "docs/decisions/2026-08-22-track-009-panel-packet-rights-01.yml",
        "docs/decisions/2026-08-22-track-009-findings-panel-routing.yml",
        "docs/decisions/2026-08-22-track-009-owner-engineering-review.yml",
    ]
    candidate = "manifests/ledger/track-009-v0.4-candidate-2026-08-21.json"
    return {
        "schema_version": "1.0.0",
        "freeze_id": "track-009-v0.4-ledger-contract-freeze-2026-08-22",
        "track": "009-evidence-parameter-ledger",
        "contract_version": "v0.4",
        "candidate_status": "frozen_synthetic_and_receipted_public_aggregate_scope",
        "frozen_at_utc": "2026-08-22T00:00:00Z",
        "frozen_by": "edithatogo",
        "accountable_role": "repository owner and sole accountable human",
        "binding_baseline": {
            "repository_commit": BASELINE_COMMIT,
            "candidate_manifest": candidate,
            "candidate_manifest_sha256": h(candidate),
            "note": (
                "Containment-managed candidate keeps status "
                "prepared_synthetic_only_not_frozen; this artifact freezes the "
                "contract surface, not the candidate."
            ),
        },
        "scope": (
            "synthetic ledgers and exactly-receipted public aggregates under "
            "recorded terms dispositions only"
        ),
        "frozen_contract_surfaces": [{"path": s, "sha256": h(s)} for s in schemas],
        "licence_gating": {
            "requirement": (
                "every ledger record carries licence_state; unreceipted or "
                "non-permissive sources cannot activate"
            ),
            "unreceipted_source_activation": "fail_closed",
        },
        "advisory_basis": [{"path": a, "sha256": h(a)} for a in advisory],
        "owner_disposition": {
            "path": OWNER_DISPOSITION.as_posix(),
            "sha256": h(OWNER_DISPOSITION.as_posix()),
        },
        "invalidation": (
            "any drift in bound contract surfaces, advisory basis, candidate "
            "manifest or upstream semantic bindings voids this freeze"
        ),
        "claims": {
            "contract_frozen": True,
            "scope_synthetic_and_receipted_public_aggregate_only": True,
            "empirical_parameter_activation": False,
            "controlled_data_in_scope": False,
            "independent_review": False,
            "track_complete": False,
            "release_authority": False,
        },
    }


def render_manifest() -> bytes:
    """Return deterministic UTF-8 bytes for the exact bounded freeze."""
    return (json.dumps(build_manifest(), indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = ROOT / OUTPUT
    rendered = render_manifest()
    if args.check:
        if not output.is_file() or output.read_bytes() != rendered:
            print(f"Track 009 contract freeze manifest drift: {OUTPUT}")
            return 1
        print(f"Track 009 contract freeze manifest passed: {OUTPUT}")
        return 0
    output.write_bytes(rendered)
    print(f"written {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
