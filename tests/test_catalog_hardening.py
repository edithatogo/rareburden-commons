from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.catalog import (
    CatalogValidationError,
    _invariant_errors,
    load_yaml,
    validate_catalog,
)
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog" / "data_sources.yml"
SCHEMA = load_mapping(ROOT / "schemas" / "data-source.schema.json")


def _catalog() -> dict[str, object]:
    return deepcopy(load_mapping(CATALOG_PATH))


def test_yaml_loader_fails_closed_for_missing_invalid_and_non_mapping(tmp_path: Path) -> None:
    with pytest.raises(CatalogValidationError, match="not found"):
        load_yaml(tmp_path / "missing.yml")

    malformed = tmp_path / "malformed.yml"
    malformed.write_text("root: [unterminated\n", encoding="utf-8")
    with pytest.raises(CatalogValidationError, match="Invalid YAML"):
        load_yaml(malformed)

    sequence = tmp_path / "sequence.yml"
    sequence.write_text("- not\n- a\n- mapping\n", encoding="utf-8")
    with pytest.raises(CatalogValidationError, match="Expected a YAML mapping"):
        load_yaml(sequence)


def test_catalog_invariants_report_all_security_and_access_errors() -> None:
    catalog = _catalog()
    source = catalog["sources"][0]  # type: ignore[index]
    duplicate = deepcopy(source)
    catalog["sources"].append(duplicate)  # type: ignore[union-attr]
    source["access_url"] = "http://example.org/data"  # type: ignore[index]
    source["official_reference"] = "relative/path"  # type: ignore[index]
    source["last_verified"] = "19-07-2026"  # type: ignore[index]
    source["verification"] = {  # type: ignore[index]
        "access_test": {"status": "passed", "verified_at": "not-a-date"},
        "ignored_non_mapping": "bad",
    }
    source["geographic_levels"] = ["national"]  # type: ignore[index]
    source["maximum_geographic_resolution"] = "subnational_1"  # type: ignore[index]
    source["data_level"] = "individual_level"  # type: ignore[index]
    source["redistribution"] = "yes"  # type: ignore[index]
    source["access_class"] = "controlled_research"  # type: ignore[index]
    source["registration_required"] = False  # type: ignore[index]

    errors = _invariant_errors(catalog)
    joined = "\n".join(errors)
    assert "Duplicate source_id" in joined
    assert "access_url" in joined and "official_reference" in joined
    assert "last_verified" in joined
    assert "verification.access_test.verified_at" in joined
    assert "maximum_geographic_resolution" in joined
    assert "individual-level sources" in joined
    assert "controlled research access" in joined


def test_catalog_non_list_and_non_mapping_entries_are_safely_ignored_by_invariants() -> None:
    assert _invariant_errors({"sources": "invalid"}) == []
    assert _invariant_errors({"sources": [None, "bad"]}) == []


def test_schema_and_invariant_failures_are_aggregated() -> None:
    catalog = _catalog()
    source = catalog["sources"][0]  # type: ignore[index]
    source.pop("name")  # type: ignore[union-attr]
    source["access_url"] = "ftp://example.org/data"  # type: ignore[index]
    with pytest.raises(CatalogValidationError) as caught:
        validate_catalog(catalog, SCHEMA)
    message = str(caught.value)
    assert "'name' is a required property" in message
    assert "access_url" in message
