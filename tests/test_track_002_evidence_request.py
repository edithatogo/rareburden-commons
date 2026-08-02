from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_track_002_qualifying_evidence_requests_are_explicit_and_fail_closed() -> None:
    record = yaml.safe_load(
        (ROOT / "docs/track-002-qualifying-evidence-request.yml").read_text(encoding="utf-8")
    )
    assert record["status"] == "requests_prepared_pending_receipts"
    requests = record["requests"]
    assert {item["gate"] for item in requests} == {
        "scientific",
        "data_governance",
        "landscape_challenge",
        "independent_operator",
    }
    assert all(item["status"] == "pending" for item in requests)
    assert all(item["required_fields"] for item in requests)


def test_track_002_source_packet_checklist_is_fail_closed() -> None:
    packet = yaml.safe_load(
        (ROOT / "docs/track-002-source-packet-checklist.yml").read_text(encoding="utf-8")
    )
    assert packet["status"] == "preparation_only"
    assert packet["activation"] == "disabled_until_accountable_dispositions"
    required = set(packet["packet_requirements"])
    assert {
        "exact_url_or_query",
        "sha256",
        "scientific_disposition",
        "data_governance_disposition",
        "source_change_exercise_receipt",
    } <= required
    assert packet["sources"]
    for source in packet["sources"]:
        assert source["exact_routes"]
        assert source["sha256_recorded"] is True
        assert source["scientific_disposition"] == "pending"
        assert source["data_governance_disposition"] == "pending"
        assert source["source_change_exercise"] == "pending"


def test_every_source_packet_candidate_has_pending_accountable_gates() -> None:
    packet = yaml.safe_load(
        (ROOT / "docs/track-002-source-packet-checklist.yml").read_text(encoding="utf-8")
    )
    assert {source["source_id"] for source in packet["sources"]} == {
        "orphadata-science",
        "un-world-population-prospects",
        "who-global-health-estimates",
        "world-bank-indicators-api",
    }
    for source in packet["sources"]:
        assert source["packet_status"] in {
            "candidate_exact_route_recorded",
            "candidate_query_manifest_recorded",
        }
        assert source["sha256_recorded"] is True
        assert source["scientific_disposition"] == "pending"
        assert source["data_governance_disposition"] == "pending"
        assert source["source_change_exercise"] == "pending"
