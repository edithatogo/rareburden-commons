from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from rareburden.economic_components import (
    EconomicComponentError,
    validate_component_prototype,
)
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load_mapping(ROOT / "schemas/economic-component-prototype.schema.json")
FIXTURE = load_mapping(ROOT / "examples/economics/component-first-invented.yml")


def _changed(component_index: int = 0) -> dict[str, object]:
    document = deepcopy(FIXTURE)
    assert isinstance(document["components"], list)
    assert isinstance(document["components"][component_index], dict)
    return document


def test_schema_and_invented_fixture_validate_and_round_trip_detached() -> None:
    Draft202012Validator.check_schema(SCHEMA)
    result = validate_component_prototype(FIXTURE)
    assert result == FIXTURE
    assert result is not FIXTURE
    result["limitations"].append("Caller mutation")  # type: ignore[union-attr]
    assert "Caller mutation" not in FIXTURE["limitations"]


def test_validation_always_uses_canonical_schema_and_missing_components_fail_safely() -> None:
    with pytest.raises(EconomicComponentError, match="failed schema validation") as error:
        validate_component_prototype({"synthetic": True})
    assert "synthetic" not in str(error.value)
    with pytest.raises(TypeError):
        validate_component_prototype(FIXTURE, {})  # type: ignore[call-arg]


@pytest.mark.parametrize("status", ["missing", "not_collected", "unassessed"])
def test_missing_statuses_never_accept_or_create_zero(status: str) -> None:
    document = _changed(2)
    quantity = document["components"][2]["quantity"]  # type: ignore[index]
    quantity["measurement_status"] = status
    document["components"][2]["missingness"]["status"] = status  # type: ignore[index]
    assert "value" not in validate_component_prototype(document)["components"][2]["quantity"]
    quantity["value"] = 0
    with pytest.raises(EconomicComponentError, match="failed schema validation"):
        validate_component_prototype(document)


def test_explicit_zero_is_distinct_from_present_nonzero() -> None:
    document = _changed()
    quantity = document["components"][0]["quantity"]  # type: ignore[index]
    quantity["measurement_status"] = "explicit_zero"
    quantity["value"] = 0
    result = validate_component_prototype(document)
    assert result["components"][0]["quantity"]["value"] == 0
    quantity["measurement_status"] = "explicit_value"
    with pytest.raises(EconomicComponentError, match="failed schema validation"):
        validate_component_prototype(document)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (True, "failed schema validation"),
        (float("nan"), "finite number"),
        (float("inf"), "finite number"),
    ],
)
def test_quantity_rejects_boolean_or_nonfinite_values(value: object, message: str) -> None:
    document = _changed()
    document["components"][0]["quantity"]["value"] = value  # type: ignore[index]
    with pytest.raises(EconomicComponentError, match=message):
        validate_component_prototype(document)


def test_unpaid_care_remains_present_unvalued_and_economically_blocked() -> None:
    result = validate_component_prototype(FIXTURE)
    care = result["components"][1]
    assert care["quantity"]["measurement_status"] == "explicit_value"
    assert care["quantity"]["value"] == 40
    assert care["valuation_readiness"]["valuation_status"] == "not_applicable"
    assert result["economic_use_status"] == "blocked"


def test_roles_and_partial_coverage_remain_independent() -> None:
    result = validate_component_prototype(FIXTURE)
    care = result["components"][1]
    assert care["roles"]["bearer"]["label"] == "Invented household"
    assert care["roles"]["payer"]["status"] == "not_applicable"
    assert care["roles"]["time_provider"]["label"] == "Invented unpaid carer"
    assert care["roles"]["recipient"]["status"] == "unassessed"
    assert care["roles"]["beneficiary"]["status"] == "unassessed"
    assert result["components"][0]["coverage"]["status"] == "partial"
    assert "total" not in result


@pytest.mark.parametrize(
    "reference",
    [
        "https://example.test/source",
        "../source",
        "/tmp/source",
        "local:invented/a?b",
        "local:invented/a//b",
        "local:invented/a/",
    ],
)
def test_references_reject_urls_paths_and_queries(reference: str) -> None:
    document = _changed()
    document["components"][0]["assumption_references"] = [reference]  # type: ignore[index]
    with pytest.raises(EconomicComponentError, match="failed schema validation") as error:
        validate_component_prototype(document)
    assert reference not in str(error.value)


def test_overlap_must_reference_other_known_components() -> None:
    for reference, message in (
        ("invented_service_contacts", "self-reference"),
        ("invented_unknown", "unknown component"),
    ):
        document = _changed()
        document["components"][0]["overlap"]["component_ids"] = [reference]  # type: ignore[index]
        with pytest.raises(EconomicComponentError, match=message):
            validate_component_prototype(document)


