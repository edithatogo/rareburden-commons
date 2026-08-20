#!/usr/bin/env python3
"""Validate the fail-closed Option B downstream-preparation contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


class DownstreamPreparationError(ValueError):
    """Raised when bounded preparation could bypass a governance gate."""


FREEZE_ORDER = ("008", "009", "010")
EXPECTED_TRACKS = {
    "003",
    "004",
    "005",
    "008",
    "009",
    "010",
    "011",
    "012",
    "013",
    "014",
    "015",
    "016",
    "017",
}
ACTIVATED_STATES = {"active", "in_review", "complete"}
REQUIRED_PROHIBITED_CLAIMS = {
    "empirical_activation",
    "community_or_human_approval",
    "custodian_approval",
    "clinical_approval",
    "independent_review",
    "quality_completion",
    "archive_authority",
    "release_authority",
}


def _mapping(path: Path) -> dict[str, Any]:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise DownstreamPreparationError(f"cannot read preparation plan {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise DownstreamPreparationError("preparation plan must be a mapping")
    return document


def _track_metadata(root: Path, track: str) -> dict[str, Any]:
    matches = sorted((root / "conductor" / "tracks").glob(f"{track}-*/metadata.json"))
    if len(matches) != 1:
        raise DownstreamPreparationError(
            f"track {track} must resolve to exactly one metadata file; found {len(matches)}"
        )
    try:
        document = json.loads(matches[0].read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DownstreamPreparationError(f"cannot read track {track} metadata: {exc}") from exc
    if not isinstance(document, dict):
        raise DownstreamPreparationError(f"track {track} metadata must be an object")
    return document


def validate(plan_path: Path, root: Path) -> None:
    """Validate bounded scope, governance labels, and serial activation order."""
    plan = _mapping(plan_path)
    if plan.get("schema_version") != "0.2.0":
        raise DownstreamPreparationError("schema_version must be 0.2.0")
    if plan.get("mode") != "dependency_ordered_bounded_preparation":
        raise DownstreamPreparationError("mode must remain dependency ordered")
    if plan.get("activation_rule") != "synthetic_public_only_until_upstream_receipts":
        raise DownstreamPreparationError("activation rule must remain synthetic/public only")
    if tuple(plan.get("freeze_order", ())) != FREEZE_ORDER:
        raise DownstreamPreparationError("freeze_order must be 008 -> 009 -> 010")

    governance = plan.get("governance")
    if not isinstance(governance, dict):
        raise DownstreamPreparationError("governance must be a mapping")
    if governance.get("panel_status") != "advisory":
        raise DownstreamPreparationError("panel outputs must remain advisory")
    if governance.get("owner_status") != "owner_operated_not_independent_review":
        raise DownstreamPreparationError(
            "owner disposition must not be labelled independent review"
        )

    prohibited = plan.get("prohibited_claims")
    if (
        not isinstance(prohibited, list)
        or not all(isinstance(item, str) for item in prohibited)
        or not REQUIRED_PROHIBITED_CLAIMS.issubset(prohibited)
    ):
        raise DownstreamPreparationError("prohibited_claims does not preserve every blocked gate")

    security = plan.get("cross_cutting_security")
    if not isinstance(security, dict) or security.get("state") != "authorized_preparation":
        raise DownstreamPreparationError("cross-cutting security must be authorized preparation")
    if security.get("production_activation") != "blocked":
        raise DownstreamPreparationError("production security activation must remain blocked")

    decision = plan.get("owner_disposition")
    if not isinstance(decision, str) or not decision:
        raise DownstreamPreparationError("owner_disposition must name a decision record")
    decision_path = root / decision
    try:
        decision_text = decision_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise DownstreamPreparationError(
            f"cannot read owner disposition {decision_path}: {exc}"
        ) from exc
    for phrase in ("Option B", "owner-operated governance", "not independent review"):
        if phrase not in decision_text:
            raise DownstreamPreparationError(
                f"owner disposition is missing required phrase: {phrase}"
            )

    tracks = plan.get("tracks")
    if not isinstance(tracks, list):
        raise DownstreamPreparationError("tracks must be a list")
    if not all(isinstance(row, dict) and isinstance(row.get("track"), str) for row in tracks):
        raise DownstreamPreparationError("every track row must have a string track identifier")
    rows = {row["track"]: row for row in tracks}
    if len(rows) != len(tracks) or set(rows) != EXPECTED_TRACKS:
        raise DownstreamPreparationError("tracks must cover each Option B lane exactly once")
    if any(not row.get("preparation") or not row.get("blocked") for row in rows.values()):
        raise DownstreamPreparationError("every track must define preparation and blocking gates")
    for track in FREEZE_ORDER:
        row = rows.get(track)
        if not isinstance(row, dict) or row.get("contract_state") != "provisional":
            raise DownstreamPreparationError(f"track {track} contract must remain provisional")
        if not row.get("blocked"):
            raise DownstreamPreparationError(f"track {track} must retain blocking gates")

    statuses = {
        track: _track_metadata(root, track).get("status") for track in ("002", "007", *FREEZE_ORDER)
    }
    if statuses["008"] in ACTIVATED_STATES and any(
        statuses[track] != "complete" for track in ("002", "007")
    ):
        raise DownstreamPreparationError(
            "track 008 cannot activate before tracks 002 and 007 complete"
        )
    if statuses["009"] in ACTIVATED_STATES and any(
        statuses[track] != "complete" for track in ("002", "008")
    ):
        raise DownstreamPreparationError(
            "track 009 cannot activate before tracks 002 and 008 complete"
        )
    if statuses["010"] in ACTIVATED_STATES and statuses["009"] != "complete":
        raise DownstreamPreparationError("track 010 cannot activate before track 009 completes")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.plan.resolve(), args.root.resolve())
    except DownstreamPreparationError as exc:
        print(f"Downstream preparation contract failed: {exc}")
        return 1
    print("Downstream preparation contract passed; empirical and release gates remain blocked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
