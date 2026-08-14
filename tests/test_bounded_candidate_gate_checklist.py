from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_bounded_candidate_checklist_is_fail_closed() -> None:
    path = ROOT / "docs/bounded-candidate-gate-checklist-2026-08-03.yml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert document["mode"] == "bounded_synthetic_public"
    assert document["activation"].startswith("disabled")
    statuses = {gate["gate"]: gate["status"] for gate in document["gates"]}
    assert statuses["track_002_source_terms"] == "pending"
    assert statuses["custodian_data_governance"] == "pending"
    assert statuses["release_authority"] == "pending"
    assert len(document["stop_triggers"]) >= 3
