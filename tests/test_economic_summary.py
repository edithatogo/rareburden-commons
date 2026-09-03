from pathlib import Path

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
