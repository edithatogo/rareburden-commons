from __future__ import annotations

from pathlib import Path

from rareburden.atlas import (
    build_atlas_release_candidate,
    build_gap_api_response,
    build_gap_package,
)
from rareburden.gapmap import build_domain_gap_map
from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).parents[1]


def test_prepared_atlas_release_candidate_is_schema_valid() -> None:
    gap_map = build_domain_gap_map(
        load_mapping(ROOT / "catalog/data_sources.yml"),
        load_mapping(ROOT / "examples/config/gap-map-needs.yml"),
    )
    package = build_gap_package(gap_map, release_id="synthetic-gap-v1", source_manifest_id="rel-1")
    response = build_gap_api_response(package)
    candidate = build_atlas_release_candidate(
        package,
        response,
        reviewed_artifacts=[
            {
                "artifact_id": "gap-package-json",
                "sha256": "a" * 64,
                "package_fingerprint": package["package_fingerprint"],
                "review_receipt_id": "repository-review-gap-001",
                "review_state": "repository_reviewed_bounded",
                "licence_state": "redistributable",
            }
        ],
        citation_id="citation-synthetic-gap-v1",
        provenance_id="prov-synthetic-gap-v1",
    )
    validate_instance(candidate, load_mapping(ROOT / "schemas/atlas-release-surface.schema.json"))
