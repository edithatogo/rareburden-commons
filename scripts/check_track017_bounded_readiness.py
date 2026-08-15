#!/usr/bin/env python3
"""Validate Track 017's fail-closed bounded release-readiness contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


class ReleaseReadinessError(ValueError):
    """Raised when readiness evidence drifts or implies unavailable authority."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_readiness(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    if manifest.get("scope") != "single_owner_agent_panel_release_readiness":
        raise ReleaseReadinessError("readiness scope must remain single-owner and bounded")
    model = manifest.get("operating_model", {})
    if model.get("repository_owner_count") != 1:
        raise ReleaseReadinessError("exactly one accountable repository owner is required")
    if model.get("accountable_release_authority") != "repository_owner":
        raise ReleaseReadinessError("release authority must remain the repository owner")
    if model.get("agent_panels_are_advisory") is not True:
        raise ReleaseReadinessError("agent panels must remain advisory")
    required_prohibitions = {
        "independent_review",
        "human_review",
        "patient_or_community_consent",
        "custodian_or_licensor_approval",
        "external_or_institutional_approval",
    }
    if set(model.get("prohibited_agent_authority_claims", [])) != required_prohibitions:
        raise ReleaseReadinessError("all prohibited agent-authority claims must remain explicit")

    continuity = manifest.get("owner_and_continuity", {})
    if continuity.get("backup_status") != "owner_attested_private_backup_acceptance":
        raise ReleaseReadinessError("backup status must remain an exact owner attestation")
    if continuity.get("continuity_evidence_complete") is not False:
        raise ReleaseReadinessError(
            "backup continuity cannot be complete without a qualifying handoff"
        )
    if len(continuity.get("missing_backup_fields", [])) != 5:
        raise ReleaseReadinessError("all missing backup continuity fields must remain explicit")

    for binding in manifest.get("evidence_bindings", []):
        relative = Path(str(binding.get("artifact", "")))
        if relative.is_absolute() or ".." in relative.parts:
            raise ReleaseReadinessError(f"unsafe evidence path: {relative}")
        artifact = root / relative
        if not artifact.is_file() or _sha256(artifact) != binding.get("sha256"):
            raise ReleaseReadinessError(f"evidence hash mismatch: {relative}")

    dependency = manifest.get("integration_dependency", {})
    status = dependency.get("status")
    if status == "pending_merge":
        if any(dependency.get(key) is not None for key in ("artifact", "sha256", "merge_commit")):
            raise ReleaseReadinessError("pending Track 016 must not imply an exact binding")
        if manifest.get("status") != "prepared_awaiting_track_016_binding":
            raise ReleaseReadinessError("unbound Track 016 requires prepared status")
    elif status == "bound":
        relative = Path(str(dependency.get("artifact", "")))
        if not (root / relative).is_file() or _sha256(root / relative) != dependency.get("sha256"):
            raise ReleaseReadinessError("Track 016 dependency hash mismatch")
        if not dependency.get("merge_commit"):
            raise ReleaseReadinessError("bound Track 016 requires its merge commit")
        if manifest.get("status") != "bounded_readiness_contract_validated":
            raise ReleaseReadinessError("bound Track 016 requires validated status")
    else:
        raise ReleaseReadinessError("Track 016 dependency status is invalid")

    unsafe_claims = sorted(
        key for key, value in manifest.get("claims", {}).items() if value is not False
    )
    if unsafe_claims:
        raise ReleaseReadinessError(
            "release-readiness claims must remain false: " + ", ".join(unsafe_claims)
        )
    expected_track_016_gate = status == "bound"
    if (
        manifest.get("stable_release_gates", {}).get("track_016_bound")
        is not expected_track_016_gate
    ):
        raise ReleaseReadinessError("Track 016 gate must match its exact binding state")
    unsafe_gates = sorted(
        key
        for key, value in manifest.get("stable_release_gates", {}).items()
        if key != "track_016_bound" and value is not False
    )
    if unsafe_gates:
        raise ReleaseReadinessError(
            "stable release gates cannot close in preparation: " + ", ".join(unsafe_gates)
        )
    if manifest.get("usability_preparation", {}).get("required_agent_assessments") != 2:
        raise ReleaseReadinessError("two role-separated usability agent assessments are required")
    if manifest.get("reproduction_preparation", {}).get("clean_release_candidates_required") != 2:
        raise ReleaseReadinessError("two clean release candidates are required")
    if len(manifest.get("stop_triggers", [])) != 8:
        raise ReleaseReadinessError("all release stop triggers must remain explicit")
    return {
        "status": "bounded_readiness_preparation_valid",
        "track_016_status": status,
        "open_gate_count": sum(
            value is False for value in manifest["stable_release_gates"].values()
        ),
        "prohibited_claim_count": len(manifest["claims"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path())
    args = parser.parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    print(json.dumps(validate_readiness(payload, args.root.resolve()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
