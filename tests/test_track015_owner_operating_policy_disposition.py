from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_track015_owner_operating_policy_disposition import (
    OwnerPolicyDispositionError,
    validate,
)

ROOT = Path(__file__).parents[1]
DECISION = ROOT / "docs/decisions/2026-08-21-track-015-owner-operating-policy-disposition.yml"


def _payload() -> dict:
    return yaml.safe_load(DECISION.read_text(encoding="utf-8"))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "decision.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_owner_adopts_option_a_without_external_activation() -> None:
    assert validate(DECISION, ROOT) == {
        "status": "bounded_owner_operating_policy_disposition_valid",
        "selected_option": "A",
        "adopted_scope_count": 4,
        "external_activation": False,
    }


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("country_node_activation", True, "activated"),
        ("controlled_data_activation", True, "activated"),
        ("public_or_stable_release_authority", True, "activated"),
        ("third_party_permission", "approved", "cannot be inferred"),
    ],
)
def test_external_or_third_party_overclaim_fails_closed(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    payload = copy.deepcopy(_payload())
    payload["retained_boundaries"][field] = value
    with pytest.raises(OwnerPolicyDispositionError, match=message):
        validate(_write(tmp_path, payload), ROOT)


def test_candidate_hash_drift_fails_closed(tmp_path: Path) -> None:
    payload = _payload()
    payload["exact_candidate"]["operating_policy_sha256"] = "0" * 64
    with pytest.raises(OwnerPolicyDispositionError, match="hash mismatch"):
        validate(_write(tmp_path, payload), ROOT)
