from __future__ import annotations

import copy
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
