from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_track_009_freeze_readiness import Track009ReadinessError, validate

ROOT = Path(__file__).parents[1]
READINESS = ROOT / "docs/track-009-freeze-readiness-2026-08-21.yml"


def _candidate(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "readiness.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_current_track_009_blockers_are_consistent_and_assigned() -> None:
    validate(READINESS, ROOT)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (("claims", "contract_frozen", True), "claims must remain false"),
        (("governance", "repository_panel_output", "independent"), "must remain advisory"),
        (("governance", "owner_disposition", "independent_review"), "cannot be independent"),
    ],
)
def test_readiness_rejects_premature_claims(
    tmp_path: Path, mutation: tuple[str, str, object], message: str
) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    section, field, value = mutation
    document[section][field] = value
    with pytest.raises(Track009ReadinessError, match=message):
        validate(_candidate(tmp_path, document), ROOT)


def test_readiness_rejects_hidden_or_unassigned_issue(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["blocking_data_contract_issues"].pop()
    with pytest.raises(Track009ReadinessError, match="all three"):
        validate(_candidate(tmp_path, document), ROOT)
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["blocking_data_contract_issues"][0]["assigned_role"] = ""
    with pytest.raises(Track009ReadinessError, match="accountable role"):
        validate(_candidate(tmp_path, document), ROOT)


def test_upstream_reconciliation_is_recorded_and_non_activating() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    reconciliation = document["upstream_contract_reconciliation"]
    assert reconciliation["owner_decision_state"] == "recorded_option_A"
    assert reconciliation["recommended_option"] == "A"
    assert document["upstream_dependencies"][1]["state"] == "pending"
    assert document["claims"]["empirical_parameter_activation"] is False
    assert document["claims"]["contract_frozen"] is False


def test_readiness_rejects_upstream_reconciliation_hash_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["upstream_contract_reconciliation"]["decision_packet_sha256"] = "0" * 64
    with pytest.raises(Track009ReadinessError, match="reconciliation evidence hash drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_readiness_rejects_premature_upstream_decision(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["upstream_contract_reconciliation"]["owner_decision_state"] = "pending"
    with pytest.raises(Track009ReadinessError, match="must remain exact and recorded"):
        validate(_candidate(tmp_path, document), ROOT)


def test_exact_candidate_is_synthetic_only_and_unfrozen() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    candidate = document["v0_4_candidate_binding"]
    assert candidate["parameter_count"] == 2
    assert candidate["empirical_parameter_count"] == 0
    assert candidate["status"] == "prepared_not_frozen"
    assert document["contract_freeze_gate"]["state"] == "pending"


def test_readiness_rejects_candidate_hash_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["v0_4_candidate_binding"]["candidate_manifest_sha256"] = "0" * 64
    with pytest.raises(Track009ReadinessError, match="candidate evidence hash drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_resolved_issue_and_freeze_require_evidence(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["blocking_data_contract_issues"][0]["status"] = "resolved"
    with pytest.raises(Track009ReadinessError, match="requires a receipt"):
        validate(_candidate(tmp_path, document), ROOT)
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["contract_freeze_gate"]["state"] = "satisfied"
    with pytest.raises(Track009ReadinessError, match="exact 40-character"):
        validate(_candidate(tmp_path, document), ROOT)
