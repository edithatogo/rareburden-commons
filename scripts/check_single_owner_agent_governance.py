#!/usr/bin/env python3
"""Validate prospective simulated-agent and owner-decision governance."""

from __future__ import annotations

import argparse
from pathlib import Path

from rareburden.schema import load_document, load_mapping, validate_instance


class GovernanceError(ValueError):
    """Raised when the governance contract drifts."""


REQUIRED_PRESENTATION = {
    "options",
    "trade_offs",
    "contingencies",
    "rationale",
    "recommendation",
    "uncertainty",
    "dissent",
    "stop_triggers",
}
REQUIRED_EXTERNAL = {
    "publisher_licence_or_source_terms",
    "third_party_rights",
    "registry_event",
    "credential_or_live_service_capacity",
    "third_party_controlled_data_custodian_permission",
    "patient_or_community_consent",
    "patient_or_community_representation",
    "partnership_or_endorsement",
    "institutional_or_external_approval",
}


def _strings(value: object, label: str) -> set[str]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) for item in value):
        raise GovernanceError(f"{label} must be a non-empty string list")
    if len(value) != len(set(value)):
        raise GovernanceError(f"{label} must not contain duplicates")
    return set(value)


def validate(path: Path, root: Path) -> None:
    c = load_document(path)
    if (c.get("schema_version"), c.get("application")) != (
        "1.0.0",
        "prospective_material_decisions",
    ):
        raise GovernanceError("governance contract identity drifted")
    if c.get("historical_role_metadata_rewritten") is not False:
        raise GovernanceError("historical role metadata must not be rewritten")
    owner, panel = c.get("owner", {}), c.get("agent_panel", {})
    if owner.get("identity") != "edithatogo" or owner.get("decides_after_agent_advice") is not True:
        raise GovernanceError("repository owner decision authority drifted")
    if not all(
        owner.get(field) is True
        for field in ("repository_data_custodian", "applicable_indigenous_authority")
    ):
        raise GovernanceError("owner-held custodian and applicable Indigenous authority drifted")
    if owner.get("authority_basis") != "attributable_owner_declaration":
        raise GovernanceError("owner-held authority must remain an attributable declaration")
    expected_exclusions = {
        "unrelated_indigenous_peoples_or_communities",
        "third_party_custodians",
        "publishers_or_licensors",
        "ethics_bodies",
        "governments_or_jurisdictions",
    }
    if (
        _strings(owner.get("authority_scope_excludes"), "owner authority exclusions")
        != expected_exclusions
    ):
        raise GovernanceError("owner authority scope exclusions are incomplete")
    if owner.get("additional_human_review_planned") is not False:
        raise GovernanceError("additional human review is not part of this repository model")
    if (owner.get("remuneration_model"), owner.get("remuneration_amount")) != ("unpaid", 0):
        raise GovernanceError("repository work must remain explicitly unpaid")
    if panel.get("simulation_status") != "simulated_role_separated_advisory_panel":
        raise GovernanceError("agent panel must remain explicitly simulated")
    if (
        panel.get("minimum_perspectives") != 3
        or panel.get("perspectives_are_independent_people") is not False
    ):
        raise GovernanceError(
            "material decisions require three non-independent simulated perspectives"
        )
    if (panel.get("required_options_minimum"), panel.get("required_options_maximum")) != (2, 3):
        raise GovernanceError("owner packets must contain two or three options")
    if (
        _strings(panel.get("required_presentation"), "required presentation")
        != REQUIRED_PRESENTATION
    ):
        raise GovernanceError("required advice presentation is incomplete")
    if panel.get("recommendation_is_approval") is not False:
        raise GovernanceError("an agent recommendation must not be approval")
    boundary = c.get("external_fact_boundary", {})
    if (
        _strings(boundary.get("simulation_cannot_create"), "external fact boundary")
        != REQUIRED_EXTERNAL
    ):
        raise GovernanceError("external fact boundary is incomplete")
    if boundary.get("unresolved_fact_action") != "narrow_defer_or_stop":
        raise GovernanceError("unresolved external facts must fail closed")
    claims = c.get("claims_boundary", {})
    if not claims or any(value is not False for value in claims.values()):
        raise GovernanceError("simulation and metadata non-inference claims must remain false")
    decision = c.get("decision_rule", {})
    if not all(
        decision.get(field) is True
        for field in (
            "exact_candidate_binding_required",
            "dissent_and_uncertainty_preserved",
            "owner_disposition_required",
        )
    ):
        raise GovernanceError("owner decision safeguards are incomplete")
    if decision.get("unresolved_critical_finding") != "narrow_revise_defer_or_stop":
        raise GovernanceError("critical findings must prevent unqualified acceptance")
    schema = root / panel.get("required_packet_schema", "")
    validate_instance(
        load_document(root / "docs/agent-owner-decision-packet-template.yml"),
        load_mapping(schema),
        label="agent-owner decision template",
    )


def validate_packet(path: Path, root: Path, *, require_owner_decision: bool = False) -> None:
    packet = load_document(path)
    validate_instance(
        packet,
        load_mapping(root / "schemas/agent-owner-decision-packet.schema.json"),
        label="agent-owner decision packet",
    )
    option_ids = [option["id"] for option in packet["options"]]
    if len(option_ids) != len(set(option_ids)):
        raise GovernanceError("decision option identifiers must be unique")
    if packet["recommendation"]["option_id"] not in option_ids:
        raise GovernanceError("recommendation must reference a presented option")
    decision = packet["owner_decision"]
    if require_owner_decision and decision["status"] != "recorded":
        raise GovernanceError("an attributable owner decision is required")
    if decision["status"] == "recorded" and decision["selected_option_id"] not in option_ids:
        raise GovernanceError("owner decision must reference a presented option")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--require-owner-decision", action="store_true")
    args = parser.parse_args()
    try:
        validate(args.contract.resolve(), args.root.resolve())
        if args.packet:
            validate_packet(
                args.packet.resolve(),
                args.root.resolve(),
                require_owner_decision=args.require_owner_decision,
            )
    except (GovernanceError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"Single-owner agent governance failed: {exc}")
        return 1
    print("Single-owner agent governance passed; simulated panels advise and the owner decides.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
