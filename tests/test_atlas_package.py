from __future__ import annotations

import copy

import pytest

from rareburden.atlas import AtlasPackageError, build_gap_api_response, build_gap_package
from rareburden.gapmap import build_domain_gap_map
from rareburden.schema import load_mapping

ROOT = __import__("pathlib").Path(__file__).parents[1]


def _gap_map() -> dict[str, object]:
    return build_domain_gap_map(
        load_mapping(ROOT / "catalog/data_sources.yml"),
        load_mapping(ROOT / "examples/config/gap-map-needs.yml"),
    )


def test_gap_package_is_deterministic_aggregate_only_and_preserves_missingness() -> None:
    first = build_gap_package(_gap_map(), release_id="synthetic-gap-v1", source_manifest_id="rel-1")
    second = build_gap_package(
        _gap_map(), release_id="synthetic-gap-v1", source_manifest_id="rel-1"
    )
    assert first == second
    assert first["aggregate_only"] is True
    assert first["missingness_policy"] == "preserve_missing_not_zero"
    assert first["package_fingerprint"].startswith("atlas-")
    assert any(row["sufficiency"] == "not_assessed" for row in first["rows"])


@pytest.mark.parametrize("field", ["release_id", "source_manifest_id"])
def test_gap_package_requires_release_identity(field: str) -> None:
    kwargs = {"release_id": "synthetic-gap-v1", "source_manifest_id": "rel-1"}
    kwargs[field] = ""
    with pytest.raises(AtlasPackageError):
        build_gap_package(_gap_map(), **kwargs)


def test_gap_package_rejects_empty_rows() -> None:
    value = copy.deepcopy(_gap_map())
    value["rows"] = []
    with pytest.raises(AtlasPackageError):
        build_gap_package(value, release_id="synthetic-gap-v1", source_manifest_id="rel-1")


def test_gap_api_projection_preserves_package_identity_and_is_read_only() -> None:
    package = build_gap_package(
        _gap_map(), release_id="synthetic-gap-v1", source_manifest_id="rel-1"
    )
    response = build_gap_api_response(package)
    assert response["read_only"] is True
    assert response["package_fingerprint"] == package["package_fingerprint"]
    assert response["rows"] == package["rows"]
    assert response["missingness_policy"] == package["missingness_policy"]


def test_gap_api_projection_rejects_non_relative_or_non_aggregate_inputs() -> None:
    package = build_gap_package(
        _gap_map(), release_id="synthetic-gap-v1", source_manifest_id="rel-1"
    )
    with pytest.raises(AtlasPackageError):
        build_gap_api_response(package, endpoint="https://example.invalid/gaps")
    with pytest.raises(AtlasPackageError):
        build_gap_api_response({"rows": package["rows"]})
