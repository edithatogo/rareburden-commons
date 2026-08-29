from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from rareburden.roadmap import RoadmapValidationError, validate_roadmap_files

ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "conductor" / "roadmap.yml"
ROADMAP_SCHEMA = ROOT / "schemas" / "roadmap.schema.json"
TRACKS = ROOT / "conductor" / "tracks"
TRACK_SCHEMA = ROOT / "schemas" / "track-metadata.schema.json"


def validate_with(tracks: Path, roadmap: Path = ROADMAP) -> None:
    validate_roadmap_files(roadmap, ROADMAP_SCHEMA, tracks, TRACK_SCHEMA)


def test_seed_roadmap_is_valid() -> None:
    summary = validate_roadmap_files(ROADMAP, ROADMAP_SCHEMA, TRACKS, TRACK_SCHEMA)
    assert summary.release_count == 11
    assert summary.track_count == 19
    assert summary.v1_critical_track_count == 18
    assert summary.current_release == "0.3.0"
    assert summary.track_status_counts["complete"] == 4
    assert summary.track_status_counts["archived"] == 5


def test_dependency_cycle_is_rejected(tmp_path: Path) -> None:
    tracks = tmp_path / "tracks"
    shutil.copytree(TRACKS, tracks)
    archive = tmp_path / "archive"
    shutil.copytree(ROOT / "conductor" / "archive", archive)
    metadata_path = archive / "001-foundation" / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["dependencies"] = ["017-documentation-adoption-v1"]
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(RoadmapValidationError, match="dependency cycle"):
        validate_with(tracks)


def test_missing_track_document_is_rejected(tmp_path: Path) -> None:
    tracks = tmp_path / "tracks"
    shutil.copytree(TRACKS, tracks)
    archive = tmp_path / "archive"
    shutil.copytree(ROOT / "conductor" / "archive", archive)
    (archive / "002-public-source-acquisition" / "spec.md").unlink()

    with pytest.raises(RoadmapValidationError, match=r"missing required file spec\.md"):
        validate_with(tracks)


def test_duplicate_release_assignment_is_rejected(tmp_path: Path) -> None:
    roadmap_data = yaml.safe_load(ROADMAP.read_text(encoding="utf-8"))
    roadmap_data["releases"][3]["tracks"].append("007-landscape-novelty")
    roadmap = tmp_path / "roadmap.yml"
    roadmap.write_text(yaml.safe_dump(roadmap_data, sort_keys=False), encoding="utf-8")

    with pytest.raises(RoadmapValidationError, match="assigned to multiple releases"):
        validate_roadmap_files(roadmap, ROADMAP_SCHEMA, TRACKS, TRACK_SCHEMA)


def test_complete_track_with_unchecked_task_is_rejected(tmp_path: Path) -> None:
    tracks = tmp_path / "tracks"
    shutil.copytree(TRACKS, tracks)
    archive = tmp_path / "archive"
    shutil.copytree(ROOT / "conductor" / "archive", archive)
    track_dir = archive / "006-v1-delivery-system"
    metadata_path = track_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["status"] = "complete"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    plan_path = track_dir / "plan.md"
    plan = plan_path.read_text(encoding="utf-8").replace("- [x]", "- [ ]", 1)
    plan_path.write_text(plan, encoding="utf-8")

    with pytest.raises(RoadmapValidationError, match="complete track has unchecked"):
        validate_with(tracks)


def test_human_roadmap_track_drift_is_rejected(tmp_path: Path) -> None:
    shutil.copytree(ROOT / "conductor", tmp_path / "conductor")
    shutil.copytree(ROOT / "docs", tmp_path / "docs")
    roadmap = tmp_path / "conductor" / "roadmap.yml"
    tracks = tmp_path / "conductor" / "tracks"
    document = tmp_path / "docs" / "roadmap-v1.md"
    text = document.read_text(encoding="utf-8").replace(
        "006-v1-delivery-system — v1 delivery system and foundation hardening",
        "006-v1-delivery-system — stale title",
        1,
    )
    document.write_text(text, encoding="utf-8")

    with pytest.raises(
        RoadmapValidationError,
        match="human roadmap missing canonical track reference",
    ):
        validate_roadmap_files(roadmap, ROADMAP_SCHEMA, tracks, TRACK_SCHEMA)


def test_archived_track_may_target_current_release(tmp_path: Path) -> None:
    tracks = tmp_path / "tracks"
    shutil.copytree(TRACKS, tracks)
    shutil.copytree(ROOT / "conductor" / "archive", tmp_path / "archive")

    validate_with(tracks)


def test_complete_track_may_be_preserved_in_archive_before_planned_release() -> None:
    summary = validate_roadmap_files(ROADMAP, ROADMAP_SCHEMA, TRACKS, TRACK_SCHEMA)

    assert summary.track_status_counts["complete"] == 4
    assert (ROOT / "conductor/archive/015-governance-partnership-policy/spec.md").is_file()


def test_released_release_requires_complete_tracks(tmp_path: Path) -> None:
    roadmap_data = yaml.safe_load(ROADMAP.read_text(encoding="utf-8"))
    roadmap_data["releases"][2]["status"] = "released"
    roadmap_data["releases"][3]["status"] = "released"
    roadmap_data["releases"][4]["status"] = "released"
    roadmap_data["releases"][5]["status"] = "current"
    shutil.copytree(ROOT / "docs", tmp_path / "docs")
    roadmap = tmp_path / "conductor" / "roadmap.yml"
    roadmap.parent.mkdir()
    roadmap.write_text(yaml.safe_dump(roadmap_data, sort_keys=False), encoding="utf-8")

    with pytest.raises(RoadmapValidationError, match="released but tracks are not complete"):
        validate_roadmap_files(roadmap, ROADMAP_SCHEMA, TRACKS, TRACK_SCHEMA)


def test_release_status_regression_is_rejected(tmp_path: Path) -> None:
    roadmap_data = yaml.safe_load(ROADMAP.read_text(encoding="utf-8"))
    roadmap_data["releases"][3]["status"] = "released"
    roadmap = tmp_path / "roadmap.yml"
    roadmap.write_text(yaml.safe_dump(roadmap_data, sort_keys=False), encoding="utf-8")

    with pytest.raises(RoadmapValidationError, match="Release statuses must progress"):
        validate_roadmap_files(roadmap, ROADMAP_SCHEMA, TRACKS, TRACK_SCHEMA)
