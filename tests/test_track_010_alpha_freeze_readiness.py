from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_track_010_alpha_freeze_readiness import Track010ReadinessError, validate

ROOT = Path(__file__).parents[1]
READINESS = ROOT / "docs/track-010-alpha-freeze-readiness-2026-08-21.yml"


def _candidate(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "readiness.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_current_track_010_blockers_are_consistent() -> None:
    validate(READINESS, ROOT)


@pytest.mark.parametrize(
    ("section", "field", "value", "message"),
    [
        ("claims", "alpha_interface_frozen", True, "claims must remain false"),
        ("review_gate", "repository_panel_status", "independent", "must remain advisory"),
        ("review_gate", "owner_status", "independent_review", "cannot be independent"),
    ],
)
def test_readiness_rejects_premature_or_mislabelled_claims(
    tmp_path: Path, section: str, field: str, value: object, message: str
) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document[section][field] = value
    with pytest.raises(Track010ReadinessError, match=message):
        validate(_candidate(tmp_path, document), ROOT)


def test_satisfied_review_requires_independent_and_accountable_receipts(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["review_gate"]["state"] = "satisfied"
    with pytest.raises(Track010ReadinessError, match="every accountable receipt"):
        validate(_candidate(tmp_path, document), ROOT)


def test_upstream_reconciliation_is_recorded_and_non_activating() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    reconciliation = document["upstream_contract_reconciliation"]
    assert reconciliation["owner_decision_state"] == "recorded_option_A"
    assert reconciliation["recommended_option"] == "A"
    assert document["upstream_dependency"]["state"] == "pending"
    assert document["claims"]["alpha_interface_frozen"] is False
    assert document["claims"]["empirical_or_production_activation"] is False


def test_readiness_rejects_upstream_reconciliation_hash_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["upstream_contract_reconciliation"]["decision_packet_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="reconciliation evidence hash drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_readiness_rejects_premature_upstream_decision(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["upstream_contract_reconciliation"]["owner_decision_state"] = "pending"
    with pytest.raises(Track010ReadinessError, match="must remain exact and recorded"):
        validate(_candidate(tmp_path, document), ROOT)


def test_exact_alpha_candidate_is_synthetic_only_and_unfrozen() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    candidate = document["alpha_candidate_binding"]
    assert candidate["empirical_parameter_count"] == 0
    assert candidate["status"] == "prepared_not_frozen"
    assert document["alpha_freeze_gate"]["state"] == "pending"
    assert document["claims"]["alpha_interface_frozen"] is False


def test_readiness_rejects_alpha_candidate_hash_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["alpha_candidate_binding"]["candidate_manifest_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="candidate evidence hash drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_final_disposition_records_exact_option_a_deferral() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    disposition = document["final_owner_disposition_candidate"]
    assert disposition["exact_candidate_commit"] == ("68a1d31c623161a323d90f2b2de95d3b1a11a1a3")
    assert disposition["recommended_option"] == "A"
    assert disposition["owner_decision_state"] == "recorded_option_A"
    assert document["review_gate"]["state"] == "pending"
    assert document["alpha_freeze_gate"]["state"] == "pending"


def test_readiness_rejects_final_disposition_hash_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["final_owner_disposition_candidate"]["decision_packet_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="disposition packet hash drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_alpha_freeze_requires_exact_candidate_binding(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["alpha_freeze_gate"]["state"] = "satisfied"
    with pytest.raises(Track010ReadinessError, match="exact 40-character"):
        validate(_candidate(tmp_path, document), ROOT)
