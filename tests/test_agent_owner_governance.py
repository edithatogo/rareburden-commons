from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_normative_governance_uses_agent_panels_and_owner() -> None:
    adr = (ROOT / "docs/decisions/ADR-0009-agent-panel-owner-governance.md").read_text()
    policy = (ROOT / "docs/subagent-review-panel-policy.md").read_text()
    workflow = (ROOT / "conductor/workflow.md").read_text()
    assert "No additional person" in adr
    assert "role-separated agent" in policy
    assert "repository owner decides" in workflow
    assert "ADR-0009" in workflow


def test_unchecked_track_tasks_do_not_require_people_or_independent_review() -> None:
    prohibited = (
        "independent methods",
        "independent reproduction",
        "independent-operator",
        "patient/community review",
        "external scientific",
        "recruit patient",
    )
    for plan in sorted((ROOT / "conductor/tracks").glob("*/plan.md")):
        unchecked = "\n".join(
            line for line in plan.read_text().splitlines() if line.startswith("- [ ]")
        ).lower()
        for phrase in prohibited:
            assert phrase not in unchecked, f"{plan}: {phrase}"


def test_public_source_gate_separates_owner_use_from_publisher_rights() -> None:
    matrix = yaml.safe_load((ROOT / "docs/track-002-activation-matrix.yml").read_text())
    rows = {row["source_id"]: row for row in matrix["rows"]}
    assert set(rows) == {
        "orphadata-science",
        "un-world-population-prospects",
        "who-global-health-estimates",
        "world-bank-indicators-api",
    }
    assert all("owner_data_use" in row["required_receipts"] for row in rows.values())
    assert (
        "publisher_third_party_rights" in rows["who-global-health-estimates"]["required_receipts"]
    )


def test_backup_acceptance_is_recorded_without_false_handoff_claim() -> None:
    decision = (
        ROOT / "docs/decisions/2026-08-15-public-source-data-use-and-backup-owner.md"
    ).read_text()
    normalized = " ".join(decision.split())
    assert "backup operational owner has accepted" in normalized
    assert "not a completed handoff exercise" in normalized
