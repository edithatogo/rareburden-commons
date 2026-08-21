from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[1]
CONTRACT = ROOT / "docs/track-014-evidence-presentation-contract-2026-08-21.yml"
FIXTURES = ROOT / "examples/atlas/evidence-presentation-fixtures.yml"
SCHEMA = ROOT / "schemas/atlas-evidence-presentation-contract.schema.json"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _scenario_failures(record: dict) -> list[str]:
    failures: list[str] = []
    provenance = record["provenance"]
    uncertainty = record["uncertainty"]
    quality = record["quality"]
    missingness = record["missingness"]

    if not provenance.get("release_id") or not provenance.get("source_manifest_id"):
        failures.append("exact provenance identity is required")
    if uncertainty.get("interval_or_range") is None and not uncertainty.get("unavailable_reason"):
        failures.append("uncertainty or an unavailable reason is required")
    if not quality.get("domain_judgements") or "composite_score" in quality:
        failures.append("quality domains cannot be replaced by a composite score")
    if (
        missingness.get("state")
        in {
            "missing",
            "not_assessed",
            "non_estimable",
        }
        and missingness.get("value") is not None
    ):
        failures.append("missing or unassessed values must remain null")
    return failures


def test_contract_is_schema_valid_non_authorizing_and_covers_four_components() -> None:
    contract = _load(CONTRACT)
    schema = _load(SCHEMA)
    Draft202012Validator(schema).validate(contract)
    assert contract["publication_authorized"] is False
    assert contract["external_validation_observed"] is False
    assert set(contract["components"]) == {
        "provenance",
        "uncertainty",
        "quality",
        "missingness",
    }


def test_profiles_cover_exact_journeys_and_preserve_all_components() -> None:
    contract = _load(CONTRACT)
    profiles = contract["journey_profiles"]
    assert {profile["audience"] for profile in profiles} == {
        "patient",
        "policy",
        "research",
        "custodian",
        "funder",
    }
    for profile in profiles:
        assert set(profile["component_order"]) == set(contract["components"])


@pytest.mark.parametrize("scenario", _load(FIXTURES)["scenarios"], ids=lambda item: item["id"])
def test_synthetic_scenarios_have_expected_fail_closed_disposition(scenario: dict) -> None:
    failures = _scenario_failures(scenario["record"])
    if scenario["expected"] == "accept":
        assert failures == []
        assert "rejection_reason" not in scenario
    else:
        assert failures
        assert scenario["rejection_reason"]


def test_contract_keeps_external_validation_and_release_gates_open() -> None:
    required = " ".join(_load(CONTRACT)["validation_boundary"]["still_required"]).lower()
    for phrase in (
        "independent accessibility",
        "real-user usability",
        "licence",
        "separately executed reproduction",
        "release authority",
    ):
        assert phrase in required
