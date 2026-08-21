#!/usr/bin/env python3
"""Fail closed if the exact Track 009 candidate escapes synthetic preparation."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

MERGE_COMMIT = "a9ef5b1ffdba55a0d45faf670d8679d890e414d6"
MERGE_TREE = "6fa0fd46a54db0970ba04611f6cf90443525b9b7"
MANIFEST = Path("manifests/ledger/track-009-v0.4-candidate-2026-08-21.json")
MANIFEST_SHA256 = "82cc034860818d315a514220276658056f398df809f3884f02c4f91c02b74ec5"
ALLOWED_INPUTS = {
    "examples/ledger/public-foundation-synthetic.yml",
    "examples/ledger/economic-social-synthetic.yml",
}
ALLOWED_EXPORTS = {
    "manifests/ledger/track-009-v0.4-public-foundation-synthetic.json",
    "manifests/ledger/track-009-v0.4-economic-social-synthetic.json",
}


class CandidateContainmentError(ValueError):
    """The provisional candidate no longer satisfies its containment boundary."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_tree(root: Path, commit: str) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", f"{commit}^{{tree}}"],
        cwd=root,
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


def validate(root: Path) -> None:
    if _git_tree(root, MERGE_COMMIT) != MERGE_TREE:
        raise CandidateContainmentError("exact merged candidate commit/tree drift")
    manifest_path = root / MANIFEST
    if _sha256(manifest_path) != MANIFEST_SHA256:
        raise CandidateContainmentError("candidate manifest hash drift")
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.root.resolve())
    except (CandidateContainmentError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Track 009 candidate containment failed: {exc}")
        return 1
    print("Track 009 exact merged candidate remains synthetic-only, provisional and unfrozen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
