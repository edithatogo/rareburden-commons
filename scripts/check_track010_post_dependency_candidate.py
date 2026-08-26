#!/usr/bin/env python3
"""Validate the corrected Track 010 bounded post-dependency candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.build_track010_post_dependency_candidate import (
        ANALYSIS_SPEC,
        ENGINE_RECEIPT,
        LOCKFILE,
        MODEL,
        REFERENCE,
        RESULT_SCHEMA,
        TRACK003_PROFILE,
        TRACK009_COMPLETION,
        TRACK009_FREEZE,
        build,
    )
except ModuleNotFoundError:  # Direct execution places scripts/ on sys.path.
    from build_track010_post_dependency_candidate import (  # type: ignore[no-redef]
        ANALYSIS_SPEC,
        ENGINE_RECEIPT,
        LOCKFILE,
        MODEL,
        REFERENCE,
        RESULT_SCHEMA,
        TRACK003_PROFILE,
        TRACK009_COMPLETION,
        TRACK009_FREEZE,
        build,
    )

SOURCE_COMMIT = "4ef8a1118b720ad844d0ea7e62dc18a090bc92a1"
SOURCE_TREE = "c9f153daa76bfe5bfa1343c6c8e91ef10529f11e"
MANIFEST = Path("manifests/burden/track-010-post-dependency-candidate-2026-08-27.json")
MANIFEST_SHA256 = "bc48be8368d40cac70ee965e913c837d54fb0f4d638de234b6fb0f681ef22745"
COMPATIBILITY = Path("manifests/burden/track-010-post-dependency-compatibility-2026-08-27.json")
COMPATIBILITY_SHA256 = "ee5d9a0cb1f07a293576d330de70cde82040ebf94756a183d9b50f5080118031"
BUILD_INPUTS = [
    ENGINE_RECEIPT,
    ANALYSIS_SPEC,
    TRACK009_FREEZE,
    TRACK009_COMPLETION,
    TRACK003_PROFILE,
    REFERENCE,
    RESULT_SCHEMA,
    MODEL,
    LOCKFILE,
]
EXPECTED_FALSE_CLAIMS = {
    "scientific_approval",
    "engineering_approval",
    "patient_community_approval",
    "independent_review",
    "public_aggregate_execution",
    "empirical_or_production_activation",
    "track_003_eligible",
    "alpha_interface_frozen",
    "public_readiness",
    "publication_authority",
    "release_authority",
    "track_complete",
}


class Track010PostDependencyError(ValueError):
    """The corrected candidate escaped its bounded authority."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_tree(root: Path, commit: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", f"{commit}^{{tree}}"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Track010PostDependencyError(f"expected object in {path}")
    return value


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Track010PostDependencyError(f"expected mapping in {path}")
    return value


def _verify_regeneration(root: Path) -> None:
    runs: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="track010-post-dependency-") as temporary:
        temporary_root = Path(temporary)
        for index in range(2):
            run_root = temporary_root / f"run-{index + 1}"
            runs.append(run_root)
            for relative in BUILD_INPUTS:
                target = run_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / relative, target)
            build(
                root=run_root,
                source_commit=SOURCE_COMMIT,
                source_tree=SOURCE_TREE,
                manifest=MANIFEST,
                compatibility=COMPATIBILITY,
            )
        for relative in (MANIFEST, COMPATIBILITY):
            first = (runs[0] / relative).read_bytes()
            if first != (runs[1] / relative).read_bytes():
                raise Track010PostDependencyError(f"nondeterministic drift: {relative}")
            if first != (root / relative).read_bytes():
                raise Track010PostDependencyError(f"checked-in regeneration drift: {relative}")


def validate(root: Path) -> None:
    if _git_tree(root, SOURCE_COMMIT) != SOURCE_TREE:
        raise Track010PostDependencyError("source commit/tree drift")
    if _sha256(root / MANIFEST) != MANIFEST_SHA256:
        raise Track010PostDependencyError("candidate manifest hash drift")
    if _sha256(root / COMPATIBILITY) != COMPATIBILITY_SHA256:
        raise Track010PostDependencyError("compatibility receipt hash drift")

    manifest = _load_json(root / MANIFEST)
    compatibility = _load_json(root / COMPATIBILITY)
    claims = manifest.get("claims", {})
    if (
        manifest.get("candidate_status") != "prepared_bounded_post_dependency_not_alpha_not_frozen"
        or manifest.get("candidate_interface") != "corrected-provisional-pre-alpha"
        or claims.get("track_009_dependency_satisfied") is not True
        or any(claims.get(name) is not False for name in EXPECTED_FALSE_CLAIMS)
    ):
        raise Track010PostDependencyError("candidate claims escaped bounded scope")
    if (
        compatibility.get("status") != "bounded_post_dependency_preparation_only_not_alpha"
        or compatibility.get("adapter", {}).get("state") != "versioned_provisional"
        or compatibility.get("adapter", {}).get("stable_surface") is not False
        or compatibility.get("adapter", {}).get("direct_empirical_input") is not False
    ):
        raise Track010PostDependencyError("compatibility boundary escaped")

    completion = _load_yaml(root / TRACK009_COMPLETION)
    if (
        completion.get("authorization", {}).get("track_complete") is not True
        or completion.get("claims", {}).get("empirical_parameter_activation") is not False
        or completion.get("claims", {}).get("controlled_data_activation") is not False
        or completion.get("claims", {}).get("release_authority") is not False
    ):
        raise Track010PostDependencyError("Track 009 bounded completion scope drift")
    result_schema = _load_json(root / RESULT_SCHEMA)
    required = set(result_schema.get("required", []))
    if not {"intended_use", "activation_state", "interpretation", "limitations"} <= required:
        raise Track010PostDependencyError("portable result labels are not mandatory")
    _verify_regeneration(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.root.resolve())
    except (Track010PostDependencyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Track 010 post-dependency candidate failed: {exc}")
        return 1
    print(
        "Track 010 corrected candidate regenerates byte-for-byte and remains bounded, "
        "not activated, pre-alpha and unfrozen."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
