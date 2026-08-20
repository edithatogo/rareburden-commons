#!/usr/bin/env python3
"""Validate Track 008 freeze readiness without granting approval or freezing contracts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


class Track008ReadinessError(ValueError):
    """Raised when the Track 008 closure contract is internally inconsistent."""


DEPENDENCIES = ("002-public-source-acquisition", "007-landscape-novelty")
REQUIRED_FINDINGS = {"SEM-MED-01", "RIGHTS-MED-01", "RIGHTS-MED-02", "NAME-MED-01"}
FALSE_CLAIMS = {
    "approved_ontology_pins",
    "naming_authority",
    "independent_semantic_review",
    "contract_frozen",
    "track_complete",
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")


def _load(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise Track008ReadinessError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track008ReadinessError(f"{path} must contain a mapping")
    return value


def _metadata(root: Path, track: str) -> dict[str, Any]:
    candidates = [
        root / "conductor" / "tracks" / track / "metadata.json",
        root / "conductor" / "archive" / track / "metadata.json",
    ]
    matches = [candidate for candidate in candidates if candidate.is_file()]
    if len(matches) != 1:
        raise Track008ReadinessError(
            f"track {track} must resolve to exactly one metadata file; found {len(matches)}"
        )
    path = matches[0]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track008ReadinessError(f"cannot read metadata {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track008ReadinessError(f"metadata {path} must be an object")
    return value


def validate(path: Path, root: Path) -> None:
    document = _load(path)
    if (
        document.get("schema_version") != "1.0.0"
        or document.get("track") != "008-semantic-backbone"
    ):
        raise Track008ReadinessError("unexpected Track 008 readiness identity")
    if document.get("candidate_contract") != "v0.4" or document.get("freeze_order_position") != 1:
        raise Track008ReadinessError("Track 008 must remain first in the v0.4 freeze order")

    track_metadata = _metadata(root, "008-semantic-backbone")
    if document.get("status") != track_metadata.get("status"):
        raise Track008ReadinessError("readiness status must match Track 008 metadata")
    dependencies = document.get("upstream_dependencies")
    if not isinstance(dependencies, list) or [row.get("track") for row in dependencies] != list(
        DEPENDENCIES
    ):
        raise Track008ReadinessError("both ordered upstream dependencies are required")
    for row in dependencies:
        observed = _metadata(root, row["track"]).get("status")
        if row.get("required_status") != "complete" or row.get("observed_status") != observed:
            raise Track008ReadinessError(f"dependency state drift for {row['track']}")
        expected_state = "satisfied" if observed in {"complete", "archived"} else "pending"
        if row.get("state") != expected_state:
            raise Track008ReadinessError(f"dependency gate state mismatch for {row['track']}")

    findings = document.get("naming_and_semantic_gate", {}).get("unresolved_findings", [])
    if {row.get("id") for row in findings if isinstance(row, dict)} != REQUIRED_FINDINGS:
        raise Track008ReadinessError("the four bounded-review findings must remain explicit")
    governance = document.get("governance", {})
    if governance.get("repository_panel_output") != "advisory":
        raise Track008ReadinessError("repository panel output must remain advisory")
    if governance.get("owner_disposition") != "owner_operated_not_independent_review":
        raise Track008ReadinessError("owner disposition cannot be independent review")

    claims = document.get("claims", {})
    if any(claims.get(name) is not False for name in FALSE_CLAIMS):
        raise Track008ReadinessError("blocked Track 008 claims must remain false")
    freeze = document.get("contract_freeze_gate", {})
    if freeze.get("state") == "satisfied":
        if not COMMIT.fullmatch(str(freeze.get("exact_candidate_commit", ""))):
            raise Track008ReadinessError("freeze requires an exact 40-character candidate commit")
        if not SHA256.fullmatch(str(freeze.get("semantic_manifest_sha256", ""))):
            raise Track008ReadinessError("freeze requires an exact semantic manifest SHA-256")
        if not freeze.get("blocking_findings_resolved") or not freeze.get(
            "accountable_freeze_decision"
        ):
            raise Track008ReadinessError(
                "freeze requires resolved findings and accountable decision"
            )
    elif freeze.get("state") != "pending":
        raise Track008ReadinessError("freeze gate state must be pending or satisfied")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("readiness", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.readiness.resolve(), args.root.resolve())
    except Track008ReadinessError as exc:
        print(f"Track 008 freeze readiness failed: {exc}")
        return 1
    print(
        "Track 008 readiness passed; approval, independent review and v0.4 freeze "
        "remain separate gates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
