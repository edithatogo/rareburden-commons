"""Tests for Track 016 reference closeout script and authorization gates."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from scripts.check_track016_reference_closeout import (
    DECISION,
    Track016CloseoutError,
    validate_authorization,
    validate_plan_and_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def test_track016_authorization_passes_on_repository_root() -> None:
    validate_authorization(ROOT)


def test_track016_authorization_fails_closed_on_claim_drift(tmp_path: Path) -> None:
    shutil.copytree(ROOT / "docs", tmp_path / "docs")
    shutil.copytree(ROOT / "manifests", tmp_path / "manifests")
    shutil.copytree(ROOT / "results", tmp_path / "results")
    shutil.copytree(ROOT / "src", tmp_path / "src")

    decision_path = tmp_path / DECISION
    data = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
    data["claims"]["empirical_activation"] = True
    decision_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(Track016CloseoutError, match="authorization scope drift"):
        validate_authorization(tmp_path)


def test_track016_plan_requires_all_tasks_checked(tmp_path: Path) -> None:
    shutil.copytree(ROOT / "conductor", tmp_path / "conductor")
    plan_path = tmp_path / "conductor/tracks/016-security-reliability-operations/plan.md"
    content = plan_path.read_text(encoding="utf-8")
    uncheck = content.replace("- [x]", "- [ ]", 1)
    plan_path.write_text(uncheck, encoding="utf-8")

    with pytest.raises(Track016CloseoutError, match="unchecked tasks"):
        validate_plan_and_registry(tmp_path)
