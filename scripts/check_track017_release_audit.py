#!/usr/bin/env python3
"""Check the owner-operated Track 017 release-readiness audit boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_COMMIT = "8da7c861a8502e762a7245fe56408ed8c6911bb1"
EXPECTED_TREE = "e0d772f7d640f395ed6adf66cd611c228611e06c"
REQUIRED = (
    "docs/v1-release-candidate-checklist-017.md",
    "docs/v1-evidence-index-2026-08-16.md",
    "docs/track-017-real-data-adoption-guidance-2026-09-08.yml",
    "manifests/release/v1-evidence-index-2026-08-16.json",
    "manifests/release/track-017-bounded-exercises-2026-08-16.json",
)


def audit(root: Path) -> dict[str, object]:
    hashes: dict[str, str] = {}
    for relative in REQUIRED:
        path = root / relative
        if not path.is_file():
            raise ValueError(f"missing Track 017 evidence: {relative}")
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    metadata = json.loads(
        (root / "conductor/tracks/017-documentation-adoption-v1/metadata.json").read_text(
            encoding="utf-8"
        )
    )
    if metadata.get("status") != "blocked":
        raise ValueError("Track 017 metadata must remain blocked")
    return {
        "track_id": "017-documentation-adoption-v1",
        "candidate_commit": EXPECTED_COMMIT,
        "candidate_tree": EXPECTED_TREE,
        "evidence_sha256": hashes,
        "owner_operated_clean_candidate_count": 2,
        "owner_operated_reproduction": "passed_non_independent",
        "independent_review": False,
        "stable_release_authorized": False,
        "tag_created": False,
        "publication_verified": False,
        "post_publication_verification": False,
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
