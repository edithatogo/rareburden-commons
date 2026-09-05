from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from rareburden.atlas import (
    AtlasPackageError,
    build_atlas_release_candidate,
    build_atlas_release_status,
    build_gap_api_response,
    build_gap_package,
    build_static_product_set,
    validate_accessibility_consistency,
)
from rareburden.gapmap import build_domain_gap_map
from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).parents[1]


def _surface() -> tuple[dict, dict, dict]:
    gap_map = build_domain_gap_map(
        load_mapping(ROOT / "catalog/data_sources.yml"),
        load_mapping(ROOT / "examples/config/gap-map-needs.yml"),
    )
    package = build_gap_package(
        gap_map,
        release_id="track-014-static-product-set-v1",
        source_manifest_id="track-013-bounded-reconciliation-2026-08-16",
    )
    candidate = build_atlas_release_candidate(
        package,
        build_gap_api_response(package),
        reviewed_artifacts=[
            {
                "artifact_id": "track-013-bounded-reconciliation",
                "sha256": "5" * 64,
                "package_fingerprint": package["package_fingerprint"],
                "review_receipt_id": "track-013-repository-bounded-pass",
                "review_state": "repository_reviewed_bounded",
                "licence_state": "metadata_only",
            }
        ],
        citation_id="citation-track-014-synthetic",
        provenance_id="prov-track-014-synthetic",
    )
    return package, candidate, build_atlas_release_status(candidate, [])


def test_static_product_set_builds_exact_bounded_product_types() -> None:
    package, candidate, status = _surface()
    product_set = build_static_product_set(
        package,
        candidate,
        status,
        country_scope_id="XAA",
        demonstrator_scope_id="synthetic-public-foundation",
    )
    validate_instance(
        product_set,
        load_mapping(ROOT / "schemas/atlas-static-product-set.schema.json"),
    )
    assert {item["product_type"] for item in product_set["products"]} == {
        "gap",
        "country",
        "demonstrator",
    }
    assert product_set["publication_authorized"] is False
    assert product_set["synthetic_only"] is True
    assert all(item["estimate_status"] == "not_assessed" for item in product_set["products"])
    assert all(item["text_alternative"] for item in product_set["products"])
    assert all(item["non_colour_status_labels"] for item in product_set["products"])


def test_static_product_set_is_deterministic_and_preserves_exact_identity() -> None:
    package, candidate, status = _surface()
    first = build_static_product_set(
        package,
        candidate,
        status,
        country_scope_id="XAA",
        demonstrator_scope_id="synthetic-public-foundation",
    )
    second = build_static_product_set(
        package,
        candidate,
        status,
        country_scope_id="XAA",
        demonstrator_scope_id="synthetic-public-foundation",
    )
    assert first == second
    assert first["package_fingerprint"] == package["package_fingerprint"]
    assert first["release_surface_fingerprint"] == candidate["release_surface_fingerprint"]
    assert first["status_fingerprint"] == status["status_fingerprint"]


def test_accessibility_consistency_validator_binds_all_three_projections() -> None:
    package, candidate, status = _surface()
    product_set = build_static_product_set(
        package,
        candidate,
        status,
        country_scope_id="XAA",
        demonstrator_scope_id="synthetic-public-foundation",
    )
    result = validate_accessibility_consistency(
        package, build_gap_api_response(package), product_set
    )
    assert result["status"] == "repository_accessibility_contract_valid"
    assert result["product_count"] == 3
    assert result["human_conformance_assessed"] is False
    assert result["real_user_testing_observed"] is False


def test_accessibility_consistency_rejects_projection_drift() -> None:
    package, candidate, status = _surface()
    product_set = build_static_product_set(
        package,
        candidate,
        status,
        country_scope_id="XAA",
        demonstrator_scope_id="synthetic-public-foundation",
    )
    drifted = copy.deepcopy(build_gap_api_response(package))
    drifted["rows"] = []
    with pytest.raises(AtlasPackageError, match="API rows differ"):
        validate_accessibility_consistency(package, drifted, product_set)


def test_prospective_products_route_advisory_review_without_claiming_participation() -> None:
    package, candidate, status = _surface()
    product_set = build_static_product_set(
        package,
        candidate,
        status,
        country_scope_id="XAA",
        demonstrator_scope_id="synthetic-public-foundation",
    )
    assert product_set["synthetic_only"] is True
    assert product_set["publication_authorized"] is False
    for product in product_set["products"]:
        assert (
            "Advisory accessibility/usability challenge and owner disposition remain pending."
            in product["limitations"]
        )
        assert (
            "No actual user participation or independent review is claimed."
            in product["limitations"]
        )
        assert (
            "Independent accessibility and real-user review remain pending."
            not in product["limitations"]
        )
        assert (
            "Synthetic metadata-only design fixture; no empirical burden estimate is presented."
            in product["limitations"]
        )
        assert product["publication_authorized"] is False
        assert product["aggregate_only"] is True
        assert product["estimate_status"] == "not_assessed"
        assert product["rows"] == package["rows"]
        assert product["non_colour_status_labels"] == [
            "Not assessed",
            "Synthetic only",
            "Not published",
        ]


@pytest.mark.parametrize(
    ("country_scope_id", "demonstrator_scope_id"),
    [("", "synthetic-public-foundation"), ("XAA", ""), ("AU", "synthetic")],
)
def test_static_product_set_rejects_ambiguous_or_real_country_scope(
    country_scope_id: str, demonstrator_scope_id: str
) -> None:
    package, candidate, status = _surface()
    with pytest.raises(AtlasPackageError):
        build_static_product_set(
            package,
            candidate,
            status,
            country_scope_id=country_scope_id,
            demonstrator_scope_id=demonstrator_scope_id,
        )


def test_static_product_set_rejects_identity_or_missingness_drift() -> None:
    package, candidate, status = _surface()
    drifted = copy.deepcopy(package)
    drifted["rows"][0]["sufficiency"] = "sufficient"
    with pytest.raises(AtlasPackageError, match="unassessed sufficiency"):
        build_static_product_set(
            drifted,
            candidate,
            status,
            country_scope_id="XAA",
            demonstrator_scope_id="synthetic-public-foundation",
        )


def test_repository_accessibility_review_remains_advisory_and_external_gates_open() -> None:
    review = yaml.safe_load(
        (ROOT / "docs/track-014-repository-accessibility-review-2026-08-21.yml").read_text(
            encoding="utf-8"
        )
    )
    assert review["independent_review"] is False
    assert review["real_user_testing_observed"] is False
    assert review["publication_authorized"] is False
    statuses = {item["id"]: item["status"] for item in review["criteria"]}
    assert statuses["text_alternatives"] == "pass_repository_contract"
    assert statuses["keyboard_and_assistive_technology"] == "not_independently_assessed"
    assert review["findings"]["external_findings"]
