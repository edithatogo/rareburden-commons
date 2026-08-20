from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "conductor/tracks/017-documentation-adoption-v1"


def test_track017_plan_retains_append_only_evidence_history() -> None:
    plan = (TRACK / "plan.md").read_text(encoding="utf-8")
    assert plan.count("- [x]") == 25
    assert plan.count("- [~]") == 0
    assert plan.count("- [ ]") == 18
    for evidence in (
        "track-017-bounded-exercises-2026-08-16.json",
        "v1-evidence-index-2026-08-16.json",
        "track-017-owner-bounded-disposition-2026-08-16.json",
        "track-017-bounded-readiness-2026-08-16.json",
        "track-017-evidence-contract-reconciliation-2026-08-20.md",
    ):
        assert evidence in plan


def test_track017_single_owner_contract_has_no_additional_person_gate() -> None:
    current_contracts = (
        TRACK / "spec.md",
        TRACK / "plan.md",
        TRACK / "review.md",
        ROOT / "conductor/panel-gate-plan.md",
        ROOT / "docs/track-017-v1-implementation-plan-2026-08-02.md",
        ROOT / "docs/v1-release-candidate-checklist-017.md",
        ROOT / "docs/track-017-evidence-contract-reconciliation-2026-08-20.md",
    )
    combined = "\n".join(path.read_text(encoding="utf-8") for path in current_contracts)
    for stale_requirement in (
        "Recruit two independent users",
        "Complete independent node-operator",
        "two independent usability receipts",
        "one independent reproduction and equivalence report",
        "multi-person sign-off",
    ):
        assert stale_requirement not in combined
    assert "No independent or additional-person review is required" in combined
    assert "repository owner records" in combined


def test_reconciliation_preserves_planned_status_and_stable_release_boundary() -> None:
    metadata = json.loads((TRACK / "metadata.json").read_text(encoding="utf-8"))
    review = (TRACK / "review.md").read_text(encoding="utf-8")
    reconciliation = (
        ROOT / "docs/track-017-evidence-contract-reconciliation-2026-08-20.md"
    ).read_text(encoding="utf-8")
    assert metadata["status"] == "planned"
    assert metadata["updated"] == "2026-08-20"
    assert "25 completed" in review
    assert "18 pending" in review
    assert "Track 017 remains Planned" in reconciliation
    assert "stable v1 remains disabled" in reconciliation
