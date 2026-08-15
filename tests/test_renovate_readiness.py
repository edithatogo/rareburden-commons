from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_renovate_readiness import RenovateReadinessError, validate_renovate_readiness

ROOT = Path(__file__).resolve().parents[1]


def _write_root(tmp_path: Path, config: dict) -> Path:
    (tmp_path / ".github").mkdir()
    (tmp_path / "renovate.json").write_text(json.dumps(config), encoding="utf-8")
    return tmp_path


def _valid_config() -> dict:
    return {
        "extends": ["github>edithatogo/renovate-config"],
        "dependencyDashboard": True,
        "prConcurrentLimit": 5,
        "prHourlyLimit": 2,
        "schedule": ["before 6am on monday"],
    }


def test_repository_renovate_configuration_is_ready_but_not_execution_evidence() -> None:
    result = validate_renovate_readiness(ROOT)
    assert result["status"] == "repository_configuration_ready"
    assert result["hosted_app_execution_observed"] is False


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("extends", [], "preset"),
        ("dependencyDashboard", False, "Dashboard"),
        ("prConcurrentLimit", 20, "limits"),
        ("prHourlyLimit", 20, "limits"),
        ("schedule", [], "schedule"),
    ],
)
def test_readiness_fails_closed_on_configuration_drift(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    config = _valid_config()
    config[field] = value
    with pytest.raises(RenovateReadinessError, match=message):
        validate_renovate_readiness(_write_root(tmp_path, config))


def test_readiness_rejects_competing_dependabot(tmp_path: Path) -> None:
    root = _write_root(tmp_path, _valid_config())
    (root / ".github" / "dependabot.yml").write_text("version: 2\n", encoding="utf-8")
    with pytest.raises(RenovateReadinessError, match="compete"):
        validate_renovate_readiness(root)
