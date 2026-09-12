#!/usr/bin/env python3
"""Check the owner-operated Track 016 audit boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_COMMIT = "8da7c861a8502e762a7245fe56408ed8c6911bb1"
EXPECTED_TREE = "e0d772f7d640f395ed6adf66cd611c228611e06c"
REQUIRED = (
    "docs/track-016-production-release-readiness-2026-08-21.yml",
    "docs/track-016-operations-review-packet.md",
    "docs/track-016-owner-operated-exercise-receipt-2026-08-16.json",
    "docs/track-016-real-data-operations-boundary-2026-09-08.yml",
)


def audit(root: Path) -> dict[str, object]:
    hashes: dict[str, str] = {}
    for relative in REQUIRED:
        path = root / relative
        if not path.is_file():
            raise ValueError(f"missing Track 016 evidence: {relative}")
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    readiness = (root / REQUIRED[0]).read_text(encoding="utf-8")
    for marker in (
        'status: "blocked"',
        "production_operations_enabled: false",
        "independent_operator_review_complete: false",
        "independent_security_review_complete: false",
        "release_authorized: false",
    ):
        if marker not in readiness:
            raise ValueError(f"Track 016 readiness boundary missing: {marker}")
    return {
        "track_id": "016-security-reliability-operations",
        "candidate_commit": EXPECTED_COMMIT,
        "candidate_tree": EXPECTED_TREE,
        "evidence_sha256": hashes,
        "owner_operated_checks": "passed_against_exact_baseline",
        "independent_security_review": False,
        "independent_operator_review": False,
        "production_operations": False,
        "release_authorized": False,
        "publication_verified": False,
        "status": "blocked_external_gates_remain",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(audit(args.root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
