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


def test_alpha_freeze_requires_exact_candidate_binding(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["alpha_freeze_gate"]["state"] = "satisfied"
    with pytest.raises(Track010ReadinessError, match="exact 40-character"):
        validate(_candidate(tmp_path, document), ROOT)
