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


def test_deferred_candidate_manifests_remain_conditional_and_unapproved() -> None:
    for filename, source_id in (
        ("track-002-un-wpp-2024-candidate.yml", "un-world-population-prospects"),
        ("track-002-who-ghe-2021-candidate.yml", "who-global-health-estimates"),
    ):
        candidate = yaml.safe_load((ROOT / "docs" / filename).read_text(encoding="utf-8"))
        assert candidate["source_id"] == source_id
        assert candidate["licence_state"] == "conditional"
        assert candidate["decision"] == "candidate_only"
        assert candidate["redistribution_position"] == "pending_review"
        assert candidate["third_party_material"] == "pending_review"
        assert candidate["scientific_reviewer"] == "pending"
        assert candidate["data_governance_reviewer"] == "pending"
        assert candidate["exact_url"].startswith("https://")
        assert candidate["landing_page_url"].startswith("https://")
        assert candidate["licence_or_terms_url"].startswith("https://")
        assert len(candidate["sha256"]) == 64
        assert candidate["size_bytes"] > 0
