"""Validate and fingerprint the bounded Track 008 source-release inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_inventory(document: dict[str, Any], root: Path) -> dict[str, Any]:
    if document.get("status") != "bounded_source_reconciliation":
        raise ValueError("inventory must remain bounded_source_reconciliation")
    claims = document.get("claims")
    if not isinstance(claims, dict) or any(claims.values()):
        raise ValueError("all Track 008 activation and completeness claims must remain false")
    if document.get("activation") != "synthetic_and_metadata_only_no_v0_4_freeze":
        raise ValueError("inventory must not activate or freeze the semantic contract")
    records = document.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("inventory requires source records")
    seen: set[str] = set()
    rendered: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("source record must be an object")
        source_id = record.get("source_id")
        if not isinstance(source_id, str) or source_id in seen:
            raise ValueError("source_id values must be non-empty and unique")
        seen.add(source_id)
        evidence = record.get("release_evidence")
        if not isinstance(evidence, str):
            raise ValueError(f"{source_id} requires release_evidence")
        evidence_path = (root / evidence).resolve()
        if root.resolve() not in evidence_path.parents or not evidence_path.is_file():
            raise ValueError(f"{source_id} release_evidence is missing or unsafe")
        public_bytes = record.get("byte_route") in {
            "public_rights_filtered_archive",
            "public_or_private_rights_filtered_archive",
        }
        licence_state = str(record.get("licence_state", ""))
        if public_bytes and "cc_by_4_0" not in licence_state:
            raise ValueError(f"{source_id} public byte route lacks exact permissive terms")
        if record.get("byte_route") == "private_licensed_archive_only" and "disabled" not in str(
            record.get("semantic_use")
        ):
            raise ValueError(f"{source_id} private bytes must remain disabled")
        rendered.append({**record, "release_evidence_sha256": _sha256(evidence_path)})
    stable = {
        "schema_version": document["schema_version"],
        "track": document["track"],
        "as_of": document["as_of"],
        "activation": document["activation"],
        "upstream_state": document["upstream_state"],
        "records": rendered,
        "claims": claims,
    }
    digest = hashlib.sha256(
        json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {**stable, "inventory_sha256": digest}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    document = yaml.safe_load(args.inventory.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("inventory must be a mapping")
    rendered = render_inventory(document, args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rendered, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
