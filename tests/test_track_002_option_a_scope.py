from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_option_a_scope_remains_bounded_and_inactive() -> None:
    scope = yaml.safe_load((ROOT / "docs/track-002-option-a-scope.yml").read_text(encoding="utf-8"))
    assert scope["activation"] == "disabled_until_scientific_and_data_governance_receipts"
    assert [item["source_id"] for item in scope["primary_preparation_sources"]] == [
        "orphadata-science",
        "un-world-population-prospects",
    ]
    deferred = {item["source_id"]: item["status"] for item in scope["deferred_candidates"]}
    assert deferred == {
        "who-global-health-estimates": "candidate_only",
        "world-bank-indicators-api": "probe_only",
    }
    assert "no_raw_third_party_source_bytes_in_repository_or_release" in scope["exclusions"]
