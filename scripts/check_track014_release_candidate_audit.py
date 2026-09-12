#!/usr/bin/env python3
"""Audit the exact Track 014 release candidate without authorising publication."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.check_track014_release_surface import validate_release_surface_manifest

COMMIT = "110da59060d1183f82b7e54e388ca18225c5e88d"
TREE = "006fc0292585f9e5ac9beb5cc5c1bf0a96cc3cd5"
SURFACE = Path("manifests/atlas/track-014-bounded-release-surface-2026-08-16.json")
ARTIFACTS = {
    Path(
        "results/track-014-reference-2026-09-06/reference-report.md"
    ): "d378fada43f9cfb289ead9e3490f849d47009814f520b73b9b03366ad553a197",
    Path(
        "results/track-014-reference-2026-09-06/reference-results.json"
    ): "756e98484ad8bc81b4346df7987dc878931d9755335e39857fa802adeaaccf31",
    Path(
        "results/track-014-reference-2026-09-06/reference-tables.csv"
    ): "495703787a4f22811325defabbadb5fe58d9ce675baba8f135df57eef54e3e3c",
}
SUPPORTING = {
    Path("docs/track-014-accessibility-checklist.md"),
    Path("docs/track-014-evidence-presentation-contract-2026-08-21.yml"),
    Path("docs/track-014-owner-installed-reproduction-receipt-2026-08-22.json"),
    Path("docs/reviews/track-014-reference-output-panel-2026-09-06.yml"),
}


class Track014AuditError(ValueError):
    """Raised when the release-candidate audit cannot be reproduced safely."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path) -> dict[str, Any]:
    surface_path = root / SURFACE
    if not surface_path.is_file():
        raise Track014AuditError(f"missing release surface: {SURFACE}")
    surface = json.loads(surface_path.read_text(encoding="utf-8"))
    surface_result = validate_release_surface_manifest(surface, root)
    if surface_result["publication_authorized"]:
        raise Track014AuditError("release surface unexpectedly authorises publication")

    artifact_hashes: dict[str, str] = {}
    for relative, expected in ARTIFACTS.items():
        path = root / relative
        if not path.is_file() or digest(path) != expected:
            raise Track014AuditError(f"reference artifact hash mismatch: {relative}")
        artifact_hashes[str(relative)] = expected
    supporting = {}
    for relative in sorted(SUPPORTING):
        path = root / relative
        if not path.is_file():
            raise Track014AuditError(f"missing supporting evidence: {relative}")
        supporting[str(relative)] = digest(path)

    return {
        "status": "exact_candidate_audit_pass_with_release_gates_pending",
        "candidate": {"commit": COMMIT, "tree": TREE},
        "release_surface": surface_result,
        "artifact_hashes": artifact_hashes,
        "supporting_evidence_hashes": supporting,
        "assessment": {
            "accessibility": "contract and advisory review pass; real-user certification absent",
            "usability": "repository-authored journeys only; user research absent",
            "reproduction": (
                "owner-operated installed-wheel reproduction pass; independent reproduction absent"
            ),
            "rights": (
                "synthetic package boundary verified; real-source redistribution "
                "scope remains pending"
            ),
            "provenance": (
                "candidate and output hashes verified; external archive/DOI authority absent"
            ),
            "release_content": (
                "exact reference outputs verified; no public artifact or endpoint published"
            ),
        },
        "claims": {
            "accessibility_approved": False,
            "independent_reproduction": False,
            "archive_or_doi_authorized": False,
            "public_artifact_verified": False,
            "release_authorized": False,
        },
        "pending_gates": [
            "independent_accessibility_and_usability_evidence",
            "independent_reproduction",
            "source_rights_and_redistribution_scope",
            "archive_or_doi_authority",
            "owner_release_authorization",
            "public_artifact_verification",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.root.resolve())
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