def test_duplicate_identity_and_reversed_period_fail() -> None:
    duplicate = _changed()
    duplicate["components"].append(deepcopy(duplicate["components"][0]))  # type: ignore[union-attr,index]
    with pytest.raises(EconomicComponentError, match="duplicate component identity"):
        validate_component_prototype(duplicate)
    reversed_period = _changed()
    reversed_period["components"][0]["observation_period"] = {  # type: ignore[index]
        "start": "2025-12-31",
        "end": "2025-01-01",
    }
    with pytest.raises(EconomicComponentError, match="period is reversed"):
        validate_component_prototype(reversed_period)


def test_mismatched_missingness_and_ambiguous_component_revision_fail() -> None:
    mismatch = _changed(2)
    mismatch["components"][2]["missingness"]["status"] = "complete"  # type: ignore[index]
    with pytest.raises(EconomicComponentError, match="missingness status"):
        validate_component_prototype(mismatch)
    duplicate = _changed()
    second = deepcopy(duplicate["components"][0])  # type: ignore[index]
    second["revision"] = 2
    duplicate["components"].append(second)  # type: ignore[union-attr]
    with pytest.raises(EconomicComponentError, match="duplicate component identity"):
        validate_component_prototype(duplicate)

    value_mismatch = _changed()
    value_mismatch["components"][0]["missingness"]["status"] = "not_collected"  # type: ignore[index]
    with pytest.raises(EconomicComponentError, match="missingness status"):
        validate_component_prototype(value_mismatch)


def test_overlap_status_and_references_are_consistent() -> None:
    unassessed = _changed(1)
    unassessed["components"][1]["overlap"]["component_ids"] = [  # type: ignore[index]
        "invented_service_contacts"
    ]
    with pytest.raises(EconomicComponentError, match="status cannot list"):
        validate_component_prototype(unassessed)
    possible = _changed()
    possible["components"][0]["overlap"]["component_ids"] = []  # type: ignore[index]
    with pytest.raises(EconomicComponentError, match="requires a component"):
        validate_component_prototype(possible)


def test_cyclic_and_excessively_deep_inputs_fail_with_safe_error() -> None:
    cyclic: dict[str, object] = {}
    cyclic["nested"] = cyclic
    with pytest.raises(EconomicComponentError, match="structure limits"):
        validate_component_prototype(cyclic)
    deep: dict[str, object] = {}
    cursor = deep
    for _ in range(22):
        child: dict[str, object] = {}
        cursor["nested"] = child
        cursor = child
    with pytest.raises(EconomicComponentError, match="structure limits"):
        validate_component_prototype(deep)


def test_declared_maximum_component_count_fits_structure_limit() -> None:
    document = _changed()
    template = deepcopy(document["components"][1])  # type: ignore[index]
    components = []
    for index in range(50):
        component = deepcopy(template)
        component["component_id"] = f"invented_component_{index:02d}"
        components.append(component)
    document["components"] = components
    assert len(validate_component_prototype(document)["components"]) == 50


def test_arbitrarily_large_integer_is_finite_without_float_conversion() -> None:
    document = _changed()
    document["components"][0]["quantity"]["value"] = 10**309  # type: ignore[index]
    result = validate_component_prototype(document)
    assert result["components"][0]["quantity"]["value"] == 10**309


def test_unknown_sensitive_shaped_field_is_rejected_without_echo() -> None:
    document = _changed()
    secret = "credential-material-must-not-appear"
    document["components"][0]["Credential"] = secret  # type: ignore[index]
    with pytest.raises(EconomicComponentError, match="failed schema validation") as error:
        validate_component_prototype(document)
    assert secret not in str(error.value)


def test_monetary_shaped_record_remains_unresolved_and_blocked() -> None:
    document = _changed()
    component = document["components"][0]  # type: ignore[index]
    component["quantity"]["kind"] = "monetary_shaped"
    component["valuation_readiness"] = {
        "currency_status": "unresolved",
        "price_year_status": "unresolved",
        "valuation_status": "unresolved",
        "rationale": "Monetary-shaped structure remains unusable for economic analysis.",
    }
    result = validate_component_prototype(document)
    assert result["economic_use_status"] == "blocked"
    component["valuation_readiness"]["currency_status"] = "not_applicable"
    with pytest.raises(EconomicComponentError, match="failed schema validation"):
        validate_component_prototype(document)


def test_totals_and_unknown_fields_are_not_contract_surface() -> None:
    document = _changed()
    document["totals"] = []
    with pytest.raises(EconomicComponentError, match="failed schema validation"):
        validate_component_prototype(document)


def test_frozen_ledger_inputs_and_manifests_remain_unchanged() -> None:
    expected = {
        "examples/ledger/economic-social-synthetic.yml": (
            "4d773a9cac101b722d98a5364a279fc5c8c1740b24f8c1c02f7894217b97b29b"
        ),
        "manifests/ledger/track-009-v0.4-contract-freeze.json": (
            "0b655589377921e55b88109aa121be6070718d6ebf21bc31602019a25039557a"
        ),
        "manifests/ledger/track-009-v0.4-economic-social-synthetic.json": (
            "3c4a36431d5f8c992a044e449972907a9b5005f2c733df608556a2ffc8c21da2"
        ),
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
