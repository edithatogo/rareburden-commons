"""Tests for Track 017 reference closeout script and authorization gates."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from scripts.check_track017_reference_closeout import (
    DECISION,
    Track017CloseoutError,
    validate_authorization,
    validate_plan_and_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def test_track017_authorization_passes_on_repository_root() -> None:
    validate_authorization(ROOT)


def test_track017_authorization_fails_closed_on_claim_drift(tmp_path: Path) -> None:
    shutil.copytree(ROOT / "docs", tmp_path / "docs")
    shutil.copytree(ROOT / "manifests", tmp_path / "manifests")
    shutil.copytree(ROOT / "results", tmp_path / "results")
    engine = tmp_path / "src/rareburden/demonstrator_adoption.py"
    engine.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "src/rareburden/demonstrator_adoption.py", engine)

    decision_path = tmp_path / DECISION
    data = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
    data["claims"]["empirical_activation"] = True
    decision_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(Track017CloseoutError, match="authorization scope drift"):
        validate_authorization(tmp_path)


def test_track017_plan_requires_all_tasks_checked(tmp_path: Path) -> None:
    shutil.copytree(ROOT / "conductor", tmp_path / "conductor")
    plan_path = tmp_path / "conductor/tracks/017-documentation-adoption-v1/plan.md"
    content = plan_path.read_text(encoding="utf-8")
    uncheck = content.replace("- [x]", "- [ ]", 1)
    plan_path.write_text(uncheck, encoding="utf-8")

    with pytest.raises(Track017CloseoutError, match="unchecked tasks"):
        validate_plan_and_registry(tmp_path)
