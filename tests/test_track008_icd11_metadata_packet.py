from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/track-008-icd11-mms-2026-01-metadata-packet.yml"
INVENTORY = ROOT / "manifests/classifications/who-icd-api-inventory-2026-08-16.json"


def test_icd11_packet_binds_exact_observed_release_metadata() -> None:
    packet = yaml.safe_load(PACKET.read_text(encoding="utf-8"))
    inventory = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
    source = packet["source"]
    assert (source["product"], source["release_id"], source["language"]) == (
        "ICD-11 for Mortality and Morbidity Statistics",
        "2026-01",
        "en",
    )
    row = next(
        item
        for item in inventory["observations"]
        if item["endpoint"] == source["canonical_endpoint_path"]
        and item["language"] == source["language"]
    )
    binding = packet["observation_binding"]
    assert row["http_status"] == binding["http_status"] == 200
    assert row["bytes"] == binding["response_size_bytes"] == 2056
    assert row["sha256"] == binding["response_sha256"]
    assert row["raw_route"] == binding["response_visibility"]
    release = next(
        item
        for item in inventory["classifications"]
        if item["classification"] == "icd11-mms" and item["release_id"] == source["release_id"]
    )
    assert source["release_date"] == release["release_date"]
    assert source["language"] in release["available_languages"]
    assert source["language"] not in release["prerelease_languages"]


def test_icd11_packet_cannot_be_interpreted_as_content_or_activation() -> None:
    packet = yaml.safe_load(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "exact_metadata_observation_candidate_only"
    assert packet["observation_binding"]["public_packet_contains_response_bytes"] is False
    assert packet["rights_and_access"]["current_credential_use"] is False
    assert packet["rights_and_access"]["access_authorized_by_packet"] is False
    assert packet["rights_and_access"]["acquisition_authorized_by_packet"] is False
    assert packet["rights_and_access"]["retention_authorized_by_packet"] is False
    assert packet["rights_and_access"]["public_raw_redistribution"] is False
    assert packet["rights_and_access"]["activation_state"].startswith("disabled")
    assert packet["claims"] == {
        "exact_release_metadata_observed": True,
        "classification_content_public": False,
        "mapping_validated": False,
        "scientific_fitness_established": False,
        "production_activation": False,
        "redistribution_authorized": False,
        "independent_review": False,
        "external_validation": False,
        "community_participation": False,
    }
