#!/usr/bin/env python3
"""Validate Track 015's bounded single-owner governance reconciliation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


class GovernanceReconciliationError(ValueError):
    """Raised when governance evidence is incomplete or overclaimed."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_governance(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    if manifest.get("scope") != "single_owner_agent_panel_repository_governance":
        raise GovernanceReconciliationError("governance scope must remain single-owner and bounded")
    model = manifest.get("operating_model", {})
    if model.get("repository_owner_count") != 1:
        raise GovernanceReconciliationError("repository must retain one accountable owner")
    if model.get("accountable_release_authority") != "repository_owner":
        raise GovernanceReconciliationError("release authority must remain the repository owner")
    if model.get("agent_panels_are_advisory") is not True:
        raise GovernanceReconciliationError("agent panels must remain advisory")
    required_authorities = {
        "independent_review",
        "human_review",
        "patient_or_community_consent",
        "custodian_or_licensor_approval",
        "institutional_or_partner_endorsement",
    }
    if set(model.get("prohibited_agent_authority_claims", [])) != required_authorities:
        raise GovernanceReconciliationError(
            "all prohibited agent-authority claims must remain explicit"
        )
    for binding in manifest.get("evidence_bindings", []):
        relative = Path(str(binding.get("artifact", "")))
        if relative.is_absolute() or ".." in relative.parts:
            raise GovernanceReconciliationError(f"unsafe evidence path: {relative}")
        path = root / relative
        if not path.is_file() or _sha256(path) != binding.get("sha256"):
            raise GovernanceReconciliationError(f"evidence hash mismatch: {relative}")
    dependency = manifest.get("integration_dependency", {})
    dependency_status = dependency.get("status")
    if dependency_status == "bound":
        if manifest.get("status") != "bounded_repository_controls_validated":
            raise GovernanceReconciliationError("bound Track 014 requires validated status")
        relative = Path(str(dependency.get("artifact", "")))
        if not (root / relative).is_file() or _sha256(root / relative) != dependency.get("sha256"):
            raise GovernanceReconciliationError("Track 014 dependency hash mismatch")
    elif dependency_status != "pending_merge" or dependency.get("sha256") is not None:
        raise GovernanceReconciliationError(
            "unbound Track 014 dependency must remain pending without a hash"
        )
    for relationship in manifest.get("relationship_register", []):
        state = relationship.get("state")
        if state not in {"proposed", "public_source_only"}:
            raise GovernanceReconciliationError(
                "relationship cannot be confirmed without exact evidence"
            )
        if state == "proposed" and relationship.get("evidence") is not None:
            raise GovernanceReconciliationError(
                "proposed relationship cannot imply agreement evidence"
            )
    unsafe = sorted(key for key, value in manifest.get("claims", {}).items() if value is not False)
    if unsafe:
        raise GovernanceReconciliationError(
            "governance claims must remain false: " + ", ".join(unsafe)
        )
    required_triggers = {
        "source rights or terms change",
        "publisher or rights-holder withdrawal notice",
        "third-party material is discovered",
        "candidate hash or provenance mismatch",
        "critical safety or semantic-integrity finding",
        "security disclosure or credential exposure",
        "reproducibility or recovery failure",
        "relationship or endorsement claim lacks evidence",
        "scope materially exceeds recorded coverage or representativeness",
    }
    if set(manifest.get("correction_withdrawal_triggers", [])) != required_triggers:
        raise GovernanceReconciliationError("all correction and withdrawal triggers are required")
    if not manifest.get("pending_track_acceptance"):
        raise GovernanceReconciliationError("constituted Track 015 acceptance must remain pending")
    return {
        "status": "bounded_governance_valid",
        "owner_count": 1,
        "relationship_count": len(manifest["relationship_register"]),
        "pending_acceptance_count": len(manifest["pending_track_acceptance"]),
        "track_014_status": dependency_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path())
    args = parser.parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    print(json.dumps(validate_governance(payload, args.root.resolve()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
