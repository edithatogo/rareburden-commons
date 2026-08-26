#!/usr/bin/env python3
"""Build the corrected Track 010 bounded post-dependency candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

COMMIT = re.compile(r"^[0-9a-f]{40}$")
ENGINE_RECEIPT = Path("manifests/burden/track-010-bounded-synthetic-receipt-2026-08-27.json")
ANALYSIS_SPEC = Path("examples/analyses/expected-population-synthetic.yml")
TRACK009_FREEZE = Path("manifests/ledger/track-009-v0.4-contract-freeze.json")
TRACK009_COMPLETION = Path(
    "docs/decisions/2026-08-26-track-009-bounded-completion-authorization.yml"
)
TRACK003_PROFILE = Path("examples/demonstrators/003-ledger-profile.yml")
REFERENCE = Path("docs/burden-engine-010-reference.md")
RESULT_SCHEMA = Path("schemas/analysis-result.schema.json")
MODEL = Path("src/rareburden/model.py")
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
        "status": "bounded_post_dependency_preparation_only_not_alpha",
        "comparison": "corrected Track 010 interface bound to completed Track 009 contract",
        "engine_receipt": _artifact(root, ENGINE_RECEIPT),
        "analysis_specification": _artifact(root, ANALYSIS_SPEC),
        "track_009_contract_freeze": _artifact(root, TRACK009_FREEZE),
        "track_009_bounded_completion": _artifact(root, TRACK009_COMPLETION),
        "track_003_interface_profile": {
            **_artifact(root, TRACK003_PROFILE),
            "binding_state": "feature_disabled_provisional_not_eligible",
        },
        "reference_contract": _artifact(root, REFERENCE),
        "analysis_result_schema": _artifact(root, RESULT_SCHEMA),
        "model_implementation": _artifact(root, MODEL),
        "dependency_lock": _artifact(root, LOCKFILE),
        "adapter": {
            "state": "versioned_provisional",
            "stable_surface": False,
            "direct_empirical_input": False,
        },
        "interpretation": (
            "Corrected fail-closed interface and deterministic synthetic execution only; "
            "not empirical activation, independent review, Track 003 eligibility, alpha "
            "freeze, publication or release authority."
        ),
    }
    _write_json(root / compatibility, compatibility_value)

    manifest_value = {
        "schema_version": "1.0.0",
        "track": "010-public-burden-engine",
        "candidate_status": "prepared_bounded_post_dependency_not_alpha_not_frozen",
        "candidate_interface": "corrected-provisional-pre-alpha",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "engine_receipt": _artifact(root, ENGINE_RECEIPT),
        "compatibility_receipt": _artifact(root, compatibility),
        "track_009_contract_freeze": _artifact(root, TRACK009_FREEZE),
        "track_009_bounded_completion": _artifact(root, TRACK009_COMPLETION),
        "track_003_interface_profile": _artifact(root, TRACK003_PROFILE),
        "permitted_scope": [
            "deterministic synthetic descriptive computation",
            "unit, invariant, intended-use and context compatibility failure testing",
            "interface preparation for exactly-receipted public aggregates without activation",
            "provenance, reproduction, recovery and security preparation",
        ],
        "claims": {
            "track_009_dependency_satisfied": True,
            "scientific_approval": False,
            "engineering_approval": False,
            "patient_community_approval": False,
            "independent_review": False,
            "public_aggregate_execution": False,
            "empirical_or_production_activation": False,
            "track_003_eligible": False,
            "alpha_interface_frozen": False,
            "public_readiness": False,
            "publication_authority": False,
            "release_authority": False,
            "track_complete": False,
        },
        "invalidation": (
            "any source commit, interface, bound artifact, Track 009 contract, dependency-lock "
            "or review drift; any failed provenance, reproduction, memory or security check; "
            "or any unresolved high or critical finding"
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
