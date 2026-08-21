from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/track-005-ghed-selection-readiness-2026-08-21.yml"
CATALOG = ROOT / "catalog/data_sources.yml"


def test_ghed_packet_keeps_exact_artifact_unselected() -> None:
    packet = yaml.safe_load(PACKET.read_text(encoding="utf-8"))
    source = packet["source_family"]
    assert packet["status"] == "selection_prepared_exact_release_unselected"
    assert source["source_id"] == "who-global-health-expenditure-database"
    for field in ("exact_release", "exact_file", "artifact_sha256", "indicator"):
        assert source[field] is None
    assert len(packet["selection_dimensions"]["estimand_alignment"]) >= 6
    assert len(packet["minimum_quality_evidence"]["uncertainty_and_interpretation"]) >= 4


def test_ghed_packet_is_fail_closed_and_does_not_activate_catalogue() -> None:
    packet = yaml.safe_load(PACKET.read_text(encoding="utf-8"))
    controls = packet["rights_and_operations"]
    false_controls = {
        "access_authorized_by_packet",
        "acquisition_authorized_by_packet",
        "retention_authorized_by_packet",
        "empirical_use_authorized_by_packet",
        "production_activation",
        "public_raw_redistribution",
        "credentials_requested_or_used",
        "bytes_retrieved_or_retained",
        "catalogue_status_changed",
        "owner_or_agent_can_create_publisher_permission",
    }
    assert all(controls[field] is False for field in false_controls)
    records = {
        source["source_id"]: source
        for source in yaml.safe_load(CATALOG.read_text(encoding="utf-8"))["sources"]
    }
    assert records["who-global-health-expenditure-database"]["status"] == "blocked"
    assert packet["claims"] == {
        "source_family_indexed": True,
        "exact_release_selected": False,
        "raw_data_archived": False,
        "scientific_fitness_established": False,
        "empirical_validation": False,
        "redistribution_authorized": False,
        "independent_review": False,
        "external_approval": False,
        "community_participation": False,
    }
