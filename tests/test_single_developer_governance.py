from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_single_developer_governance import GovernanceContractError, validate

ROOT = Path(__file__).parents[1]
CONTRACT = ROOT / "docs/single-developer-governance.yml"


def _candidate(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "governance.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_repository_uses_single_owner_agent_advice_model() -> None:
    validate(CONTRACT, ROOT)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (("owner", "holds_all_accountable_repository_roles", False), "all accountable roles"),
        (("agent_advice", "status", "approval"), "advisory perspectives"),
        (
            ("independence_boundary", "owner_or_agent_work_is_independent_review", True),
            "fail closed",
        ),
    ],
)
def test_rejects_authority_drift(
    tmp_path: Path, mutation: tuple[str, str, object], message: str
) -> None:
    document = copy.deepcopy(yaml.safe_load(CONTRACT.read_text(encoding="utf-8")))
    section, field, value = mutation
    document[section][field] = value
    with pytest.raises(GovernanceContractError, match=message):
        validate(_candidate(tmp_path, document), ROOT)


def test_rejects_incomplete_advice_format(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(CONTRACT.read_text(encoding="utf-8")))
    document["agent_advice"]["required_presentation"].remove("contingencies")
    with pytest.raises(GovernanceContractError, match="all five presentation fields"):
        validate(_candidate(tmp_path, document), ROOT)


def test_rejects_remuneration_claim(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(CONTRACT.read_text(encoding="utf-8")))
    document["remuneration"]["amount"] = 1
    with pytest.raises(GovernanceContractError, match="remuneration must remain zero"):
        validate(_candidate(tmp_path, document), ROOT)


def test_rejects_incomplete_grouped_decision(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(CONTRACT.read_text(encoding="utf-8")))
    del document["decision_groups"][0]["trade_offs"]
    with pytest.raises(GovernanceContractError, match="complete owner advice format"):
        validate(_candidate(tmp_path, document), ROOT)
