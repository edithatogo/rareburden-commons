"""Reporting fixtures and fail-closed execution-decision tests."""

import csv
import io
from pathlib import Path
from types import SimpleNamespace

import jsonschema
import pytest

from scripts import track003_reference_package as package
from scripts.track003_reference_inputs import build_reference_inputs
from scripts.track003_reference_package import (
    candidate_manifest,
    render_outputs,
    validate_disposition,
)
from scripts.track003_reference_runner import simulate

ROOT = Path(__file__).resolve().parents[1]


def pending_decision():
    return {
        "schema_version": "1.0.0",
        "simulation_status": "simulated_role_separated_advisory_panel",
        "track_id": "003-monogenic-diabetes-demonstrator",
        "candidate": {"commit": "a" * 40, "tree": "b" * 40, "evidence_manifest_sha256": "c" * 64},
        "panel": {
            "perspectives": ["science", "engineering", "simulated_harm"],
            "non_representation_statement": "Advisory agents are not independent people.",
        },
        "evidence": {
            "references": ["fixture"],
            "observed_facts": [],
            "simulated_assessments": ["fixture"],
            "cannot_infer": ["empirical validity"],
        },
        "uncertainty": ["invented"],
        "dissent": [],
        "stop_triggers": ["drift"],
        "options": [
            {
                "id": identifier,
                "title": title,
                "disposition": disposition,
                "trade_offs": ["fixture"],
                "contingencies": ["fixture"],
                "rationale": "Fixture only, never an actual decision.",
                "minimum_evidence": ["fixture"],
            }
            for identifier, title, disposition in [
                ("A", "Execute and retain exact synthetic package", "accept"),
                ("B", "Defer candidate", "defer"),
            ]
        ],
        "recommendation": {"option_id": "A", "rationale": "Fixture is not an approval."},
        "owner_decision": {"status": "pending"},
    }


def test_pending_disposition_rejects_before_any_git_or_simulation():
    with pytest.raises(ValueError, match="pending"):
        validate_disposition(ROOT, pending_decision())


def test_manifest_binds_all_scenarios_and_code_without_execution():
    manifest = candidate_manifest(ROOT)
    assert len(manifest["scenarios"]) == 12
    assert manifest["status"] == "exact_candidate_execution_disposition_pending"
    assert manifest["iterations"] == 10000
    assert manifest["seed"] == 20260830
    assert "scripts/track003_reference_package.py" in manifest["files"]
    assert "uv.lock" in manifest["files"]
    assert manifest == candidate_manifest(ROOT)


def test_report_and_csv_preserve_all_metric_labels_without_governed_execution():
    calculation = simulate(build_reference_inputs(ROOT), ROOT, iterations=100, seed=3)
    outputs = render_outputs(calculation)
    rows = list(csv.DictReader(io.StringIO(outputs["reference-tables.csv"])))
    expected = sum(len(item["summaries"]) for item in calculation["scenarios"].values())
    assert len(rows) == expected
    assert all(row["unit"] and row["conditioning_scope"] for row in rows)
    assert all(row["evidence_status"] == "synthetic_assumption" for row in rows)
    assert "Unknown/uncovered burden is unavailable, not zero" in outputs["reference-report.md"]
    assert "not an execution permission" in outputs["reference-report.md"]
    for phrase in [
        "synthetic-rbc-p002",
        "ages 0-100",
        "D=1/E=1",
        "complication-free",
        "unquantified uncertainty",
        "zero width is not certainty",
    ]:
        assert phrase in outputs["reference-report.md"]
    assert all("unquantified uncertainty" in row["interval_interpretation"] for row in rows)
    assert outputs == render_outputs(calculation)
    calculation["claims"]["empirical_activation"] = True
    with pytest.raises(ValueError, match="claims"):
        render_outputs(calculation)


