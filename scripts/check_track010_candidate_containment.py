#!/usr/bin/env python3
"""Operational containment for the exact Track 010 synthetic candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.build_track010_synthetic_candidate import (
        ANALYSIS_SPEC,
        ENGINE_RECEIPT,
        LOCKFILE,
        REFERENCE,
        TRACK003_PROFILE,
        TRACK009_DECISION,
        TRACK009_MANIFEST,
        build,
    )
except ModuleNotFoundError:  # Direct execution places scripts/ on sys.path.
    from build_track010_synthetic_candidate import (  # type: ignore[no-redef]
        ANALYSIS_SPEC,
        ENGINE_RECEIPT,
        LOCKFILE,
        REFERENCE,
        TRACK003_PROFILE,
        TRACK009_DECISION,
        TRACK009_MANIFEST,
        build,
    )

MERGED_CANDIDATE_COMMIT = "22edd34e3bedeabe57fa9deb4b45be6b9498034a"
MERGED_CANDIDATE_TREE = "eda9bbcc46a3a63fd1ee5999dae1b2de32d8f3e8"
SOURCE_COMMIT = "b99615dfc72c1133d9c18a0530415ce639d628aa"
SOURCE_TREE = "0fc30cf4235aa6d03a9c0b2dc98b21aacbde5cfc"
BUILD_INPUT_COMMIT = "3fdc5076a4ea64b307421a4967fa962cc0413547"
MANIFEST = Path("manifests/burden/track-010-synthetic-candidate-2026-08-21.json")
MANIFEST_SHA256 = "a1883f906053367a4129bd8780e83ee2f170879e00bcf019c61a5e1388bfa716"
COMPATIBILITY = Path("manifests/burden/track-010-compatibility-impact-2026-08-21.json")
COMPATIBILITY_SHA256 = "303fc578b290a0089d263f7ea9dc2644ff09a20f9fe34b189686b7412a2ce3ad"
DECISION = Path("docs/decisions/2026-08-21-track-010-synthetic-candidate-disposition.yml")
DECISION_SHA256 = "f5d2d7d0d3f31fe592184c0678efcffe3a416ea93a63daaeea6080b5e9af9d9e"
BUILD_INPUTS = [
    ENGINE_RECEIPT,
    ANALYSIS_SPEC,
    TRACK009_MANIFEST,
    TRACK009_DECISION,
    TRACK003_PROFILE,
    REFERENCE,
    LOCKFILE,
]
EXPECTED_BLOCKED_CLAIMS = {
    "alpha_interface_frozen": False,
    "empirical_or_production_activation": False,
    "engineering_approval": False,
    "independent_review": False,
    "patient_community_approval": False,
    "public_readiness": False,
    "release_authority": False,
    "scientific_approval": False,
    "track_003_eligible": False,
    "track_009_dependency_satisfied": False,
    "track_complete": False,
}


class Track010ContainmentError(ValueError):
    """The accepted synthetic pre-alpha candidate escaped its boundary."""


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


def _git_bytes(root: Path, commit: str, path: Path) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path.as_posix()}"],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Track010ContainmentError(f"expected object in {path}")
    return value


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Track010ContainmentError(f"expected mapping in {path}")
    return value


def _verify_regeneration(root: Path) -> None:
    runs: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="track010-containment-") as temporary:
        temporary_root = Path(temporary)
        for index in range(2):
            run_root = temporary_root / f"run-{index + 1}"
            runs.append(run_root)
            for relative in BUILD_INPUTS:
                target = run_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(_git_bytes(root, BUILD_INPUT_COMMIT, relative))
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
                raise Track010ContainmentError(f"nondeterministic drift: {relative}")
            if first != (root / relative).read_bytes():
                raise Track010ContainmentError(f"checked-in regeneration drift: {relative}")


def validate(root: Path) -> None:
    if _git_tree(root, MERGED_CANDIDATE_COMMIT) != MERGED_CANDIDATE_TREE:
        raise Track010ContainmentError("exact merged candidate commit/tree drift")
    if _sha256(root / MANIFEST) != MANIFEST_SHA256:
        raise Track010ContainmentError("candidate manifest hash drift")
    if _sha256(root / COMPATIBILITY) != COMPATIBILITY_SHA256:
        raise Track010ContainmentError("compatibility receipt hash drift")
    if _sha256(root / DECISION) != DECISION_SHA256:
        raise Track010ContainmentError("owner disposition hash drift")

    manifest = _load_json(root / MANIFEST)
    compatibility = _load_json(root / COMPATIBILITY)
    decision = _load_yaml(root / DECISION)
    claims = manifest.get("claims")
    if (
        manifest.get("candidate_status") != "prepared_synthetic_only_not_alpha_not_frozen"
        or manifest.get("candidate_interface") != "provisional-pre-alpha"
        or claims != EXPECTED_BLOCKED_CLAIMS
    ):
        raise Track010ContainmentError("candidate status or blocked claims escaped")
    if (
        compatibility.get("status") != "synthetic_preparation_only_not_alpha"
        or compatibility.get("track_009_candidate", {}).get("dependency_state")
        != "blocked_unfrozen_unsatisfied"
        or compatibility.get("track_003_interface_profile", {}).get("binding_state")
        != "feature_disabled_provisional_not_eligible"
        or compatibility.get("adapter", {}).get("state") != "versioned_provisional"
        or compatibility.get("adapter", {}).get("stable_surface") is not False
        or compatibility.get("adapter", {}).get("direct_empirical_input") is not False
    ):
        raise Track010ContainmentError("compatibility or provisional-adapter boundary escaped")
    owner = decision.get("owner_decision", {})
    if (
        decision.get("candidate", {}).get("commit") != MERGED_CANDIDATE_COMMIT
        or decision.get("candidate", {}).get("tree") != MERGED_CANDIDATE_TREE
        or decision.get("candidate", {}).get("evidence_manifest_sha256") != MANIFEST_SHA256
        or owner.get("status") != "recorded"
        or owner.get("selected_option_id") != "A"
        or owner.get("decided_by") != "edithatogo"
    ):
        raise Track010ContainmentError("bounded owner disposition scope drift")
    for field in (
        "engine_receipt",
        "compatibility_receipt",
        "track_009_candidate",
        "track_003_interface_profile",
    ):
        artifact = manifest.get(field, {})
        if _sha256(root / artifact.get("path", "")) != artifact.get("sha256"):
            raise Track010ContainmentError(f"candidate artifact drift: {field}")
    profile = _load_yaml(root / TRACK003_PROFILE)
    if profile.get("status") != "non_binding_draft":
        raise Track010ContainmentError("Track 003 profile escaped non-binding draft status")
    _verify_regeneration(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.root.resolve())
    except (Track010ContainmentError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Track 010 candidate containment failed: {exc}")
        return 1
    print(
        "Track 010 exact candidate regenerates byte-for-byte and remains disposable, "
        "synthetic-only, pre-alpha and unfrozen."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
