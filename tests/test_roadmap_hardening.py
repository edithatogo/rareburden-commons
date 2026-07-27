from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.roadmap import (
    RoadmapValidationError,
    _dependency_errors,
    _load_json,
    _load_tracks,
    _roadmap_invariant_errors,
    _semver_tuple,
    _track_document_errors,
)
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
TRACK_SCHEMA = load_mapping(ROOT / "schemas" / "track-metadata.schema.json")
BASE_ROADMAP = load_mapping(ROOT / "conductor" / "roadmap.yml")


def test_json_loader_and_semver_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(RoadmapValidationError, match="File not found"):
        _load_json(tmp_path / "missing.json")
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")
    with pytest.raises(RoadmapValidationError, match="Invalid JSON"):
        _load_json(invalid)
    array = tmp_path / "array.json"
    array.write_text("[]", encoding="utf-8")
    with pytest.raises(RoadmapValidationError, match="JSON object"):
        _load_json(array)
    assert _semver_tuple("1.2.3") == (1, 2, 3)
    with pytest.raises(RoadmapValidationError, match="Invalid semantic version"):
        _semver_tuple("v1.2")


def test_track_document_contract_reports_missing_structure(tmp_path: Path) -> None:
    track = tmp_path / "999-fixture"
    track.mkdir()
    metadata = {"id": track.name, "status": "complete"}
    errors = _track_document_errors(track, metadata)
    assert any("spec.md" in error for error in errors)
    assert any("plan.md" in error for error in errors)
    assert any("metadata.json" in error for error in errors)
    assert any("review.md" in error for error in errors)

    (track / "spec.md").write_text("# Fixture\n\n## Objective\n", encoding="utf-8")
    (track / "plan.md").write_text("# Plan\n\nNo tasks.\n", encoding="utf-8")
    (track / "metadata.json").write_text("{}\n", encoding="utf-8")
    errors = _track_document_errors(track, metadata)
    assert any("Acceptance criteria" in error for error in errors)
    assert any("Non-goals" in error for error in errors)
    assert any("at least one task checkbox" in error for error in errors)


def test_dependency_validator_reports_self_unknown_and_cycle() -> None:
    tracks = {
        "001-a": {"dependencies": ["001-a", "999-missing", "002-b"]},
        "002-b": {"dependencies": ["001-a"]},
        "003-c": {"dependencies": []},
    }
    errors = _dependency_errors(tracks)
    joined = "\n".join(errors)
    assert "cannot depend on itself" in joined
    assert "unknown dependency" in joined
    assert "dependency cycle" in joined


def _minimal_metadata(track_id: str) -> dict[str, object]:
    return {
        "id": track_id,
        "title": "Fixture",
        "status": "planned",
        "moscow": "must",
        "target_release": "0.4.0",
        "owner_role": "maintainer",
        "dependencies": [],
        "review_gates": ["engineering"],
        "v1_critical": True,
        "created": "2026-07-19",
        "updated": "2026-07-19",
    }


def test_track_loader_handles_missing_root_unexpected_names_and_bad_metadata(
    tmp_path: Path,
) -> None:
    tracks, errors = _load_tracks(tmp_path / "missing", TRACK_SCHEMA)
    assert tracks == {}
    assert "Track directory not found" in errors[0]

    root = tmp_path / "tracks"
    root.mkdir()
    (root / "bad name").mkdir()
    missing_metadata = root / "999-missing"
    missing_metadata.mkdir()
    invalid_json = root / "998-invalid"
    invalid_json.mkdir()
    (invalid_json / "metadata.json").write_text("{", encoding="utf-8")
    for directory in (invalid_json,):
        (directory / "spec.md").write_text(
            "# Spec\n\n## Objective\n\n## Acceptance criteria\n\n## Non-goals\n",
            encoding="utf-8",
        )
        (directory / "plan.md").write_text("- [ ] Task\n", encoding="utf-8")

    tracks, errors = _load_tracks(root, TRACK_SCHEMA)
    joined = "\n".join(errors)
    assert tracks == {}
    assert "Unexpected track directory name" in joined
    assert "missing required file metadata.json" in joined
    assert "Invalid JSON" in joined


def test_track_loader_reports_id_date_and_duplicate_errors(tmp_path: Path) -> None:
    root = tmp_path / "tracks"
    root.mkdir()
    for directory_name in ("900-first", "901-second"):
        directory = root / directory_name
        directory.mkdir()
        metadata = _minimal_metadata("900-first")
        metadata["created"] = "2026-07-20"
        metadata["updated"] = "2026-07-19"
        (directory / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
        (directory / "spec.md").write_text(
            "# Spec\n\n## Objective\n\n## Acceptance criteria\n\n## Non-goals\n",
            encoding="utf-8",
        )
        (directory / "plan.md").write_text("- [ ] Task\n", encoding="utf-8")

    tracks, errors = _load_tracks(root, TRACK_SCHEMA)
    joined = "\n".join(errors)
    assert "metadata id '900-first' must match directory name" in joined
    assert "Duplicate track id" in joined
    assert "updated date precedes created date" in joined
    assert "900-first" in tracks


def _track(track_id: str, target: str, status: str = "planned") -> dict[str, object]:
    return {
        "id": track_id,
        "title": track_id,
        "target_release": target,
        "status": status,
        "v1_critical": True,
    }


def test_roadmap_invariants_cover_assignment_order_and_release_contracts(tmp_path: Path) -> None:
    roadmap = deepcopy(BASE_ROADMAP)
    tracks = {
        "900-alpha": _track("900-alpha", "0.4.0", "active"),
        "901-beta": _track("901-beta", "0.9.0", "complete"),
        "902-gamma": _track("902-gamma", "0.1.0", "blocked"),
        "903-delta": _track("903-delta", "0.2.0", "archived"),
    }
    roadmap["releases"] = [
        {"version": "0.2.0", "status": "cancelled", "tracks": ["903-delta"]},
        {"version": "0.1.0", "status": "released", "tracks": ["902-gamma", "999-unknown"]},
        {"version": "0.4.0", "status": "current", "tracks": ["900-alpha", "900-alpha"]},
        {"version": "0.4.0", "status": "planned", "tracks": []},
    ]
    roadmap["programme"]["stable_release"] = "1.0.0"
    roadmap["programme"]["roadmap_document"] = "docs/missing-roadmap.md"
    roadmap["programme"]["stable_acceptance_contract"] = "docs/missing-acceptance.md"

    errors = _roadmap_invariant_errors(roadmap, tracks, tmp_path)
    joined = "\n".join(errors)
    assert "Duplicate release versions" in joined
    assert "ordered by semantic version" in joined
    assert "Stable release" in joined
    assert "assigned to multiple releases" in joined
    assert "not assigned" in joined
    assert "unknown track" in joined
    assert "Release statuses must progress" in joined
    assert "released but tracks are not complete" in joined
    assert "complete track targets release" in joined
    assert "active track must target the current release" in joined
    assert "blocked track targets release" in joined
    assert "file does not exist" in joined


def test_roadmap_invariants_handle_non_list_release_collection() -> None:
    assert _roadmap_invariant_errors({"releases": "bad"}, {}, ROOT) == []
