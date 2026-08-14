from pathlib import Path

from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/track-007-registration-challenge-readiness-2026-08-04.yml"
REFRESHED_PACKET = ROOT / "docs/track-007-registration-challenge-readiness-2026-08-15.yml"


def test_track_007_readiness_packet_is_fail_closed() -> None:
    packet = load_mapping(PACKET)
    assert packet["status"] == "repository_owned_readiness_pending_external_receipts"
    assert packet["submission_readiness"]["status"] == "deferred_by_owner"
    assert packet["protocol"]["frozen_protocol_hash"].startswith("sha256:")
    assert packet["protocol"]["search_strategy_hash"].startswith("sha256:")
    assert packet["methods_challenge"]["status"].endswith("independent_receipt")
    assert packet["patient_community_interpretation"]["status"].endswith("accountable_receipt")


def test_track_007_readiness_disables_unqualified_claims() -> None:
    claims = set(load_mapping(PACKET)["claim_boundary"]["disabled_until_receipts"])
    assert {
        "comprehensive landscape",
        "global completeness",
        "independent novelty confirmation",
    } <= claims


def test_refreshed_track_007_packet_binds_evidence_and_keeps_receipts_pending() -> None:
    packet = load_mapping(REFRESHED_PACKET)
    assert packet["protocol"]["version"] == "0.2.0"
    for field in ("source_packet_sha256", "search_log_sha256", "screening_register_sha256"):
        assert packet["protocol"][field].startswith("sha256:")
    assert packet["registration"]["status"] == "pending_external_registration"
    assert packet["registration"]["osf"] == "deferred_by_owner"
    assert packet["methods_challenge"]["status"].endswith("independent_receipt")
    assert packet["patient_community_interpretation"]["status"].endswith("accountable_receipt")
    disabled = set(packet["claim_boundary"]["disabled_until_qualifying_receipts"])
    assert "completed systematic or scoping review" in disabled
    assert "independently confirmed novelty" in disabled
