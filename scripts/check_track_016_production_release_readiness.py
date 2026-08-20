#!/usr/bin/env python3
"""Validate Track 016 readiness while keeping accountable gates fail closed."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


class Track016ReadinessError(ValueError):
    """Raised when the Track 016 readiness contract is inconsistent."""


COMMIT = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FALSE_CLAIMS = {
    "backup_owner_handoff_complete",
    "production_operations_enabled",
    "independent_operator_review_complete",
    "independent_security_review_complete",
    "release_authorized",
    "stable_release",
    "track_complete",
}
HISTORICAL_EVIDENCE = {
    "manifests/operations/track-016-bounded-operations-2026-08-16.json": (
        "23d3e3c57ad318849753870e7796813a48c227c64943d5d3fa457c8f3eaa575e"
    ),
    "docs/track-016-owner-operated-exercise-receipt-2026-08-16.json": (
        "b31435c60e2e3986eb1befaf33d2682fe9747e09ee416e423f7e62f754b95c58"
    ),
    "docs/release-policy.md": "2f4626b33d7402a33e0a56238ee5484618ca21699f320e42193dac761eb7bcb1",
    "docs/security-operations-016-reference.md": (
        "a81d98aabda3577de26c85cfd1e776d4380501c98846d4ea8791219d977f5b5b"
    ),
}


def _load(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise Track016ReadinessError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track016ReadinessError("readiness document must contain a mapping")
    return value


def _require_candidate(commit: Any, tree: Any, label: str) -> None:
    if not COMMIT.fullmatch(str(commit or "")) or not COMMIT.fullmatch(str(tree or "")):
        raise Track016ReadinessError(f"{label} requires exact commit and tree hashes")


def _receipt_gate(gate: dict[str, Any], label: str, *, independent: bool = False) -> None:
    state = gate.get("state")
    if state not in {"pending", "satisfied"}:
        raise Track016ReadinessError(f"{label} state must be pending or satisfied")
    if state == "satisfied":
        if not gate.get("receipt_locator"):
            raise Track016ReadinessError(f"{label} requires a receipt locator")
        _require_candidate(
            gate.get("exact_candidate_commit"), gate.get("exact_candidate_tree"), label
        )
        if independent and gate.get("reviewer_independent_of_owner_and_panel") is not True:
            raise Track016ReadinessError(f"{label} requires reviewer independence")


def validate(path: Path, root: Path) -> None:
    document = _load(path)
    if (
        document.get("schema_version") != "1.0.0"
        or document.get("track") != "016-security-reliability-operations"
    ):
        raise Track016ReadinessError("unexpected Track 016 readiness identity")
    metadata = json.loads(
        (root / "conductor/tracks/016-security-reliability-operations/metadata.json").read_text(
            encoding="utf-8"
        )
    )
    if document.get("status") != metadata.get("status"):
        raise Track016ReadinessError("readiness status must match Track 016 metadata")

    governance = document.get("governance", {})
    if governance.get("repository_panel_output") != "advisory":
        raise Track016ReadinessError("panel output must remain advisory")
    if governance.get("owner_disposition") != "owner_operated_not_independent_review":
        raise Track016ReadinessError("owner disposition cannot be independent review")
    if (
        governance.get("production_operations") != "disabled"
        or governance.get("release_runtime") != "python3.13"
    ):
        raise Track016ReadinessError(
            "production must remain disabled on the Python 3.13 release runtime"
        )

    candidate = document.get("candidate_input", {})
    _require_candidate(candidate.get("commit"), candidate.get("tree"), "candidate input")
    if candidate.get("exact_release_candidate") is not False:
        raise Track016ReadinessError(
            "preparation input cannot be promoted to an exact release candidate"
        )
    for evidence in candidate.get("evidence", []):
        evidence_name = str(evidence.get("path", ""))
        evidence_path = root / evidence_name
        expected = str(evidence.get("sha256", ""))
        source_commit = evidence.get("source_commit")
        if not SHA256.fullmatch(expected) or not evidence_path.is_file():
            raise Track016ReadinessError(
                "candidate evidence requires an existing SHA-256-bound file"
            )
        if HISTORICAL_EVIDENCE.get(evidence_name) != expected:
            raise Track016ReadinessError(f"candidate evidence hash drift: {evidence_path}")
        if source_commit is not None:
            if not COMMIT.fullmatch(str(source_commit)):
                raise Track016ReadinessError("candidate evidence source commit is invalid")
            try:
                evidence_bytes = subprocess.run(
                    ["git", "show", f"{source_commit}:{evidence['path']}"],
                    cwd=root,
                    check=True,
                    capture_output=True,
                ).stdout
            except subprocess.CalledProcessError as exc:
                shallow = subprocess.run(
                    ["git", "rev-parse", "--is-shallow-repository"],
                    cwd=root,
                    check=False,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                disposition_commit = document.get("exact_candidate_owner_disposition", {}).get(
                    "exact_candidate_commit"
                )
                if not (
                    shallow == "true"
                    and candidate.get("shallow_checkout_policy")
                    == "allow_unavailable_exact_history_without_upgrading_claims"
                    and source_commit == disposition_commit
                ):
                    raise Track016ReadinessError(
                        "candidate evidence source commit is unavailable"
                    ) from exc
                continue
        else:
            evidence_bytes = evidence_path.read_bytes()
        observed = hashlib.sha256(evidence_bytes).hexdigest()
        if observed != expected:
            raise Track016ReadinessError(f"candidate evidence hash drift: {evidence_path}")

    backup = document.get("backup_owner_handoff", {})
    if backup.get("state") not in {"pending", "satisfied"}:
        raise Track016ReadinessError("backup handoff state must be pending or satisfied")
    if (
        backup.get("primary_owner") != "edithatogo"
        or backup.get("backup_identity") != "privacy_preserving_private_role"
    ):
        raise Track016ReadinessError(
            "bounded primary and privacy-preserving backup roles must remain explicit"
        )
    if backup.get("state") == "satisfied":
        receipt = backup.get("required_receipt", {})
        required = ("locator", "scope", "escalation_path", "expires_at", "revocation_method")
        if (
            any(not receipt.get(field) for field in required)
            or receipt.get("handoff_exercise_passed") is not True
        ):
            raise Track016ReadinessError(
                "backup handoff requires scoped, expiring exercised receipt"
            )
        _require_candidate(
            receipt.get("candidate_commit"), receipt.get("candidate_tree"), "backup handoff"
        )
        try:
            expiry = datetime.fromisoformat(str(receipt["expires_at"]).replace("Z", "+00:00"))
        except ValueError as exc:
            raise Track016ReadinessError("backup handoff expiry must be ISO-8601") from exc
        if expiry <= datetime.now(UTC):
            raise Track016ReadinessError("backup handoff receipt is expired")

    operations = document.get("production_operations_gate", {})
    if operations.get("state") not in {"pending", "satisfied"}:
        raise Track016ReadinessError("production operations state must be pending or satisfied")
    if operations.get("state") == "satisfied":
        controls = operations.get("required_controls", {})
        if any(
            value
            in {
                None,
                "synthetic_only",
                "prepared_not_activated",
                "prepared_not_exercised_in_production",
                "owner_operated_synthetic_only",
                "synthetic_public_scope_only",
            }
            for value in controls.values()
        ):
            raise Track016ReadinessError(
                "production operations require qualifying control receipts"
            )

    reviews = document.get("qualifying_reviews", {})
    _receipt_gate(reviews.get("independent_operator", {}), "independent operator", independent=True)
    _receipt_gate(reviews.get("independent_security", {}), "independent security", independent=True)
    _receipt_gate(document.get("exact_candidate_owner_disposition", {}), "owner disposition")
    owner_disposition = document.get("exact_candidate_owner_disposition", {})
    if owner_disposition.get("authority_model") != "owner_operated_not_independent_review":
        raise Track016ReadinessError("owner disposition authority must remain owner-operated")
    disposed = owner_disposition.get("state") == "satisfied"
    if document.get("claims", {}).get("exact_candidate_owner_disposed") is not disposed:
        raise Track016ReadinessError("owner disposition claim must match its receipt gate")
    if disposed:
        receipt_path = root / str(owner_disposition.get("receipt_locator", ""))
        if not receipt_path.is_file():
            raise Track016ReadinessError("owner disposition receipt must exist")
        try:
            expiry = datetime.fromisoformat(
                str(owner_disposition.get("expires_at", "")).replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise Track016ReadinessError("owner disposition expiry must be ISO-8601") from exc
        if expiry <= datetime.now(UTC):
            raise Track016ReadinessError("owner disposition is expired")
    _receipt_gate(document.get("release_authority", {}), "release authority")

    claims = document.get("claims", {})
    if any(claims.get(name) is not False for name in FALSE_CLAIMS):
        raise Track016ReadinessError("blocked Track 016 claims must remain false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("readiness", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.readiness.resolve(), args.root.resolve())
    except (Track016ReadinessError, OSError, json.JSONDecodeError) as exc:
        print(f"Track 016 production/release readiness failed: {exc}")
        return 1
    print(
        "Track 016 preparation passed; handoff, production, independent review "
        "and release remain gated."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
