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


def test_synthetic_candidate_does_not_satisfy_dependency_or_alpha_freeze() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    candidate = document["synthetic_candidate_preparation"]
    assert candidate["status"] == "prepared_synthetic_only_not_alpha_not_frozen"
    assert document["upstream_dependency"]["state"] == "satisfied"
    assert document["review_gate"]["state"] == "pending"
    assert document["alpha_freeze_gate"]["state"] == "pending"
    assert set(document["claims"].values()) == {False}


def test_track009_dependency_requires_exact_bounded_completion(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["upstream_dependency"]["completion_decision_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="completion binding drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_synthetic_candidate_rejects_manifest_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["synthetic_candidate_preparation"]["candidate_manifest_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="candidate evidence drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_bounded_owner_disposition_rejects_receipt_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["bounded_owner_disposition"]["decision_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="receipt hash drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_repository_advisory_packet_remains_pending_and_blocking(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    review = document["review_gate"]
    assert review["repository_recommendation"] == "revise"
    assert review["repository_owner_decision"] == "pending"
    assert len(review["unresolved_blocking_findings"]) == 3
    review["repository_owner_decision"] = "recorded"
    with pytest.raises(Track010ReadinessError, match="pending decision drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_repository_advisory_packet_rejects_hash_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["review_gate"]["repository_advisory_packet_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="packet binding drift"):
        validate(_candidate(tmp_path, document), ROOT)


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


def test_alpha_freeze_requires_exact_candidate_binding(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["alpha_freeze_gate"]["state"] = "satisfied"
    with pytest.raises(Track010ReadinessError, match="exact 40-character"):
        validate(_candidate(tmp_path, document), ROOT)
