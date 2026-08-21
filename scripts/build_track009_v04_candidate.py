#!/usr/bin/env python3
"""Build deterministic synthetic Track 009 candidate and migration evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from rareburden.ledger import load_ledger

COMMIT = re.compile(r"^[0-9a-f]{40}$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def build(
    *,
    root: Path,
    source_commit: str,
    source_tree: str,
    schema: Path,
    ledgers: list[Path],
    exports: list[Path],
    manifest: Path,
    migration: Path,
) -> None:
    if not COMMIT.fullmatch(source_commit) or not COMMIT.fullmatch(source_tree):
        raise ValueError("source commit and tree must be exact 40-character Git identifiers")
    if len(ledgers) != len(exports) or not ledgers:
        raise ValueError("each input ledger requires one export path")

    exported: list[dict[str, Any]] = []
    for ledger_path, export_path in zip(ledgers, exports, strict=True):
        ledger = load_ledger(root / ledger_path, root / schema)
        _write_json(root / export_path, ledger.portable_document())
        exported.append(
            {
                "ledger_id": ledger.document["ledger_id"],
                "path": export_path.as_posix(),
                "parameters": len(ledger.records),
                "sha256": _sha256(root / export_path),
            }
        )

    schema_hash = _sha256(root / schema)
    migration_value = {
        "schema_version": "1.0.0",
        "track": "009-evidence-parameter-ledger",
        "candidate_contract": "v0.4-provisional",
        "comparison": "self-baseline deterministic regeneration check",
        "schema_path": schema.as_posix(),
        "previous_schema_sha256": schema_hash,
        "current_schema_sha256": schema_hash,
        "exports": exported,
        "interpretation": (
            "The synthetic exports reproduce their own candidate baseline. "
            "This is not an approved schema migration, empirical validation or ledger freeze."
        ),
    }
    _write_json(root / migration, migration_value)

    manifest_value = {
        "schema_version": "1.0.0",
        "track": "009-evidence-parameter-ledger",
        "candidate_status": "prepared_synthetic_only_not_frozen",
        "candidate_contract": "v0.4-provisional",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "schema": {"path": schema.as_posix(), "sha256": schema_hash},
        "input_ledgers": [
            {"path": path.as_posix(), "sha256": _sha256(root / path)} for path in ledgers
        ],
        "exports": exported,
        "migration_receipt": {
            "path": migration.as_posix(),
            "sha256": _sha256(root / migration),
        },
        "claims": {
            "empirical_parameter_activation": False,
            "epidemiology_approval": False,
            "data_governance_approval": False,
            "engineering_approval": False,
            "independent_review": False,
            "contract_frozen": False,
            "track_complete": False,
        },
        "invalidation": "any input, export, schema, upstream semantic or evidence hash drift",
    }
    _write_json(root / manifest, manifest_value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-tree", required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, action="append", required=True)
    parser.add_argument("--export", type=Path, action="append", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--migration", type=Path, required=True)
    args = parser.parse_args()
    build(
        root=args.root.resolve(),
        source_commit=args.source_commit,
        source_tree=args.source_tree,
        schema=args.schema,
        ledgers=args.ledger,
        exports=args.export,
        manifest=args.manifest,
        migration=args.migration,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
