from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_track015_operating_policy_candidate import OperatingPolicyError, validate

ROOT = Path(__file__).parents[1]
POLICY = ROOT / "docs/track-015-operating-policy-candidate-2026-08-21.yml"


def _payload() -> dict:
    return yaml.safe_load(POLICY.read_text(encoding="utf-8"))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "policy.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_candidate_is_bounded_and_pending_owner_disposition() -> None:
    assert validate(POLICY) == {
        "status": "bounded_operating_policy_candidate_valid",
        "prohibited_use_count": 4,
        "country_node_activation_requirement_count": 5,
        "owner_disposition_pending": True,
    }


@pytest.mark.parametrize(
    ("section", "field", "value", "message"),
    [
        ("scope", "controlled_or_third_party_inputs", "enabled", "fail closed"),
        ("scope", "authority_for_unrelated_communities_or_nodes", "claimed", "cannot be claimed"),
        ("funder_independence", "funder_veto", "allowed", "must remain prohibited"),
        (
            "complaints_and_appeals",
            "independence_claim",
            True,
            "cannot be described as independent",
        ),
        ("country_node", "default_state", "active", "must remain fail closed"),
    ],
)
def test_unsafe_policy_drift_fails_closed(
    tmp_path: Path, section: str, field: str, value: object, message: str
) -> None:
    payload = copy.deepcopy(_payload())
    payload[section][field] = value
    with pytest.raises(OperatingPolicyError, match=message):
        validate(_write(tmp_path, payload))


def test_remuneration_and_human_review_cannot_be_reintroduced(tmp_path: Path) -> None:
    payload = _payload()
    payload["remuneration"] = {"model": "paid", "amount": 1}
    with pytest.raises(OperatingPolicyError, match="must remain unpaid"):
        validate(_write(tmp_path, payload))
    payload = _payload()
    payload["human_review_required"] = True
    with pytest.raises(OperatingPolicyError, match="not a repository gate"):
        validate(_write(tmp_path, payload))
