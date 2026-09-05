from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.economic_summary import calculate_synthetic_component_summary
from rareburden.schema import load_mapping


def test_synthetic_summary_preserves_components_and_blocks_uncertain_aggregation() -> None:
    fixture = load_mapping(Path("examples/economics/component-first-invented.yml"))
    result = calculate_synthetic_component_summary(fixture)
    assert result["intended_use"] == "synthetic_assurance"
    assert [row["component_id"] for row in result["components"]] == [
        "invented_service_contacts",
        "invented_unpaid_care",
        "invented_participation_gap",
    ]
    assert result["components"][0]["aggregation_status"] == "blocked_overlap_uncertainty"
    assert result["components"][1]["aggregation_status"] == "blocked_overlap_uncertainty"
    assert result["components"][2]["aggregation_status"] == "blocked_missingness"
    assert result["eligible_aggregates"] == []
    assert result["valuation_blocked_component_ids"] == []


@pytest.mark.parametrize(
    "changed_context", [None, "population", "geography", "observation_period", "perspective"]
)
def test_aggregation_requires_matching_context(changed_context: str | None) -> None:
    fixture = load_mapping(Path("examples/economics/component-first-invented.yml"))
    first = deepcopy(fixture["components"][0])
    first["overlap"] = {
        "assessment_status": "assessed_no_overlap",
        "component_ids": [],
        "rationale": "Invented disjoint resources for this test.",
    }
    second = deepcopy(first)
    second["component_id"] = "another_resource"
    if changed_context in {"population", "geography"}:
        second[changed_context]["id"] = "different_context"
    elif changed_context == "observation_period":
        second[changed_context] = {"start": "2020-01-01", "end": "2020-12-31"}
    elif changed_context == "perspective":
        second[changed_context]["definition_reference"] = "local:invented/other_perspective"
    fixture["components"] = [first, second]
    result = calculate_synthetic_component_summary(fixture)
    aggregates = result["eligible_aggregates"]
    assert len(aggregates) == (1 if changed_context is None else 2)
    assert sum(item["value"] for item in aggregates) == 2 * first["quantity"]["value"]
    assert all("population" in item and "observation_period" in item for item in aggregates)
