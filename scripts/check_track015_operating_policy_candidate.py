#!/usr/bin/env python3
"""Validate the bounded Track 015 operating-policy candidate."""

from __future__ import annotations

import argparse
from pathlib import Path

from rareburden.schema import load_document


class OperatingPolicyError(ValueError):
    """Raised when the operating-policy candidate weakens a required boundary."""


def validate(path: Path) -> dict[str, object]:
    policy = load_document(path)
    if (policy.get("schema_version"), policy.get("track")) != (
        "1.0.0",
        "015-governance-partnership-policy",
    ):
        raise OperatingPolicyError("policy identity drifted")
    if policy.get("status") != "candidate_pending_owner_disposition":
        raise OperatingPolicyError("candidate must remain pending owner disposition")
    if policy.get("decision_authority") != "repository_owner":
        raise OperatingPolicyError("only the repository owner may decide")
    if policy.get("human_review_required") is not False:
        raise OperatingPolicyError("additional human review is not a repository gate")
    if policy.get("remuneration") != {"model": "unpaid", "amount": 0}:
        raise OperatingPolicyError("repository work must remain unpaid")

    scope = policy.get("scope", {})
    if scope.get("controlled_or_third_party_inputs") != (
        "disabled_without_scope_matched_permission"
    ):
        raise OperatingPolicyError("controlled and third-party inputs must fail closed")
    if scope.get("authority_for_unrelated_communities_or_nodes") != "not_claimed":
        raise OperatingPolicyError("unrelated community or node authority cannot be claimed")

    prohibited = set(policy.get("acceptable_use", {}).get("prohibited", []))
    if len(prohibited) != 4 or not any("re-identification" in item for item in prohibited):
        raise OperatingPolicyError("acceptable-use prohibitions are incomplete")
    if policy.get("funder_independence", {}).get("funder_veto") != "prohibited":
        raise OperatingPolicyError("funder veto must remain prohibited")
    if policy.get("complaints_and_appeals", {}).get("independence_claim") is not False:
        raise OperatingPolicyError("owner appeals cannot be described as independent")

    care = policy.get("indigenous_data_and_care", {})
    if care.get("owner_applicable_authority") != "declared":
        raise OperatingPolicyError("owner applicable-authority declaration drifted")
    if care.get("unrelated_people_or_country_node_rule") != (
        "require_attributable_scope_matched_authority_before_activation"
    ):
        raise OperatingPolicyError("unrelated authority must remain evidence-bound")

    node = policy.get("country_node", {})
    if (
        node.get("default_state") != "inactive"
        or len(node.get("required_before_activation", [])) != 5
    ):
        raise OperatingPolicyError("country-node activation must remain fail closed")
    return {
        "status": "bounded_operating_policy_candidate_valid",
        "prohibited_use_count": len(prohibited),
        "country_node_activation_requirement_count": 5,
        "owner_disposition_pending": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("policy", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.policy.resolve())
    except (OperatingPolicyError, OSError, TypeError, ValueError) as exc:
        print(f"Track 015 operating-policy candidate failed: {exc}")
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
