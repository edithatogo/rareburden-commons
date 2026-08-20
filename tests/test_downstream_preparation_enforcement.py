from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from scripts.check_downstream_preparation import DownstreamPreparationError, validate

ROOT = Path(__file__).parents[1]
PLAN = ROOT / "docs/downstream-bounded-preparation-plan-2026-08-03.yml"


def test_option_b_contract_passes_for_current_blocked_track_state() -> None:
    validate(PLAN, ROOT)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("freeze_order", ["009", "008", "010"], "freeze_order"),
        ("prohibited_claims", ["release_authority"], "blocked gate"),
        ("tracks", [], "Option B lane"),
    ],
)
def test_option_b_contract_rejects_weakened_boundaries(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    document = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    document[field] = value
    candidate = tmp_path / "plan.yml"
    candidate.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    with pytest.raises(DownstreamPreparationError, match=message):
        validate(candidate, ROOT)


def test_option_b_contract_rejects_out_of_order_track_activation(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    decision = root / "docs" / "decisions" / "2026-08-20-owner-option-b-bounded-preparation.md"
    decision.parent.mkdir(parents=True)
    decision.write_text(
        "Option B\n\nowner-operated governance, not independent review\n", encoding="utf-8"
    )
    plan = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    plan_path = root / "docs" / "plan.yml"
    plan_path.write_text(yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")

    metadata = {
        "002": {"status": "complete"},
        "007": {"status": "complete"},
        "008": {"status": "blocked"},
        "009": {"status": "active"},
        "010": {"status": "blocked"},
    }
    for track, payload in metadata.items():
        directory = root / "conductor" / "tracks" / f"{track}-fixture"
        directory.mkdir(parents=True)
        (directory / "metadata.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(DownstreamPreparationError, match="009 cannot activate"):
        validate(plan_path, root)


def test_archived_dependency_resolves_from_archive(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    decision = root / "docs" / "decisions" / "2026-08-20-owner-option-b-bounded-preparation.md"
    decision.parent.mkdir(parents=True)
    decision.write_text(
        "Option B\n\nowner-operated governance, not independent review\n", encoding="utf-8"
    )
    plan = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    plan_path = root / "docs" / "plan.yml"
    plan_path.write_text(yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
    metadata = {
        "002": ("tracks", {"status": "complete"}),
        "007": ("archive", {"status": "archived"}),
        "008": ("tracks", {"status": "active"}),
        "009": ("tracks", {"status": "blocked"}),
        "010": ("tracks", {"status": "blocked"}),
    }
    for track, (location, payload) in metadata.items():
        directory = root / "conductor" / location / f"{track}-fixture"
        directory.mkdir(parents=True)
        (directory / "metadata.json").write_text(json.dumps(payload), encoding="utf-8")

    validate(plan_path, root)


def test_option_b_contract_rejects_production_security_activation(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(PLAN.read_text(encoding="utf-8")))
    document["cross_cutting_security"]["production_activation"] = "authorized"
    candidate = tmp_path / "plan.yml"
    candidate.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    with pytest.raises(DownstreamPreparationError, match="production security"):
        validate(candidate, ROOT)
