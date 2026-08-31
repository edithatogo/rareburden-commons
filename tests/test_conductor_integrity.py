"""Regression coverage for status drift missed by historical roadmap checks."""

import json
import shutil
from pathlib import Path

import pytest

from rareburden.roadmap import _track_document_errors
from scripts.check_conductor_integrity import validate

ROOT = Path(__file__).resolve().parents[1]
TRACK = "003-monogenic-diabetes-demonstrator"


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    shutil.copytree(ROOT / "conductor", tmp_path / "conductor")
    return tmp_path


def test_repository_integrity() -> None:
    validate(ROOT)


@pytest.mark.parametrize(
    "field",
    [
        "completed_tracks",
        "active_tracks",
        "archived_tracks",
        "ready_tracks",
        "planned_tracks",
        "blocked_tracks",
    ],
)
def test_reject_setup_projection_drift(repository: Path, field: str) -> None:
    path = repository / "conductor/setup_state.json"
    state = json.loads(path.read_text())
    state[field].append("999-unrecorded")
    path.write_text(json.dumps(state))
    with pytest.raises(ValueError, match="setup state"):
        validate(repository)


@pytest.mark.parametrize("change", ["status", "duplicate", "missing", "index"])
def test_reject_registry_drift(repository: Path, change: str) -> None:
    path = repository / "conductor/tracks.md"
    text = path.read_text()
    row = next(line for line in text.splitlines() if line.startswith("| 003 |"))
    replacement = {
        "status": row.replace("Complete", "Blocked"),
        "duplicate": row + "\n" + row,
        "missing": "",
        "index": row.replace("/index.md", "/spec.md"),
    }[change]
    path.write_text(text.replace(row, replacement))
    with pytest.raises(ValueError, match="registry"):
        validate(repository)


@pytest.mark.parametrize("change", ["missing", "empty", "handshake", "escape"])
def test_reject_invalid_index(repository: Path, change: str) -> None:
    path = repository / "conductor/tracks" / TRACK / "index.md"
    if change == "missing":
        path.unlink()
    elif change == "empty":
        path.write_text("")
    elif change == "handshake":
        path.write_text(path.read_text().replace("](spec.md)", "](absent.md)"))
    else:
        path.write_text(path.read_text() + "\n[escape](../../../outside.md)\n")
    with pytest.raises(ValueError, match="index"):
        validate(repository)


@pytest.mark.parametrize("status,mark", [("complete", "~"), ("complete", " "), ("planned", "~")])
def test_roadmap_rejects_task_state_mismatch(tmp_path: Path, status: str, mark: str) -> None:
    (tmp_path / "plan.md").write_text(f"- [x] Parent\n  - [{mark}] Child\n")
    errors = _track_document_errors(tmp_path, {"id": "fixture", "status": status})
    assert any("plan tasks" in error for error in errors)


@pytest.mark.parametrize("change", ["duplicate", "type", "item"])
def test_reject_malformed_setup(repository: Path, change: str) -> None:
    path = repository / "conductor/setup_state.json"
    state = json.loads(path.read_text())
    values = state["completed_tracks"]
    state["completed_tracks"] = {"duplicate": values + values[:1], "type": {}, "item": [False]}[
        change
    ]
    path.write_text(json.dumps(state))
    with pytest.raises(ValueError, match="setup state"):
        validate(repository)


@pytest.mark.parametrize("status,mark", [("complete", "~"), ("planned", "~"), ("complete", " ")])
def test_integrity_rejects_incomplete_plan(repository: Path, status: str, mark: str) -> None:
    directory = repository / "conductor/tracks" / TRACK
    metadata = json.loads((directory / "metadata.json").read_text())
    metadata["status"] = status
    (directory / "metadata.json").write_text(json.dumps(metadata))
    (directory / "plan.md").write_text(f"- [{mark}] Task\n")
    registry = repository / "conductor/tracks.md"
    text = registry.read_text()
    row = next(line for line in text.splitlines() if line.startswith("| 003 |"))
    registry.write_text(text.replace(row, row.replace("Complete", status.title())))
    with pytest.raises(ValueError, match="tasks"):
        validate(repository)


def test_reject_missing_tracks(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no tracks"):
        validate(tmp_path)


def test_reject_metadata_identity_drift(repository: Path) -> None:
    path = repository / "conductor/tracks" / TRACK / "metadata.json"
    metadata = json.loads(path.read_text())
    metadata["id"] = "999-wrong"
    path.write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match="mismatched track"):
        validate(repository)


def test_cli(
    repository: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    from scripts.check_conductor_integrity import main

    monkeypatch.setattr("sys.argv", ["check", "--root", str(repository)])
    main()
    assert "agree" in capsys.readouterr().out


@pytest.mark.parametrize(
    "column,value",
    [
        (1, "wrong-title"),
        (3, "Should"),
        (4, "v9.9.9"),
        (5, "Different owner"),
        (6, "008, 009"),
        (6, "008, 009, 010, 010"),
    ],
)
def test_reject_remaining_registry_field_drift(repository: Path, column: int, value: str) -> None:
    path = repository / "conductor/tracks.md"
    text = path.read_text()
    row = next(line for line in text.splitlines() if line.startswith("| 003 |"))
    cells = [cell.strip() for cell in row.split("|")[1:-1]]
    if column == 1:
        cells[column] = cells[column].replace("Monogenic diabetes", value)
    else:
        cells[column] = value
    path.write_text(text.replace(row, "| " + " | ".join(cells) + " |"))
    with pytest.raises(ValueError, match="registry fields"):
        validate(repository)


@pytest.mark.parametrize("status", ["in_review", "proposed"])
def test_lifecycle_transitions_require_setup_inventory(repository: Path, status: str) -> None:
    directory = repository / "conductor/tracks" / TRACK
    metadata = json.loads((directory / "metadata.json").read_text())
    metadata["status"] = status
    (directory / "metadata.json").write_text(json.dumps(metadata))
    registry = repository / "conductor/tracks.md"
    text = registry.read_text()
    row = next(line for line in text.splitlines() if line.startswith("| 003 |"))
    registry.write_text(
        text.replace(row, row.replace("Complete", status.replace("_", " ").title()))
    )
    setup = repository / "conductor/setup_state.json"
    state = json.loads(setup.read_text())
    state["completed_tracks"].remove(TRACK)
    setup.write_text(json.dumps(state))
    with pytest.raises(ValueError, match=f"{status}_tracks"):
        validate(repository)
    state[f"{status}_tracks"].append(TRACK)
    setup.write_text(json.dumps(state))
    validate(repository)
