#!/usr/bin/env python3
"""Validate complete criterion indexing without inferring stable acceptance."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


class V1EvidenceIndexError(ValueError):
    """Raised when the v1 evidence index is incomplete, stale, or overclaimed."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_v1_index(index: dict[str, Any], root: Path) -> dict[str, Any]:
    contract = Path(str(index.get("acceptance_contract", "")))
    if contract.is_absolute() or ".." in contract.parts or not (root / contract).is_file():
        raise V1EvidenceIndexError("acceptance contract path is unsafe or missing")
    contract_ids = re.findall(
        r"^\| (V1-[A-Z]+-\d+) \|",
        (root / contract).read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    indexed_ids = [
        criterion
        for group in index.get("criterion_groups", [])
        for criterion in group.get("criteria", [])
    ]
    if len(indexed_ids) != len(set(indexed_ids)):
        raise V1EvidenceIndexError("criterion IDs must not be duplicated")
    missing = sorted(set(contract_ids) - set(indexed_ids))
    extra = sorted(set(indexed_ids) - set(contract_ids))
    if missing or extra or indexed_ids != contract_ids:
        raise V1EvidenceIndexError(f"criterion coverage mismatch: missing={missing}, extra={extra}")
    if index.get("criterion_count") != len(contract_ids) or index.get("index_complete") is not True:
        raise V1EvidenceIndexError("complete index count and status must match the contract")

    bound_paths: set[str] = set()
    for binding in index.get("evidence_bindings", []):
        relative = Path(str(binding.get("artifact", "")))
        if relative.is_absolute() or ".." in relative.parts:
            raise V1EvidenceIndexError(f"unsafe evidence path: {relative}")
        artifact = root / relative
        if not artifact.is_file() or _sha256(artifact) != binding.get("sha256"):
            raise V1EvidenceIndexError(f"evidence hash mismatch: {relative}")
        bound_paths.add(str(relative))
    for group in index.get("criterion_groups", []):
        if not group.get("evidence") or not group.get("gap"):
            raise V1EvidenceIndexError("every criterion group needs evidence and an explicit gap")
        if any(path not in bound_paths for path in group["evidence"]):
            raise V1EvidenceIndexError("criterion evidence must be hash-bound")
        if group.get("release_gate_satisfied") is not False:
            raise V1EvidenceIndexError("indexing cannot satisfy stable release criteria")
    if index.get("release_acceptance_complete") is not False:
        raise V1EvidenceIndexError("release acceptance must remain incomplete")
    unsafe = sorted(key for key, value in index.get("claims", {}).items() if value is not False)
    if unsafe:
        raise V1EvidenceIndexError("v1 release and authority claims must remain false")
    required_pending = {
        "qualifying backup continuity evidence",
        "exact owner v1 candidate decision",
        "public stable artifact publication and verification",
    }
    if set(index.get("pending_release_actions", [])) != required_pending:
        raise V1EvidenceIndexError("all remaining release actions must stay explicit")
    return {
        "criterion_count": len(contract_ids),
        "group_count": len(index["criterion_groups"]),
        "index_complete": True,
        "release_acceptance_complete": False,
        "pending_release_action_count": len(required_pending),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("index", type=Path)
    parser.add_argument("--root", type=Path, default=Path())
    args = parser.parse_args()
    payload = json.loads(args.index.read_text(encoding="utf-8"))
    print(json.dumps(validate_v1_index(payload, args.root.resolve()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
