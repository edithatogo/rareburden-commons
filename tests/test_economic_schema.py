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


TEMPLATE_PATH = Path("examples/economics/economic-ledger-template.yml")


def test_economic_ledger_template_validates_against_schema() -> None:
    schema = load_mapping(SCHEMA_PATH)
    template = load_mapping(TEMPLATE_PATH)
    validate_instance(template, schema)


def test_economic_ledger_template_stays_data_free() -> None:
    """The template is a scaffold and must not silently acquire data or values.

    Converting it into a bound candidate fixture is a separately named,
    owner-dispositioned act (docs/track-005-method-options-2026-08-31.md).
    These assertions fail closed until then.
    """
    template = load_mapping(TEMPLATE_PATH)
    assert template["quantity"]["measurement_status"] in {"not_collected", "unassessed"}
    assert "value" not in template["quantity"]
    assert template["valuation"]["status"] == "unvalued"
    assert template["missingness"]["status"] in {"not_collected", "unassessed"}
