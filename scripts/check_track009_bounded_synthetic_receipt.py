#!/usr/bin/env python3
"""Validate the bounded Track 009 synthetic technical sub-completion."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from rareburden.schema import SchemaValidationError, validate_document_files
from scripts.check_track009_source_profile_role import validate as validate_profile_role


class Track009SyntheticReceiptError(ValueError):
    """Raised when scoped Track 009 completion escapes its synthetic boundary."""


ROOT = Path(__file__).parents[1]
RECEIPT = Path("docs/track-009-bounded-synthetic-technical-receipt-2026-08-22.yml")
SCHEMA = Path("schemas/track-009-bounded-synthetic-technical-receipt.schema.json")
MATRIX = Path("examples/ledger/source-profile-role-structural-synthetic.yml")
MATRIX_SCHEMA = Path("schemas/source-profile-role-structural-assessment.schema.json")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise Track009SyntheticReceiptError("receipt path is missing")
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise Track009SyntheticReceiptError(f"receipt path escapes repository: {value}") from exc
    if not path.is_file():
        raise Track009SyntheticReceiptError(f"receipt artifact is missing: {value}")
    return path


def _git_tree(root: Path, commit: str) -> str:
    # Mutation tests use an isolated artifact root without a .git directory;
    # production validation always runs from the repository root.
    git_root = root if (root / ".git").exists() else ROOT
    try:
        return subprocess.run(
            ["git", "rev-parse", f"{commit}^{{tree}}"],
            cwd=git_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Track009SyntheticReceiptError("candidate commit cannot be resolved") from exc


def validate(root: Path, receipt_path: Path = RECEIPT, schema_path: Path = SCHEMA) -> None:
    receipt = validate_document_files(root / receipt_path, root / schema_path)
    candidate = receipt["candidate"]
    if _git_tree(root, candidate["commit"]) != candidate["tree"]:
        raise Track009SyntheticReceiptError("candidate commit/tree binding drift")

    review = receipt["review_packet"]
    review_path = _resolve(root, review["path"])
    if _sha256(review_path) != review["sha256"]:
        raise Track009SyntheticReceiptError("review packet hash drift")
    if review["candidate_commit"] != _git_tree_commit(
        root, review["candidate_commit"], review["candidate_tree"]
    ):
        raise Track009SyntheticReceiptError("review packet candidate binding drift")
    if (
        candidate["repository_commit"] != review["candidate_commit"]
        or candidate["repository_tree"] != review["candidate_tree"]
    ):
        raise Track009SyntheticReceiptError("repository candidate binding drift")
    validate_document_files(
        review_path,
        root / "schemas/agent-owner-decision-packet.schema.json",
    )

    for path_field, hash_field in (
        ("manifest", "manifest_sha256"),
        ("migration_receipt", "migration_sha256"),
        ("schema", "schema_sha256"),
        ("profile_role_matrix", "profile_role_matrix_sha256"),
    ):
        path = _resolve(root, candidate[path_field])
        if _sha256(path) != candidate[hash_field]:
            raise Track009SyntheticReceiptError(f"candidate hash drift: {candidate[path_field]}")

    manifest = json.loads(_resolve(root, candidate["manifest"]).read_text(encoding="utf-8"))
    if (
        manifest.get("candidate_status") != "prepared_synthetic_only_not_frozen"
        or manifest.get("track") != "009-evidence-parameter-ledger"
        or any(value is not False for value in manifest.get("claims", {}).values())
    ):
        raise Track009SyntheticReceiptError("candidate manifest overstates synthetic scope")

    validate_profile_role(root, MATRIX, MATRIX_SCHEMA)

    blocker_ids = [row["id"] for row in receipt["global_blockers"]]
    if blocker_ids != ["EPI-MED-01", "EPI-MED-02", "GOV-MED-01"]:
        raise Track009SyntheticReceiptError("global blockers must remain explicit and ordered")

    metadata_path = root / "conductor/tracks/009-evidence-parameter-ledger/metadata.json"
    metadata: dict[str, Any] = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("status") != "blocked":
        raise Track009SyntheticReceiptError("global Track 009 status must remain blocked")


def _git_tree_commit(root: Path, commit: str, expected_tree: str) -> str:
    tree = _git_tree(root, commit)
    if tree != expected_tree:
        raise Track009SyntheticReceiptError("candidate commit/tree binding drift")
    return commit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path, nargs="?", default=RECEIPT)
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        validate(args.root.resolve(), args.receipt, args.schema)
    except (OSError, SchemaValidationError, Track009SyntheticReceiptError) as exc:
        print(f"Track 009 bounded synthetic receipt failed: {exc}")
        return 1
    print(
        "Track 009 bounded synthetic technical receipt passed; global empirical "
        "gates remain blocked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
