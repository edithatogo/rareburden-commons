#!/usr/bin/env python3
"""Validate the exact bounded Track 015 owner operating-policy disposition."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from rareburden.schema import load_document


class OwnerPolicyDispositionError(ValueError):
    """Raised when the Track 015 owner disposition overclaims or drifts."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path: Path, root: Path) -> dict[str, object]:
    receipt = load_document(path)
    if (receipt.get("schema_version"), receipt.get("track"), receipt.get("status")) != (
        "1.0.0",
        "015-governance-partnership-policy",
        "accepted_bounded_repository_policy",
    ):
        raise OwnerPolicyDispositionError("owner disposition identity drifted")
    decision = receipt.get("decision", {})
    if decision.get("selected_option") != "A" or decision.get("disposition") != "accept":
        raise OwnerPolicyDispositionError("recommended Option A must be selected")
    if decision.get("governance_status") != "owner_operated_not_independent_review":
        raise OwnerPolicyDispositionError("owner decision cannot be independent review")

    candidate = receipt.get("exact_candidate", {})
    for key, hash_key in (
        ("operating_policy_path", "operating_policy_sha256"),
        ("tabletop_path", "tabletop_sha256"),
        ("options_path", "options_sha256"),
    ):
        relative = Path(str(candidate.get(key, "")))
        if relative.is_absolute() or ".." in relative.parts:
            raise OwnerPolicyDispositionError("candidate path is unsafe")
        evidence = root / relative
        if not evidence.is_file() or _sha256(evidence) != candidate.get(hash_key):
            raise OwnerPolicyDispositionError("exact candidate evidence hash mismatch")

    boundaries = receipt.get("retained_boundaries", {})
    false_boundaries = {
        "independent_or_additional_human_review",
        "country_node_activation",
        "controlled_data_activation",
        "public_or_stable_release_authority",
        "global_representativeness",
    }
    if any(boundaries.get(key) is not False for key in false_boundaries):
        raise OwnerPolicyDispositionError("inactive or prohibited boundary was activated")
    if boundaries.get("third_party_permission") != "not_claimed":
        raise OwnerPolicyDispositionError("third-party permission cannot be inferred")
    if receipt.get("tabletop_disposition", {}).get("external_activation") is not False:
        raise OwnerPolicyDispositionError("tabletop cannot activate an external path")
    if len(receipt.get("stop_triggers", [])) != 5:
        raise OwnerPolicyDispositionError("stop triggers are incomplete")
    if receipt.get("invalidation", {}).get("material_change_requires_new_disposition") is not True:
        raise OwnerPolicyDispositionError("material change must require a new disposition")
    return {
        "status": "bounded_owner_operating_policy_disposition_valid",
        "selected_option": "A",
        "adopted_scope_count": len(receipt.get("adopted_scope", [])),
        "external_activation": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("decision", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        result = validate(args.decision.resolve(), args.root.resolve())
    except (OwnerPolicyDispositionError, OSError, TypeError, ValueError) as exc:
        print(f"Track 015 owner disposition failed: {exc}")
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
