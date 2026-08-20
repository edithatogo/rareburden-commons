from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_option_a_scope_remains_bounded_and_inactive() -> None:
    scope = yaml.safe_load((ROOT / "docs/track-002-option-a-scope.yml").read_text(encoding="utf-8"))
    assert scope["activation"] == "disabled_until_exact_owner_activation_and_publisher_rights"
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


def test_candidate_manifests_preserve_source_specific_terms_and_unapproved_state() -> None:
    wpp = yaml.safe_load(
        (ROOT / "docs/track-002-un-wpp-2024-candidate.yml").read_text(encoding="utf-8")
    )
    who = yaml.safe_load(
        (ROOT / "docs/track-002-who-ghe-2021-candidate.yml").read_text(encoding="utf-8")
    )

    assert wpp["licence_state"] == "exact_workbook_cc_by_3_0_igo_observed"
    assert wpp["decision"] == "candidate_only_terms_observed_activation_disabled"
    assert wpp["redistribution_position"].startswith("permitted_with_attribution")
    assert who["licence_state"] == "conditional"
    assert who["decision"] == "candidate_only_raw_hf_upload_withheld"
    assert who["redistribution_position"].startswith("conditional_pending_")

    for candidate in (wpp, who):
        assert candidate["methods_advice"].startswith("bounded agent-panel advice")
        assert candidate["owner_data_use_disposition"]
        assert candidate["source_change_exercise"].startswith("complete 2026-08-20")
        assert candidate["exact_url"].startswith("https://")
        assert candidate["landing_page_url"].startswith("https://")
        assert candidate["licence_or_terms_url"].startswith("https://")
        assert len(candidate["sha256"]) == 64
        assert candidate["size_bytes"] > 0
