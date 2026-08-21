#!/usr/bin/env python3
"""Build a deterministic, unfrozen Track 010 synthetic preparation candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

COMMIT = re.compile(r"^[0-9a-f]{40}$")
ENGINE_RECEIPT = Path("manifests/burden/track-010-bounded-synthetic-receipt-2026-08-16.json")
ANALYSIS_SPEC = Path("examples/analyses/expected-population-synthetic.yml")
TRACK009_MANIFEST = Path("manifests/ledger/track-009-v0.4-candidate-2026-08-21.json")
TRACK009_DECISION = Path("docs/decisions/2026-08-21-track-009-post-merge-options.yml")
TRACK003_PROFILE = Path("examples/demonstrators/003-ledger-profile.yml")
REFERENCE = Path("docs/burden-engine-010-reference.md")
LOCKFILE = Path("uv.lock")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.as_posix(), "sha256": _sha256(root / path)}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def build(
    *,
    root: Path,
    source_commit: str,
    source_tree: str,
    manifest: Path,
    compatibility: Path,
) -> None:
    if not COMMIT.fullmatch(source_commit) or not COMMIT.fullmatch(source_tree):
        raise ValueError("source commit and tree must be exact 40-character Git identifiers")

    compatibility_value = {
        "schema_version": "1.0.0",
        "track": "010-public-burden-engine",
        "status": "synthetic_preparation_only_not_alpha",
        "comparison": "exact provisional Track 009 and Track 003 structural binding",
        "engine": _artifact(root, ENGINE_RECEIPT),
        "analysis_specification": _artifact(root, ANALYSIS_SPEC),
        "track_009_candidate": {
            **_artifact(root, TRACK009_MANIFEST),
            "merge_commit": "a9ef5b1ffdba55a0d45faf670d8679d890e414d6",
            "merge_tree": "6fa0fd46a54db0970ba04611f6cf90443525b9b7",
            "dependency_state": "blocked_unfrozen_unsatisfied",
        },
        "track_009_bounded_owner_disposition": _artifact(root, TRACK009_DECISION),
        "track_003_interface_profile": {
            **_artifact(root, TRACK003_PROFILE),
            "binding_state": "feature_disabled_provisional_not_eligible",
        },
        "reference_contract": _artifact(root, REFERENCE),
        "dependency_lock": _artifact(root, LOCKFILE),
        "adapter": {
            "state": "versioned_provisional",
            "stable_surface": False,
            "direct_empirical_input": False,
        },
        "interpretation": (
            "Hash compatibility and deterministic synthetic execution only; not scientific "
            "fitness, independent review, Track 003 eligibility or alpha-interface stability."
        ),
    }
    _write_json(root / compatibility, compatibility_value)

    manifest_value = {
        "schema_version": "1.0.0",
        "track": "010-public-burden-engine",
        "candidate_status": "prepared_synthetic_only_not_alpha_not_frozen",
        "candidate_interface": "provisional-pre-alpha",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "engine_receipt": _artifact(root, ENGINE_RECEIPT),
        "compatibility_receipt": _artifact(root, compatibility),
        "track_009_candidate": _artifact(root, TRACK009_MANIFEST),
        "track_003_interface_profile": _artifact(root, TRACK003_PROFILE),
        "permitted_scope": [
            "deterministic synthetic descriptive computation",
            "unit and invariant failure testing",
            "provenance, reproduction, recovery and security preparation",
        ],
        "claims": {
            "scientific_approval": False,
            "engineering_approval": False,
            "patient_community_approval": False,
            "independent_review": False,
            "track_009_dependency_satisfied": False,
            "track_003_eligible": False,
            "alpha_interface_frozen": False,
            "empirical_or_production_activation": False,
            "public_readiness": False,
            "release_authority": False,
            "track_complete": False,
        },
        "invalidation": (
            "any upstream, candidate, interface, artifact or dependency-lock drift; any failed "
            "provenance or reproduction check; or any unresolved high/critical finding"
        ),
    }
    _write_json(root / manifest, manifest_value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-tree", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--compatibility", type=Path, required=True)
    args = parser.parse_args()
    build(
        root=args.root.resolve(),
        source_commit=args.source_commit,
        source_tree=args.source_tree,
        manifest=args.manifest,
        compatibility=args.compatibility,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
