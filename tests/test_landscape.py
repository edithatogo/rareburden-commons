from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from rareburden.landscape import (
    LandscapeValidationError,
    render_landscape_markdown,
    validate_landscape,
)
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
LANDSCAPE = load_mapping(ROOT / "catalog" / "initiatives.yml")
SCHEMA = load_mapping(ROOT / "schemas" / "initiative-landscape.schema.json")
SCREENING_EXERCISE = load_mapping(
    ROOT / "docs" / "track-007-panel-screening-exercise-2026-08-02.yml"
)
SEARCH_LOG = load_mapping(ROOT / "docs" / "track-007-search-log-2026-08-01.yml")
SEARCH_LOG_REFRESH = load_mapping(ROOT / "docs" / "track-007-search-log-2026-08-14.yml")
SEARCH_RESULTS_REFRESH = ROOT / "docs" / "track-007-search-results-2026-08-15.json"
SCREENING_REFRESH = ROOT / "docs" / "track-007-screening-2026-08-15.json"
SCREENING_RESOLUTIONS = ROOT / "docs" / "track-007-screening-resolutions-2026-08-15.json"
REGISTRATION_PACKET = ROOT / "docs" / "track-007-registration-packet.md"


def test_seed_landscape_is_valid() -> None:
    summary = validate_landscape(LANDSCAPE, SCHEMA)
    assert summary.initiative_count == 13
    assert summary.review_status == "internal_review"
    assert summary.decision_outcome == "proceed_with_narrowed_scope"
    assert summary.external_review_status == "planned"
    assert summary.status_counts["active"] >= 8
    assert summary.relationship_counts["foundational_dependency"] >= 3
    assert summary.overlap_dimension_counts["policy"] >= 3


def test_duplicate_initiative_id_is_rejected() -> None:
    value = copy.deepcopy(LANDSCAPE)
    value["initiatives"][1]["initiative_id"] = value["initiatives"][0]["initiative_id"]
    with pytest.raises(LandscapeValidationError, match="Duplicate initiative_id"):
        validate_landscape(value, SCHEMA)


def test_non_https_reference_is_rejected() -> None:
    value = copy.deepcopy(LANDSCAPE)
    value["initiatives"][0]["evidence_references"] = ["http://example.org/evidence"]
    with pytest.raises(LandscapeValidationError, match="evidence_references"):
        validate_landscape(value, SCHEMA)


def test_federated_patient_data_requires_compatible_access() -> None:
    value = copy.deepcopy(LANDSCAPE)
    initiative = next(
        item for item in value["initiatives"] if item["initiative_id"] == "erdera-virtual-platform"
    )
    initiative["data_access"] = "open"
    with pytest.raises(LandscapeValidationError, match="federated participant-data initiatives"):
        validate_landscape(value, SCHEMA)


def test_unreviewed_unqualified_proceed_is_rejected() -> None:
    value = copy.deepcopy(LANDSCAPE)
    value["decision"]["outcome"] = "proceed"
    value["decision"]["external_review_status"] = "planned"
    with pytest.raises(LandscapeValidationError, match="external_review_status is complete"):
        validate_landscape(value, SCHEMA)


def test_non_data_policy_record_cannot_claim_patient_records() -> None:
    value = copy.deepcopy(LANDSCAPE)
    value["initiatives"][0]["patient_level_data"] = True
    with pytest.raises(LandscapeValidationError, match="patient_level_data"):
        validate_landscape(value, SCHEMA)


def test_landscape_markdown_is_deterministic_and_complete() -> None:
    first = render_landscape_markdown(LANDSCAPE)
    second = render_landscape_markdown(copy.deepcopy(LANDSCAPE))
    assert first == second
    assert "# Rare-disease initiative landscape" in first
    assert "WHO rare-disease global action plan mandate" in first
    assert "proceed_with_narrowed_scope" in first
    assert first.endswith("\n")


def test_landscape_rendering_keeps_claims_provisional() -> None:
    rendered = render_landscape_markdown(LANDSCAPE).lower()
    assert "external review" in rendered
    assert "preliminary novelty decision" in rendered
    assert "not a completed systematic or scoping review" in rendered
    assert "novelty remains provisional" in rendered
    assert "partnership" not in rendered.split("## preliminary novelty decision", 1)[0]


def test_track_007_synthetic_screening_reconciles_without_closing_external_gates() -> None:
    counts = SCREENING_EXERCISE["counts"]
    assert counts["screened"] == counts["included"] + counts["excluded"] + counts["uncertain"]
    assert SCREENING_EXERCISE["expected"]["uncertain_is_not_included"] is True
    assert SCREENING_EXERCISE["expected"]["external_registration_required"] is True
    assert SCREENING_EXERCISE["expected"]["independent_challenge_required"] is True


