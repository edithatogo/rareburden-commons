from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from scripts.sync_validation_artifacts import (
    REPORTS,
    ValidationArtifactError,
    check,
    sync,
)


def _fixture(tmp_path: Path) -> Path:
    root = tmp_path
    (root / "docs").mkdir()
    for name in REPORTS:
        (root / name).write_text(f"report:{name}\n", encoding="utf-8")
    artifacts = [{"path": name, "sha256": "0" * 64, "size_bytes": 0} for name in REPORTS]
    manifest = {
        "repository": {"commit": None, "tree_state": "dirty", "tag": "candidate"},
        "artefacts": deepcopy(artifacts),
        "summary": {"artefact_count": 0, "artefact_bytes": 0, "material_count": 0},
    }
    report = {"source_commit": "pending", "artifacts": deepcopy(artifacts)}
    reconciliation = {"artifacts": deepcopy(artifacts)}
    for name, document in (
        ("release-manifest-candidate-2026-08-03.yml", manifest),
        ("validation-report-artifacts-2026-08-03.yml", report),
        ("release-candidate-evidence-reconciliation-2026-08-04.yml", reconciliation),
    ):
        (root / "docs" / name).write_text(yaml.safe_dump(document), encoding="utf-8")
    return root


def test_sync_binds_all_reports_and_exact_commit(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    commit = "a" * 40
    sync(root, commit=commit)
    check(root)
    manifest = yaml.safe_load((root / "docs/release-manifest-candidate-2026-08-03.yml").read_text())
    assert manifest["repository"] == {
        "commit": commit,
        "tree_state": "clean",
        "tag": "candidate",
    }
    assert manifest["summary"]["artefact_count"] == 4
    assert manifest["summary"]["artefact_bytes"] > 0


def test_check_fails_closed_when_a_tracked_report_changes(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    sync(root, commit="b" * 40)
    (root / "junit.xml").write_text("changed\n", encoding="utf-8")
    with pytest.raises(ValidationArtifactError, match=r"drift detected: junit\.xml"):
        check(root)
