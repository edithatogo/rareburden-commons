from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_track015_governance_tabletop_candidate import (
    TabletopCandidateError,
    validate,
)

ROOT = Path(__file__).parents[1]
TABLETOP = ROOT / "docs/track-015-governance-tabletop-candidate-2026-08-21.yml"


def _payload() -> dict:
    return yaml.safe_load(TABLETOP.read_text(encoding="utf-8"))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "tabletop.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_tabletop_candidate_covers_all_fail_closed_scenarios() -> None:
    assert validate(TABLETOP, ROOT) == {
        "status": "simulated_tabletop_candidate_valid",
        "scenario_count": 5,
        "owner_disposition_pending": True,
        "external_activation": False,
    }


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("independent_or_human_review", True, "not independent or human"),
        ("public_or_external_activation", True, "cannot activate"),
        ("owner_disposition", {"status": "approved"}, "must remain explicitly pending"),
    ],
)
def test_tabletop_authority_drift_fails_closed(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    payload = _payload()
    payload[field] = value
    with pytest.raises(TabletopCandidateError, match=message):
        validate(_write(tmp_path, payload), ROOT)


def test_unsafe_scenario_recommendation_is_rejected(tmp_path: Path) -> None:
    payload = copy.deepcopy(_payload())
    payload["scenarios"][4]["recommendation"] = "release_as_is"
    with pytest.raises(TabletopCandidateError, match="recommendation drifted"):
        validate(_write(tmp_path, payload), ROOT)
