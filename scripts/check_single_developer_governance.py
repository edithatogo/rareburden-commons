#!/usr/bin/env python3
"""Validate the single-owner and advisory-agent governance contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


class GovernanceContractError(ValueError):
    """Raised when repository governance drifts from the owner decision."""


OWNER_ROLE = "Repository owner (all accountable repository roles)"
REQUIRED_ADVICE = {"options", "trade_offs", "contingencies", "rationale", "recommendation"}
REQUIRED_ROLES = {
    "repository_owner",
    "sole_developer",
    "methods_decider",
    "scientific_decider",
    "clinical_scope_decider",
    "epidemiology_decider",
    "semantic_decider",
    "data_use_decider",
    "repository_data_custodian",
    "applicable_indigenous_authority",
    "patient_community_perspective_decider",
    "equity_and_harm_decider",
    "engineering_decider",
    "security_decider",
    "operations_decider",
    "programme_decider",
    "release_decider",
}


def _load(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise GovernanceContractError(f"cannot read governance contract: {exc}") from exc
    if not isinstance(value, dict):
        raise GovernanceContractError("governance contract must contain a mapping")
    return value


def validate(path: Path, root: Path) -> None:
    contract = _load(path)
    if (contract.get("schema_version"), contract.get("operating_model")) != (
        "1.0.0",
        "single_developer_single_accountable_owner",
    ):
        raise GovernanceContractError("unexpected governance contract identity")
    owner = contract.get("owner", {})
    if owner.get("identity") != "edithatogo" or owner.get("metadata_role") != OWNER_ROLE:
        raise GovernanceContractError("repository owner identity or metadata role drifted")
    if owner.get("holds_all_accountable_repository_roles") is not True:
        raise GovernanceContractError("repository owner must hold all accountable roles")
    if set(owner.get("accountable_roles", [])) != REQUIRED_ROLES:
        raise GovernanceContractError("accountable owner role set is incomplete")
    advice = contract.get("agent_advice", {})
    if (advice.get("status"), advice.get("role_separation")) != (
        "advisory_only",
        "perspectives_not_independent_people",
    ):
        raise GovernanceContractError("agent roles must remain advisory perspectives")
    if set(advice.get("required_presentation", [])) != REQUIRED_ADVICE:
        raise GovernanceContractError("agent advice must include all five presentation fields")
    if "independent_review" not in advice.get("prohibited_claims", []):
        raise GovernanceContractError("agent advice must prohibit independence claims")
    remuneration = contract.get("remuneration", {})
    if (
        remuneration.get("model") != "none"
        or remuneration.get("amount") != 0
        or remuneration.get("promise_or_entitlement_created") is not False
    ):
        raise GovernanceContractError("remuneration must remain zero with no promise")
    groups = contract.get("decision_groups", [])
    required_group_fields = {
        "id",
        "rationale",
        "options",
        "trade_offs",
        "recommendation",
        "owner_decision",
        "contingency",
    }
    if not groups or any(not required_group_fields.issubset(group) for group in groups):
        raise GovernanceContractError(
            "decision groups must include the complete owner advice format"
        )
    authority = contract.get("owner_authority_declaration", {})
    if (
        authority.get("declared_by") != "edithatogo"
        or authority.get("repository_data_custodian") is not True
        or authority.get("applicable_indigenous_authority") is not True
    ):
        raise GovernanceContractError(
            "owner custodian and Indigenous authority declaration drifted"
        )
    required_limits = {
        "authority_for_unrelated_indigenous_peoples_or_communities",
        "authority_over_third_party_custodians",
        "publisher_or_licensor_rights",
        "jurisdictional_ethics_or_legal_approval",
    }
    if set(authority.get("does_not_claim", [])) != required_limits:
        raise GovernanceContractError("owner authority declaration scope limits drifted")
    boundary = contract.get("review_model", {})
    if (
        boundary.get("independent_human_review_planned") is not False
        or boundary.get("additional_human_reviewer_required") is not False
        or boundary.get("owner_or_agent_work_is_independent_review") is not False
        or boundary.get("independent_review_claim_permitted") is not False
    ):
        raise GovernanceContractError("independent human review must remain absent from the plan")
    metadata_paths = sorted((root / "conductor/tracks").glob("*/metadata.json"))
    metadata_paths += sorted((root / "conductor/archive").glob("*/metadata.json"))
    if not metadata_paths:
        raise GovernanceContractError("no Conductor track metadata found")
    for metadata_path in metadata_paths:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("owner_role") != OWNER_ROLE:
            raise GovernanceContractError(f"track owner role drift: {metadata_path}")
    register = (root / "conductor/tracks.md").read_text(encoding="utf-8")
    rows = [line for line in register.splitlines() if line.startswith("| ") and line[2:5].isdigit()]
    if not rows or any(f"| {OWNER_ROLE} |" not in row for row in rows):
        raise GovernanceContractError(
            "track register owner roles must identify the repository owner"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.contract.resolve(), args.root.resolve())
    except (GovernanceContractError, OSError, json.JSONDecodeError) as exc:
        print(f"Single-developer governance failed: {exc}")
        return 1
    print("Single-developer governance passed; agents advise and the repository owner decides.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