def test_track_007_search_log_preserves_bounded_discovery_and_provisional_status() -> None:
    assert SEARCH_LOG["protocol_version"] == "RBC-LAND-007-v0.1.0"
    assert SEARCH_LOG["status"] == "discovery_only"
    assert SEARCH_LOG["records"]
    for record in SEARCH_LOG["records"]:
        assert record["endpoint"].startswith("https://")
        assert record["http_status"] in {200, "not_applicable"}
        assert record["raw_export"] in {"not_retained", "retained_lawfully"}
        assert record["screening_status"] in {
            "unscreened",
            "exact_title_only",
            "screened",
        }
    assert any(
        "not a complete public search" in limitation for limitation in SEARCH_LOG["limitations"]
    )


def test_track_007_registration_packet_is_versioned_and_fail_closed() -> None:
    packet = REGISTRATION_PACKET.read_text(encoding="utf-8")
    assert "RBC-LAND-007 v0.1.0" in packet
    assert "versioned draft; not externally registered" in packet
    for field in ("query_string", "endpoint_or_database", "export_sha256", "exclusion_reason"):
        assert field in packet
    assert "Methods reviewer" in packet
    assert "patient/community reviewer" in packet.lower()
    assert "Track 007 stays in review" in packet


def test_track_007_search_refresh_covers_registered_queries_and_stays_unscreened() -> None:
    assert SEARCH_LOG_REFRESH["protocol_version"] == "RBC-LAND-007-v0.2.0"
    assert SEARCH_LOG_REFRESH["status"] == "discovery_only"
    assert len(SEARCH_LOG_REFRESH["method"]["query_strings"]) == 5
    assert set(SEARCH_LOG_REFRESH["method"]["active_sources"]) == {
        "github",
        "zenodo",
        "huggingface_datasets",
        "crossref",
    }
    assert SEARCH_LOG_REFRESH["method"]["excluded_active_sources"]["osf"].startswith(
        "deferred_by_owner"
    )
    assert SEARCH_LOG_REFRESH["screening"]["status"] == "unscreened"
    for observation in SEARCH_LOG_REFRESH["observations"]:
        assert len(observation["totals_by_query"]) == 5
        assert len(observation["response_sha256_by_query"]) == 5
        assert all(value.startswith("sha256:") for value in observation["response_sha256_by_query"])
    assert any("No completeness" in item for item in SEARCH_LOG_REFRESH["limitations"])


def test_track_007_bounded_first_page_screen_is_complete_and_reconciled() -> None:
    snapshot_bytes = SEARCH_RESULTS_REFRESH.read_bytes()
    snapshot = json.loads(snapshot_bytes)
    screening = json.loads(SCREENING_REFRESH.read_text(encoding="utf-8"))
    assert snapshot["protocol_version"] == "RBC-LAND-007-v0.2.0"
    assert len(snapshot["records"]) == 20
    assert all(
        record["first_page_items"] == len(record["first_page_records"])
        for record in snapshot["records"]
    )
    counts = screening["counts"]
    assert counts["discovered_occurrences"] == sum(
        record["first_page_items"] for record in snapshot["records"]
    )
    assert counts["screened"] == counts["included"] + counts["excluded"] + counts["uncertain"]
    assert counts["unique_after_exact_identifier_deduplication"] == counts["screened"]
    assert counts["exact_duplicate_occurrences_removed"] == (
        counts["discovered_occurrences"] - counts["screened"]
    )
    assert (
        screening["source_snapshot_sha256"]
        == "sha256:" + hashlib.sha256(snapshot_bytes).hexdigest()
    )
    assert screening["counts"]["uncertain"] == 0
    assert screening["resolution_version"] == "RBC-LAND-007-RESOLVE-v0.2.1"
    resolution = json.loads(SCREENING_RESOLUTIONS.read_text(encoding="utf-8"))
    assert resolution["scope"] == "bounded_first_page_uncertain_record_resolution"
    assert resolution["resolutions"][0]["evidence"]["observed_type"] == "grant"


def test_track_007_screening_is_fail_closed_and_does_not_overmerge_titles() -> None:
    screening = json.loads(SCREENING_REFRESH.read_text(encoding="utf-8"))
    self_result = next(
        item
        for item in screening["decisions"]
        if item["identifier"] == "edithatogo/rareburden-commons"
    )
    assert self_result["decision"] == "exclude"
    assert self_result["reason"] == "self_result"
    assert screening["counts"]["potential_entity_duplicate_groups"] == len(
        screening["potential_entity_duplicates"]
    )
    assert all(
        len(group["canonical_keys"]) > 1 for group in screening["potential_entity_duplicates"]
    )
    assert any("not automatically merged" in item.lower() for item in screening["limitations"])
    assert any("No completeness" in item for item in screening["limitations"])
