"""Validate and fingerprint the bounded cross-estate terminology audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

REQUIRED_FAMILIES = {
    "who-icd",
    "who-fic-related",
    "umls",
    "hpo",
    "snomed-ct",
    "meddra",
    "orphacode",
    "orphadata",
    "panelapp",
    "mondo",
    "clinvar",
}


def render_audit(document: dict[str, Any], root: Path) -> dict[str, Any]:
    claims = document.get("claims")
    if not isinstance(claims, dict) or any(claims.values()):
        raise ValueError("all global-completeness and public-licensing claims must remain false")
    records = document.get("families")
    if not isinstance(records, list):
        raise ValueError("families must be a list")
    ids = [record.get("id") for record in records if isinstance(record, dict)]
    if set(ids) != REQUIRED_FAMILIES or len(ids) != len(REQUIRED_FAMILIES):
        raise ValueError("audit family scope is missing, duplicated or unexpected")
    rendered: list[dict[str, Any]] = []
    for record in records:
        evidence_path = (root / record["evidence"]).resolve()
        if root.resolve() not in evidence_path.parents or not evidence_path.is_file():
            raise ValueError(f"unsafe or missing evidence for {record['id']}")
        if record["public_route"] not in {
            "metadata_only",
            "metadata_only_with_submitter_caveats",
            "existing_public_archive",
            "exact_unmodified_core_assets_with_attribution",
        }:
            raise ValueError(f"unsupported public route for {record['id']}")
        if (
            record["id"] in {"umls", "snomed-ct", "meddra"}
            and record["public_route"] != "metadata_only"
        ):
            raise ValueError(f"licensed family {record['id']} must remain metadata-only")
        rendered.append(
            {
                **record,
                "evidence_sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
            }
        )
    stable = {
        "schema_version": document["schema_version"],
        "track": document["track"],
        "as_of": document["as_of"],
        "status": document["status"],
        "scope_claim": document["scope_claim"],
        "destinations": document["destinations"],
        "families": rendered,
        "routing_rules": document["routing_rules"],
        "claims": claims,
    }
    return {
        **stable,
        "audit_sha256": hashlib.sha256(
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
    result = render_audit(document, args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
