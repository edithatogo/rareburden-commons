from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_track_016_production_release_readiness import Track016ReadinessError, validate

ROOT = Path(__file__).parents[1]
READINESS = ROOT / "docs/track-016-production-release-readiness-2026-08-21.yml"


def _candidate(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "readiness.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_current_track_016_readiness_is_consistent() -> None:
    validate(READINESS, ROOT)


@pytest.mark.parametrize(
    ("section", "field", "value", "message"),
    [
        ("claims", "release_authorized", True, "claims must remain false"),
        ("governance", "repository_panel_output", "independent", "must remain advisory"),
        ("governance", "production_operations", "enabled", "production must remain disabled"),
        ("candidate_input", "exact_release_candidate", True, "cannot be promoted"),
    ],
)
def test_rejects_premature_claims(
    tmp_path: Path, section: str, field: str, value: object, message: str
) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document[section][field] = value
    with pytest.raises(Track016ReadinessError, match=message):
        validate(_candidate(tmp_path, document), ROOT)


def test_rejects_unexercised_backup_handoff(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["backup_owner_handoff"]["state"] = "satisfied"
    with pytest.raises(Track016ReadinessError, match="scoped, expiring exercised receipt"):
        validate(_candidate(tmp_path, document), ROOT)


def test_rejects_non_independent_security_receipt(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    gate = document["qualifying_reviews"]["independent_security"]
    gate.update(
        {
            "state": "satisfied",
            "receipt_locator": "private-register:security-1",
            "exact_candidate_commit": "a" * 40,
            "exact_candidate_tree": "b" * 40,
        }
    )
    with pytest.raises(Track016ReadinessError, match="reviewer independence"):
        validate(_candidate(tmp_path, document), ROOT)


def test_rejects_evidence_hash_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["candidate_input"]["evidence"][0]["sha256"] = "0" * 64
    with pytest.raises(Track016ReadinessError, match="hash drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_owner_disposition_is_exact_bounded_and_not_release_authority() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    disposition = document["exact_candidate_owner_disposition"]
    assert disposition["state"] == "satisfied"
    assert disposition["authority_model"] == "owner_operated_not_independent_review"
    assert disposition["exact_candidate_commit"] == "fb4a0443fa207e13d15fbf326d46bf5df56f0ab5"
    assert disposition["exact_candidate_tree"] == "7694ec20137fbac76ebf2a72df863f244caeafb8"
    assert document["claims"]["exact_candidate_owner_disposed"] is True
    assert document["claims"]["release_authorized"] is False


def test_rejects_owner_disposition_claim_mismatch(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["claims"]["exact_candidate_owner_disposed"] = False
    with pytest.raises(Track016ReadinessError, match="claim must match"):
        validate(_candidate(tmp_path, document), ROOT)