@pytest.fixture
def accepted(tmp_path, monkeypatch):
    """Mock Git identity and tiny non-analytical files; never a real owner decision."""
    (tmp_path / "schemas").mkdir()
    (tmp_path / "schemas/agent-owner-decision-packet.schema.json").write_bytes(
        (ROOT / "schemas/agent-owner-decision-packet.schema.json").read_bytes()
    )
    manifest = {"files": {}, "seed": 1, "iterations": 100}
    (tmp_path / "manifest.json").write_text(package.canonical(manifest))
    monkeypatch.setattr(package, "MANIFEST", "manifest.json")
    monkeypatch.setattr(package, "candidate_manifest", lambda root: manifest)
    monkeypatch.setattr(
        package.subprocess,
        "check_output",
        lambda command, **kwargs: {"HEAD": "a" * 40, "HEAD^{tree}": "b" * 40}.get(command[-1], ""),
    )
    monkeypatch.setattr(
        package.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=0)
    )
    decision = pending_decision()
    decision["owner_decision"] = {
        "status": "recorded",
        "selected_option_id": "A",
        "decided_by": "edithatogo",
        "decided_at_utc": "2026-08-30T00:00:00Z",
        "rationale": "Synthetic test fixture, never an actual decision.",
    }
    decision["candidate"]["evidence_manifest_sha256"] = package.digest(
        (tmp_path / "manifest.json").read_bytes()
    )
    return tmp_path, decision


def test_accepted_fixture_validates_without_executing(accepted):
    root, decision = accepted
    assert package.validate_disposition(root, decision)["seed"] == 1


@pytest.mark.parametrize(
    "change",
    [
        "track",
        "duplicate",
        "timestamp",
        "manifest",
        "commit",
        "tree",
        "selection",
        "recommendation",
        "title",
        "option",
    ],
)
def test_decision_mutations_rejected(accepted, change):
    root, decision = accepted
    if change == "track":
        decision["track_id"] = "004-other-track"
    elif change == "duplicate":
        decision["options"][1]["id"] = "A"
    elif change == "timestamp":
        decision["owner_decision"]["decided_at_utc"] = "invalid"
    elif change in {"commit", "tree"}:
        decision["candidate"][change] = "d" * 40
    elif change == "manifest":
        decision["candidate"]["evidence_manifest_sha256"] = "d" * 64
    elif change == "selection":
        decision["owner_decision"]["selected_option_id"] = "B"
    elif change == "recommendation":
        decision["recommendation"]["option_id"] = "C"
    elif change == "title":
        decision["options"][0]["title"] = "Different permission"
    else:
        decision["options"][0]["disposition"] = "defer"
    with pytest.raises((ValueError, jsonschema.ValidationError)):
        package.validate_disposition(root, decision)


def test_imported_root_must_match_checkout(tmp_path):
    with pytest.raises(ValueError, match="module root"):
        package.validate_execution_roots(tmp_path)
    package.validate_execution_roots(ROOT)


@pytest.mark.parametrize("change", ["decision", "manifest", "dirty"])
def test_mid_calculation_drift_prevents_output(accepted, monkeypatch, change):
    root, decision = accepted
    decision_path = root / "decision.json"
    decision_path.write_text(package.canonical(decision))
    monkeypatch.setattr(package, "validate_execution_roots", lambda root: None)
    monkeypatch.setattr(package, "build_reference_inputs", lambda root: {})
    monkeypatch.setattr(
        package,
        "render_outputs",
        lambda calculation: dict.fromkeys(package.OUTPUTS, "non-analytical fixture"),
    )

    def changed(*args, **kwargs):
        if change == "decision":
            decision_path.write_text("{}")
        elif change == "manifest":
            (root / "manifest.json").write_text("{}")
        else:
            monkeypatch.setattr(
                package.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=1)
            )
        return {}

    monkeypatch.setattr(package, "simulate", changed)
    output = root / "output"
    with pytest.raises(ValueError):
        package.execute(root, decision_path, output)
    assert not output.exists()
