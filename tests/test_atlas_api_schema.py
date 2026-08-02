from __future__ import annotations

from pathlib import Path

from rareburden.atlas import build_gap_api_response, build_gap_package
from rareburden.gapmap import build_domain_gap_map
from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).parents[1]


def test_atlas_api_response_is_schema_valid_and_preserves_package_parity() -> None:
    gap_map = build_domain_gap_map(
        load_mapping(ROOT / "catalog/data_sources.yml"),
        load_mapping(ROOT / "examples/config/gap-map-needs.yml"),
    )
    package = build_gap_package(gap_map, release_id="synthetic-gap-v1", source_manifest_id="rel-1")
    response = build_gap_api_response(package)
    validate_instance(response, load_mapping(ROOT / "schemas/atlas-api-response.schema.json"))
    assert response["package_fingerprint"] == package["package_fingerprint"]
    assert response["rows"] == package["rows"]
