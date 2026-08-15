from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_track_002_terms_matrix_is_complete_and_fail_closed() -> None:
    matrix = yaml.safe_load(
        (ROOT / "docs/track-002-source-terms-matrix.yml").read_text(encoding="utf-8")
    )
    assert matrix["status"] == "bounded_owner_disposition_preparation_only"
    assert matrix["activation"] == "disabled_until_accountable_dispositions"
    assert {record["source_id"] for record in matrix["records"]} == {
        "orphadata-science",
        "un-world-population-prospects",
        "who-global-health-estimates",
        "world-bank-indicators-api",
    }
    for record in matrix["records"]:
        assert record["exact_record"]
        assert record["licence_state"]
        assert record["redistribution"]
        assert record["scientific_disposition"] == "pending" or record[
            "scientific_disposition"
        ].startswith("owner_bounded_")
        assert record["data_governance_disposition"].startswith("owner_")
        assert record["source_change_exercise"] == "pending"
    who = next(
        record
        for record in matrix["records"]
        if record["source_id"] == "who-global-health-estimates"
    )
    assert "publisher_third_party_rights_pending" in who["data_governance_disposition"]
