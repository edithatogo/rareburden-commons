from pathlib import Path

from rareburden.schema import load_mapping

ROOT = Path(__file__).parents[1]
PACKET = ROOT / "docs/track-007-community-authority-evidence-packet-2026-08-20.yml"


def test_community_authority_packet_is_pending_and_attributable() -> None:
    data = load_mapping(PACKET)
    assert data["status"] == "pending_attributable_community_evidence"
    assert data["current_state"]["attributable_receipts"] == 0
    assert data["current_state"]["agent_panel_substitute"] == "prohibited"
    assert data["current_state"]["owner_disposition_substitute"] == "prohibited"
    assert data["next_action"]["requires_external_accountable_participant"] is True


def test_community_authority_packet_requires_scope_and_withdrawal() -> None:
    data = load_mapping(PACKET)
    fields = set(data["required_receipt_fields"])
    assert {"authority_basis_or_scope", "exact_candidate_commit_and_manifest"} <= fields
    assert {"withdrawal_or_correction_route", "language_and_accessibility_support"} <= fields
    assert "unattributed_or_ambiguous_authority" in data["stop_triggers"]
    assert "consent_or_partnership_inferred_from_public_visibility" in data["stop_triggers"]
