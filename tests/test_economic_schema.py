from __future__ import annotations

from pathlib import Path

import pytest

from rareburden.schema import SchemaValidationError, load_mapping, validate_instance

SCHEMA_PATH = Path("schemas/economic-parameters.schema.json")
FIXTURE_PATH = Path("examples/economics/economic-reference-parameters.yml")


def test_economic_parameters_schema_validates_canonical_fixture() -> None:
    schema = load_mapping(SCHEMA_PATH)
    fixture = load_mapping(FIXTURE_PATH)
    validate_instance(fixture, schema)


def test_economic_parameters_schema_rejects_missing_required_fields() -> None:
    schema = load_mapping(SCHEMA_PATH)
    fixture = load_mapping(FIXTURE_PATH)
    del fixture["perspective"]
    with pytest.raises(SchemaValidationError):
        validate_instance(fixture, schema)


def test_economic_parameters_schema_rejects_valued_without_currency() -> None:
    schema = load_mapping(SCHEMA_PATH)
    fixture = load_mapping(FIXTURE_PATH)
    del fixture["valuation"]["currency"]
    with pytest.raises(SchemaValidationError):
        validate_instance(fixture, schema)
