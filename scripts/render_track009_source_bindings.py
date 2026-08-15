"""Render immutable Track 009 source bindings from bounded evidence receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_bindings(document: dict[str, Any], root: Path) -> dict[str, Any]:
    if document.get("contract_freeze") is not False or any(document["claims"].values()):
        raise ValueError("Track 009 activation and freeze claims must remain false")
    upstream_path = root / document["upstream_track_008_manifest"]
    upstream = json.loads(upstream_path.read_text(encoding="utf-8"))
    if upstream.get("inventory_sha256") != document.get("upstream_inventory_sha256"):
        raise ValueError("Track 008 inventory fingerprint mismatch")
    upstream_ids = {record["source_id"] for record in upstream["records"]}
    records = [*document["source_releases"], document["synthetic_release"]]
    seen: set[str] = set()
    rendered: list[dict[str, Any]] = []
    for record in records:
        release_id = record["source_release_id"]
        if release_id in seen:
            raise ValueError("duplicate source_release_id")
        seen.add(release_id)
        evidence = record["evidence"]
        if evidence == "track_008":
            if release_id not in upstream_ids:
                raise ValueError(f"{release_id} is absent from Track 008 provenance")
            evidence_path = upstream_path
        else:
            evidence_path = root / evidence
        if not evidence_path.is_file():
            raise ValueError(f"missing evidence for {release_id}")
        if record["visibility"] == "private" and not record["activation_state"].startswith(
            "disabled_"
        ):
            raise ValueError(f"private source {release_id} must remain disabled")
        if record["licence_state"] not in {"permitted", "not_applicable"} and not record[
            "activation_state"
        ].startswith("disabled_"):
            raise ValueError(f"unusable source {release_id} must remain disabled")
        rendered.append(
            {
                **record,
                "provenance_manifest_sha256": _sha(evidence_path),
            }
        )
    stable = {
        "schema_version": document["schema_version"],
        "track": document["track"],
        "upstream_inventory_sha256": document["upstream_inventory_sha256"],
        "source_releases": rendered,
        "claims": document["claims"],
    }
    return {
        **stable,
        "binding_set_sha256": hashlib.sha256(
            json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    document = yaml.safe_load(args.source.read_text(encoding="utf-8"))
    rendered = render_bindings(document, args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rendered, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
