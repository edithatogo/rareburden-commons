from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
DECISION = ROOT / "docs/track-002-private-archive-capacity-decision-2026-08-16.yml"
CHECKLIST = ROOT / "docs/track-002-private-archive-capacity-checklist-2026-08-16.yml"
SOURCE = ROOT / "manifests/uts/all-release-families-2026-08-15.json"
CAPACITY = ROOT / "manifests/uts/hf-private-capacity-state-2026-08-16.json"


def test_backlog_is_derived_from_exact_uts_manifest_and_checkpoint() -> None:
    decision = yaml.safe_load(DECISION.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    historical = {
        family["release_type"]: sum(
            not release.get("current", False) for release in family["releases"]
        )
        for family in source["families"]
    }
    expected_remaining = dict(historical)
    expected_remaining["umls-metathesaurus-mrconso-file"] -= 5

    assert sum(historical.values()) == decision["backlog"]["historical_artifacts_initial"] == 2437
    assert decision["backlog"]["verified_historical_artifacts"] == 5
    assert expected_remaining == decision["backlog"]["remaining_by_family"]
    assert (
        sum(expected_remaining.values())
        == decision["backlog"]["remaining_historical_artifacts"]
        == 2432
    )
    assert decision["backlog"]["remaining_bytes"] == "unknown"
    family_cursor = decision["backlog"]["latest_family_cursor"]
    assert family_cursor["family"] == "umls-metathesaurus-full-subset"
    assert family_cursor["observed_verified"] == 12
    assert family_cursor["observed_pending"] == 2
    assert family_cursor["failed_run_max_artifacts"] == 1
    assert family_cursor["cursor_advanced_by_failed_run"] is False


def test_decision_preserves_exact_quota_failure_and_no_paid_action() -> None:
    decision = yaml.safe_load(DECISION.read_text(encoding="utf-8"))
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))

    assert decision["current_state"]["capacity"] == capacity["status"] == "blocked"
    assert decision["current_state"]["evidence"] == capacity["evidence"]["reference"]
    assert decision["current_state"]["failure"]["http_status"] == 403
    assert decision["current_state"]["safeguards"] == {
        "cursor_advanced": False,
        "failed_payload_archived": False,
        "redownload_permitted": False,
    }
    assert decision["claims"]["paid_resource_created"] is False
    assert decision["claims"]["capacity_restored"] is False
    unauthorized = " ".join(decision["recommendation"]["actions_not_authorized"]).lower()
    assert "purchasing" in unauthorized
    assert "creating an object-store" in unauthorized
    assert "redownloading licensed bytes" in unauthorized
    assert "capacity state to ready" in unauthorized


def test_options_have_tradeoffs_contingencies_and_fail_closed_default() -> None:
    decision = yaml.safe_load(DECISION.read_text(encoding="utf-8"))
    options = {option["id"]: option for option in decision["options"]}

    assert set(options) == {"A", "B", "C"}
    assert all(
        option["benefits"] and option["tradeoffs"] and option["contingencies"]
        for option in options.values()
    )
    assert decision["recommendation"]["immediate"] == "C"
    assert decision["recommendation"]["preferred_resumption"] == "A"
    assert decision["claims"]["historical_archive_complete"] is False
    assert decision["claims"]["public_redistribution"] is False
    tranche = decision["recommendation"]["proposed_first_tranche_after_unblock"]
    assert tranche["family"] == "umls-metathesaurus-full-subset"
    assert tranche["maximum_artifacts"] == 2
    public_boundary = decision["parallel_public_archive_boundary"]
    assert public_boundary["scope"] == "mondo_public_release_assets"
    assert public_boundary["canary"] == "github-actions:31900277331"
    assert public_boundary["receipt_sha256"] == (
        "a69f97827208a05290634be0701e3a82e03959a2ff1cd6b98ace2e2f0336b17d"
    )
    assert "does not\nchange Options A, B or C" in public_boundary["relevance"]


def test_checklist_cannot_authorize_download_or_cursor_advance() -> None:
    checklist = yaml.safe_load(CHECKLIST.read_text(encoding="utf-8"))
    assert checklist["status"] == "not_authorized"
    assert checklist["fail_closed_until_all_steps_pass"] is True
    assert all(
        step["status"] == "pending" and step["required_evidence"] for step in checklist["steps"]
    )
    assert checklist["current_behavior"] == {
        "capacity_state": "blocked",
        "source_download_allowed": False,
        "cursor_advance_allowed": False,
        "paid_resource_creation_allowed": False,
    }
