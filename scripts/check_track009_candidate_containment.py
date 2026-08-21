#!/usr/bin/env python3
"""Fail closed if the exact Track 009 candidate escapes synthetic preparation."""

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
    from scripts.build_track009_v04_candidate import build
except ModuleNotFoundError:  # Direct script execution has scripts/ on sys.path.
    from build_track009_v04_candidate import build

MERGE_COMMIT = "a9ef5b1ffdba55a0d45faf670d8679d890e414d6"
MERGE_TREE = "6fa0fd46a54db0970ba04611f6cf90443525b9b7"
MANIFEST = Path("manifests/ledger/track-009-v0.4-candidate-2026-08-21.json")
MANIFEST_SHA256 = "82cc034860818d315a514220276658056f398df809f3884f02c4f91c02b74ec5"
DECISION = Path("docs/decisions/2026-08-21-track-009-post-merge-options.yml")
DECISION_SHA256 = "d6b7454973c87d650fb381f5a5b7b152e3b75dcbab41599c99536dc504958562"
ALLOWED_INPUTS = {
    "examples/ledger/public-foundation-synthetic.yml",
    "examples/ledger/economic-social-synthetic.yml",
}
ALLOWED_EXPORTS = {
    "manifests/ledger/track-009-v0.4-public-foundation-synthetic.json",
    "manifests/ledger/track-009-v0.4-economic-social-synthetic.json",
}
SCHEMA = Path("schemas/parameter-ledger.schema.json")
MIGRATION = Path("manifests/ledger/track-009-v0.4-migration-impact-2026-08-21.json")
REGENERATED_ARTIFACTS = {*ALLOWED_EXPORTS, MANIFEST.as_posix(), MIGRATION.as_posix()}


class CandidateContainmentError(ValueError):
    """The provisional candidate no longer satisfies its containment boundary."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_tree(root: Path, commit: str) -> str:
    git_root = root if (root / ".git").exists() else Path(__file__).parents[1]
    completed = subprocess.run(
        ["git", "rev-parse", f"{commit}^{{tree}}"],
        cwd=git_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CandidateContainmentError(f"expected mapping in {path}")
    return value


def verify_regeneration(root: Path, manifest: dict[str, Any]) -> None:
    """Regenerate twice in isolation and require exact checked-in bytes."""
    source_commit = manifest.get("source_commit")
    source_tree = manifest.get("source_tree")
    ledger_paths = [Path(row["path"]) for row in manifest.get("input_ledgers", [])]
    if {path.as_posix() for path in ledger_paths} != ALLOWED_INPUTS:
        raise CandidateContainmentError("candidate synthetic input order or inventory drift")
    export_by_ledger = {row["ledger_id"]: Path(row["path"]) for row in manifest.get("exports", [])}
    export_paths: list[Path] = []
    for ledger_path in ledger_paths:
        ledger = _load_yaml(root / ledger_path)
        try:
            export_paths.append(export_by_ledger[ledger["ledger_id"]])
        except KeyError as exc:
            raise CandidateContainmentError("candidate export inventory drift") from exc

    runs: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="track009-regeneration-") as temporary:
        temporary_root = Path(temporary)
        for index in range(2):
            run_root = temporary_root / f"run-{index + 1}"
            runs.append(run_root)
            for relative in [SCHEMA, *ledger_paths]:
                target = run_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / relative, target)
            build(
                root=run_root,
                source_commit=str(source_commit),
                source_tree=str(source_tree),
                schema=SCHEMA,
                ledgers=ledger_paths,
                exports=export_paths,
                manifest=MANIFEST,
                migration=MIGRATION,
            )

        for relative_value in sorted(REGENERATED_ARTIFACTS):
            relative = Path(relative_value)
            first = (runs[0] / relative).read_bytes()
            second = (runs[1] / relative).read_bytes()
            if first != second:
                raise CandidateContainmentError(
                    f"nondeterministic regeneration drift: {relative.as_posix()}"
                )
            if first != (root / relative).read_bytes():
                raise CandidateContainmentError(
                    f"checked-in candidate regeneration drift: {relative.as_posix()}"
                )


def validate(root: Path) -> None:
    if _git_tree(root, MERGE_COMMIT) != MERGE_TREE:
        raise CandidateContainmentError("exact merged candidate commit/tree drift")
    manifest_path = root / MANIFEST
    if _sha256(manifest_path) != MANIFEST_SHA256:
        raise CandidateContainmentError("candidate manifest hash drift")
    decision_path = root / DECISION
    if _sha256(decision_path) != DECISION_SHA256:
        raise CandidateContainmentError("bounded owner disposition hash drift")
    decision = _load_yaml(decision_path)
    owner_decision = decision.get("owner_decision", {})
    if (
        decision.get("candidate", {}).get("commit") != MERGE_COMMIT
        or decision.get("candidate", {}).get("tree") != MERGE_TREE
        or decision.get("candidate", {}).get("evidence_manifest_sha256") != MANIFEST_SHA256
        or owner_decision.get("status") != "recorded"
        or owner_decision.get("selected_option_id") != "A"
        or owner_decision.get("decided_by") != "edithatogo"
    ):
        raise CandidateContainmentError("bounded owner disposition scope drift")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("candidate_status") != "prepared_synthetic_only_not_frozen"
        or manifest.get("candidate_contract") != "v0.4-provisional"
        or any(value is not False for value in manifest.get("claims", {}).values())
    ):
        raise CandidateContainmentError("candidate status or authority claims escaped")

    inputs = {row.get("path") for row in manifest.get("input_ledgers", [])}
    exports = {row.get("path") for row in manifest.get("exports", [])}
    if inputs != ALLOWED_INPUTS or exports != ALLOWED_EXPORTS:
        raise CandidateContainmentError("candidate synthetic input/export allowlist drift")

    for relative in sorted(ALLOWED_INPUTS):
        ledger = _load_yaml(root / relative)
        if "synthetic" not in str(ledger.get("ledger_id", "")):
            raise CandidateContainmentError("input ledger is not explicitly synthetic")
        parameters = ledger.get("parameters", [])
        limitation_values = list(ledger.get("limitations", []))
        for parameter in parameters:
            limitation_values.extend(parameter.get("limitations", []))
        limitations = " ".join(str(value).lower() for value in limitation_values)
        if "synthetic" not in limitations or "not" not in limitations:
            raise CandidateContainmentError("input ledger lacks a synthetic non-empirical warning")
        for parameter in parameters:
            source_ids = parameter.get("source_release_ids", [])
            semantic_ids = parameter.get("semantic_entity_ids", [])
            if any(not str(value).startswith("synthetic-") for value in source_ids):
                raise CandidateContainmentError("non-synthetic source release entered candidate")
            if any(not str(value).startswith("synthetic:") for value in semantic_ids):
                raise CandidateContainmentError(
                    "non-synthetic semantic identifier entered candidate"
                )

    verify_regeneration(root, manifest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.root.resolve())
    except (CandidateContainmentError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Track 009 candidate containment failed: {exc}")
        return 1
    print(
        "Track 009 exact merged candidate regenerates byte-for-byte and remains "
        "synthetic-only, provisional and unfrozen."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
