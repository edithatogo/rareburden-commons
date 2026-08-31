"""Map existing reproduction evidence without executing another analysis."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts import check_track003_reference_closeout as check

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "manifests/quality/track013-reproduction-mapping-20260901.json"
TRACK = ROOT / "conductor/tracks/013-quality-validation-gap-equity"


def test_mapped_historical_package_validates_without_simulation(monkeypatch) -> None:
    def forbidden(*args, **kwargs):
        raise AssertionError("Criterion mapping must not execute another analysis")

    monkeypatch.setattr("scripts.track003_reference_package.simulate", forbidden)
    monkeypatch.setattr("scripts.track003_reference_runner.simulate", forbidden)
    check.validate(ROOT)


def test_mapping_binds_exact_evidence_without_new_authority() -> None:
    mapping = json.loads(MAPPING.read_bytes())
    assert mapping["schema_version"] == "1.0.0"
    assert mapping["track_id"] == "013-quality-validation-gap-equity"
    assert mapping["criterion_id"] == 3
    assert mapping["candidate_commit"] == check.COMMIT
    assert mapping["candidate_tree"] == check.TREE
    assert mapping["claims"] == {
        "criterion_satisfied": True,
        "new_analysis_executed": False,
        "new_authorization_recorded": False,
        "independent_review": False,
        "empirical_validation": False,
        "track_complete": False,
        "release": False,
    }
    assert {check.RECEIPT, check.DECISION} <= set(mapping["files"])
    for relative, expected in mapping["files"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected


def test_mapping_uses_two_existing_runs_of_one_candidate() -> None:
    mapping = json.loads(MAPPING.read_bytes())
    receipt = json.loads((ROOT / check.RECEIPT).read_bytes())
    assert receipt["candidate"]["commit"] == mapping["candidate_commit"]
    assert receipt["candidate"]["tree"] == mapping["candidate_tree"]
    assert receipt["decision"] == {"path": check.DECISION, "sha256": check.DECISION_SHA}
    assert [run["role"] for run in receipt["runs"]] == ["primary", "separate_reproduction"]
    assert len({run["checkout_id"] for run in receipt["runs"]}) == 2
    for run in receipt["runs"]:
        assert run["exit_code"] == 0
        assert run["receipt"]["candidate_commit"] == check.COMMIT
        assert run["receipt"]["output_sha256"] == check.OUTPUT_HASHES
    assert receipt["execution_environment"]["same_host"] is True
    assert receipt["execution_environment"]["separate_virtual_environments"] is True
    assert receipt["execution_environment"]["independent_review"] is False
    assert receipt["comparison"]["extra_executions"] == 0


def test_only_reproduction_task_is_closed_while_other_validation_remains_pending() -> None:
    plan = " ".join((TRACK / "plan.md").read_text(encoding="utf-8").split())
    assert (
        "- [x] Run a separately executed owner-operated reproduction of at least one analysis"
        in plan
    )
    for task in (
        "Triangulate monogenic-diabetes estimates.",
        "Triangulate bronchiectasis estimates.",
        "Validate paediatric and economic outputs within their permitted scope.",
        "Decompose uncertainty and identify decision-sensitive parameters.",
    ):
        assert f"- [ ] {task}" in plan
    assert plan.count("- [ ]") == 4
    assert json.loads((TRACK / "metadata.json").read_bytes())["status"] == "blocked"
