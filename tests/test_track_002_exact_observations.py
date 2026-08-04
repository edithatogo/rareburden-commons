from pathlib import Path

from rareburden.schema import load_mapping


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs/track-002-exact-source-observations-2026-08-03.yml"


def test_track_002_observations_are_explicit_and_fail_closed() -> None:
    packet = load_mapping(PATH)
    assert packet["status"] == "retrieval_observation_only"
    assert packet["activation"] == "disabled_until_accountable_dispositions"
    assert len(packet["records"]) == 5
    for record in packet["records"]:
        assert record["route"].startswith("https://")
        assert (record["sha256"] is not None and len(record["sha256"]) == 64) or record["http_status"] == 0
        assert "pending" in record["terms_status"]


def test_track_002_unavailable_api_cannot_be_promoted() -> None:
    packet = load_mapping(PATH)
    api = next(item for item in packet["records"] if item["source_id"] == "world-bank-indicators-api")
    assert api["http_status"] == 0
    assert api["sha256"] is None
    assert "null or unavailable" in packet["fail_closed_rules"][0]
