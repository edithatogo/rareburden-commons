"""Reconcile current Conductor projections without executing analysis or using Git."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Keep the documented direct-checkout invocation working without requiring an
# editable install of the package.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from rareburden.roadmap import CHECKBOX_RE  # noqa: E402 - direct checkout bootstrap


def validate(root: Path) -> None:
    """Fail closed on registry, setup-state, navigation or task-state drift."""
    root = root.resolve()
    conductor = root / "conductor"
    tracks: dict[str, tuple[Path, dict]] = {}
    for area in ("tracks", "archive"):
        for path in sorted((conductor / area).glob("*/metadata.json")):
            metadata = json.loads(path.read_text(encoding="utf-8"))
            track_id = metadata["id"]
            if track_id in tracks or path.parent.name != track_id:
                raise ValueError(f"duplicate or mismatched track: {track_id}")
            tracks[track_id] = (path.parent, metadata)
    if not tracks:
        raise ValueError("no tracks found")

    registry: dict[str, list[str]] = {}
    for line in (conductor / "tracks.md").read_text(encoding="utf-8").splitlines():
        if re.match(r"^\| \d{3} \|", line):
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            if len(cells) != 7 or cells[0] in registry:
                raise ValueError("malformed or duplicate registry row")
            registry[cells[0]] = cells
    if set(registry) != {track_id[:3] for track_id in tracks}:
        raise ValueError("registry inventory differs from metadata")

    for track_id, (directory, metadata) in tracks.items():
        row = registry[track_id[:3]]
        status = row[2].split(" (")[0].lower().replace(" ", "_")
        if status != metadata["status"]:
            raise ValueError(f"{track_id}: registry status differs from metadata")
        relative = directory.relative_to(conductor).as_posix()
        if f"](./{relative}/index.md)" not in row[1]:
            raise ValueError(f"{track_id}: registry must link canonical index")
        expected_title = f"[{metadata['title']}](./{relative}/index.md)"
        expected_dependencies = {item[:3] for item in metadata["dependencies"]}
        dependencies = [] if row[6] == "—" else [item.strip() for item in row[6].split(",")]
        if (
            row[1] != expected_title
            or row[3].lower() != metadata["priority"]
            or row[4] != f"v{metadata['target_release']}"
            or row[5] != metadata["owner_role"]
            or len(dependencies) != len(set(dependencies))
            or set(dependencies) != expected_dependencies
        ):
            raise ValueError(f"{track_id}: registry fields differ from metadata")
        index = directory / "index.md"
        if not index.is_file() or not index.read_text(encoding="utf-8").strip():
            raise ValueError(f"{track_id}: missing or empty index")
        text = index.read_text(encoding="utf-8")
        for name in ("spec.md", "plan.md", "metadata.json"):
            target = directory / name
            if f"]({name})" not in text or not target.is_file():
                raise ValueError(f"{track_id}: missing index handshake {name}")
        for link in re.findall(r"\]\(([^)]+)\)", text):
            target = directory / link
            if (
                Path(link).is_absolute()
                or ".." in Path(link).parts
                or not target.resolve().is_relative_to(root)
                or not target.is_file()
                or not target.read_text(encoding="utf-8").strip()
            ):
                raise ValueError(f"{track_id}: unsafe or empty index target {link}")
        if metadata["status"] == "archived" and directory.parent.name != "archive":
            raise ValueError(f"{track_id}: archived status outside archive directory")
        if directory.parent.name == "archive" and metadata["status"] not in {
            "complete",
            "archived",
        }:
            raise ValueError(f"{track_id}: unfinished track in archive directory")
        states = CHECKBOX_RE.findall((directory / "plan.md").read_text(encoding="utf-8"))
        if not states or (
            metadata["status"] == "complete" and any(s.lower() != "x" for s in states)
        ):
            raise ValueError(f"{track_id}: missing or incomplete tasks")
        if metadata["status"] == "planned" and "~" in states:
            raise ValueError(f"{track_id}: planned track has in-progress tasks")

    setup = json.loads((conductor / "setup_state.json").read_text(encoding="utf-8"))
    # Legacy completed_tracks includes archived lifecycle records; archived_tracks
    # is a location inventory, including bounded-complete Track 015. Keep both
    # meanings explicit instead of treating archive location as a status change.
    expected = {
        "completed_tracks": {
            i for i, (_, m) in tracks.items() if m["status"] in {"complete", "archived"}
        },
        "archived_tracks": {i for i, (p, _) in tracks.items() if p.parent.name == "archive"},
    }
    for field, status in (
        ("active_tracks", "active"),
        ("ready_tracks", "ready"),
        ("blocked_tracks", "blocked"),
        ("planned_tracks", "planned"),
        ("in_review_tracks", "in_review"),
        ("proposed_tracks", "proposed"),
    ):
        expected[field] = {i for i, (_, m) in tracks.items() if m["status"] == status}
    for field, values in expected.items():
        actual = setup.get(field)
        if not isinstance(actual, list) or any(not isinstance(i, str) for i in actual):
            raise ValueError(f"setup state {field}: expected a string list")
        if len(actual) != len(set(actual)) or set(actual) != values:
            raise ValueError(f"setup state {field}: differs from canonical tracks")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    validate(args.root)
    print("Conductor registry, setup state, indexes and task states agree")


if __name__ == "__main__":
    main()
