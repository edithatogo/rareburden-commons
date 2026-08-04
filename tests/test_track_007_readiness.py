from pathlib import Path

from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/track-007-registration-challenge-readiness-2026-08-04.yml"


def test_track_007_readiness_packet_is_fail_closed() -> None:
    packet = load_mapping(PACKET)
    assert packet["status"] == "repository_owned_readiness_pending_external_receipts"
    assert packet["submission_readiness"]["status"] == "blocked_missing_authenticated_route"
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
