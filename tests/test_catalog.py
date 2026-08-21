from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.catalog import (
    CatalogValidationError,
    load_schema,
    load_yaml,
    validate_catalog,
    validate_catalog_files,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog" / "data_sources.yml"
SCHEMA = ROOT / "schemas" / "data-source.schema.json"


def test_seed_catalog_is_valid() -> None:
    summary = validate_catalog_files(CATALOG, SCHEMA)
    assert summary.source_count >= 10
    assert summary.access_class_counts["open_download_api"] >= 5
    assert summary.access_class_counts["controlled_research"] >= 2


def test_duplicate_source_ids_are_rejected() -> None:
    catalog = load_yaml(CATALOG)
    schema = load_schema(SCHEMA)
    invalid = deepcopy(catalog)
    invalid["sources"].append(deepcopy(invalid["sources"][0]))

    with pytest.raises(CatalogValidationError, match="Duplicate source_id"):
        validate_catalog(invalid, schema)


def test_unknown_access_class_is_rejected() -> None:
    catalog = load_yaml(CATALOG)
    schema = load_schema(SCHEMA)
    invalid = deepcopy(catalog)
    invalid["sources"][0]["access_class"] = "email_someone"

    with pytest.raises(CatalogValidationError, match="access_class"):
        validate_catalog(invalid, schema)


def test_controlled_source_cannot_be_freely_redistributable() -> None:
    catalog = load_yaml(CATALOG)
    schema = load_schema(SCHEMA)
    invalid = deepcopy(catalog)
    controlled = next(
        source for source in invalid["sources"] if source["access_class"] == "controlled_research"
    )
    controlled["redistribution"] = "yes"

    with pytest.raises(CatalogValidationError, match="individual-level sources"):
        validate_catalog(invalid, schema)


def test_restricted_source_families_are_indexed_but_fail_closed() -> None:
    records = {source["source_id"]: source for source in load_yaml(CATALOG)["sources"]}
    restricted = {
        "human-phenotype-ontology",
        "who-icd-10-11",
        "omim",
        "snomed-ct",
        "snomed-ct-national-edition-germany",
        "meddra",
    }
    assert restricted <= records.keys()
    for source_id in restricted:
        source = records[source_id]
        assert source["status"] == "blocked"
        assert source["verification"]["acquisition_test"]["status"] == "blocked"
        assert source["verification"]["terms_review"]["status"] == "blocked"

    ghed = records["who-global-health-expenditure-database"]
    assert ghed["status"] == "blocked"
    assert ghed["redistribution"] == "unknown"
