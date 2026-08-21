from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_track015_repository_closeout import Track015CloseoutError, validate

ROOT = Path(__file__).parents[1]
PARTNERSHIP = ROOT / "docs/track-015-partnership-sustainability-map-2026-08-21.yml"
TABLETOP = ROOT / "docs/track-015-policy-user-tabletop-2026-08-21.yml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_bounded_repository_closeout_is_valid() -> None:
    assert validate(PARTNERSHIP, TABLETOP, ROOT) == {
        "status": "track_015_bounded_repository_closeout_valid",
        "target_count": 6,
        "scenario_count": 5,
        "external_activation": False,
        "annual_cash_budget": 0,
    }


def test_relationship_overclaim_fails_closed(tmp_path: Path) -> None:
    payload = _load(PARTNERSHIP)
    payload["relationship_state"] = "confirmed_partner"
    with pytest.raises(Track015CloseoutError, match="overclaims"):
        validate(_write(tmp_path, "partnership.yml", payload), TABLETOP, ROOT)


@pytest.mark.parametrize("field", ["global_claim", "representativeness_claim"])
def test_global_claim_overreach_fails_closed(tmp_path: Path, field: str) -> None:
    payload = copy.deepcopy(_load(TABLETOP))
    payload["geographic_claim_disposition"][field] = "approved"
    with pytest.raises(Track015CloseoutError, match="not bounded"):
        validate(PARTNERSHIP, _write(tmp_path, "tabletop.yml", payload), ROOT)


def test_external_activation_fails_closed(tmp_path: Path) -> None:
    payload = _load(TABLETOP)
    payload["public_or_external_activation"] = True
    with pytest.raises(Track015CloseoutError, match="cannot activate"):
        validate(PARTNERSHIP, _write(tmp_path, "tabletop.yml", payload), ROOT)
