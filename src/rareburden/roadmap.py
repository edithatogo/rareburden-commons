"""Validate the RareBurden Conductor roadmap and track graph."""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .catalog import load_schema, load_yaml

TRACK_ID_RE = re.compile(r"^[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
CHECKBOX_RE = re.compile(r"^- \[(?P<state>[ xX])\] ", re.MULTILINE)


class RoadmapValidationError(ValueError):
    """Raised when roadmap or Conductor track metadata are inconsistent."""


@dataclass(frozen=True)
class RoadmapSummary:
    """Stable summary of the validated programme roadmap."""

    release_count: int
    track_count: int
    v1_critical_track_count: int
    current_release: str
    track_status_counts: dict[str, int]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RoadmapValidationError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RoadmapValidationError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RoadmapValidationError(f"Expected a JSON object at the root of {path}")
    return data


def _schema_errors(data: dict[str, Any], schema: dict[str, Any], label: str) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{label}.{location}: {error.message}")
    return errors


def _semver_tuple(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.fullmatch(version)
    if not match:
        raise RoadmapValidationError(f"Invalid semantic version: {version}")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def _track_document_errors(track_dir: Path, metadata: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    track_id = metadata.get("id", track_dir.name)
    required = ("spec.md", "plan.md", "metadata.json")
    for name in required:
        if not (track_dir / name).is_file():
            errors.append(f"{track_id}: missing required file {name}")

    spec_path = track_dir / "spec.md"
    if spec_path.is_file():
        spec = spec_path.read_text(encoding="utf-8")
        for heading in ("## Objective", "## Acceptance criteria", "## Non-goals"):
            if heading not in spec:
                errors.append(f"{track_id}.spec.md: missing heading {heading!r}")

    plan_path = track_dir / "plan.md"
    if plan_path.is_file():
        plan = plan_path.read_text(encoding="utf-8")
        states = [match.group("state").lower() for match in CHECKBOX_RE.finditer(plan)]
        if not states:
            errors.append(f"{track_id}.plan.md: must contain at least one task checkbox")
        if metadata.get("status") == "complete" and any(state == " " for state in states):
            errors.append(f"{track_id}: complete track has unchecked plan tasks")

    if metadata.get("status") == "complete" and not (track_dir / "review.md").is_file():
        errors.append(f"{track_id}: complete track must contain review.md")

    return errors


def _dependency_errors(tracks: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for track_id, metadata in tracks.items():
        for dependency in metadata.get("dependencies", []):
            if dependency == track_id:
                errors.append(f"{track_id}: cannot depend on itself")
            elif dependency not in tracks:
                errors.append(f"{track_id}: unknown dependency {dependency}")

    state: dict[str, int] = dict.fromkeys(tracks, 0)
    stack: list[str] = []

    def visit(track_id: str) -> None:
        if state[track_id] == 2:
            return
        if state[track_id] == 1:
            start = stack.index(track_id)
            cycle = [*stack[start:], track_id]
            errors.append(f"dependency cycle: {' -> '.join(cycle)}")
            return
        state[track_id] = 1
        stack.append(track_id)
        for dependency in tracks[track_id].get("dependencies", []):
            if dependency in tracks:
                visit(dependency)
        stack.pop()
        state[track_id] = 2

    for track_id in sorted(tracks):
        visit(track_id)
    return errors


def _load_tracks(
    tracks_root: Path,
    track_schema: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    tracks: dict[str, dict[str, Any]] = {}

    if not tracks_root.is_dir():
        return tracks, [f"Track directory not found: {tracks_root}"]

    roots = [tracks_root]
    archive_root = tracks_root.parent / "archive"
    if archive_root.is_dir():
        roots.append(archive_root)
    track_dirs = sorted(
        path
        for root in roots
        for path in root.iterdir()
        if path.is_dir() and path.name != "README.md"
    )
    for track_dir in track_dirs:
        if not TRACK_ID_RE.fullmatch(track_dir.name):
            errors.append(f"Unexpected track directory name: {track_dir.name}")
            continue
        metadata_path = track_dir / "metadata.json"
        if not metadata_path.is_file():
            errors.append(f"{track_dir.name}: missing required file metadata.json")
            continue
        try:
            metadata = _load_json(metadata_path)
        except RoadmapValidationError as exc:
            errors.append(str(exc))
            continue

        errors.extend(_schema_errors(metadata, track_schema, track_dir.name))
        track_id = metadata.get("id")
        if track_id != track_dir.name:
            errors.append(f"{track_dir.name}: metadata id {track_id!r} must match directory name")
        if isinstance(track_id, str):
            if track_id in tracks:
                errors.append(f"Duplicate track id: {track_id}")
            else:
                tracks[track_id] = metadata

        created = metadata.get("created")
        updated = metadata.get("updated")
        if isinstance(created, str) and isinstance(updated, str):
            try:
                if date.fromisoformat(updated) < date.fromisoformat(created):
                    errors.append(f"{track_dir.name}: updated date precedes created date")
            except ValueError:
                # The schema reports malformed dates.
                pass

        errors.extend(_track_document_errors(track_dir, metadata))

    errors.extend(_dependency_errors(tracks))
    return tracks, errors


def _roadmap_invariant_errors(
    roadmap: dict[str, Any],
    tracks: dict[str, dict[str, Any]],
    root: Path,
) -> list[str]:
    errors: list[str] = []
    releases = roadmap.get("releases", [])
    if not isinstance(releases, list):
        return errors

    versions = [release.get("version") for release in releases if isinstance(release, dict)]
    duplicate_versions = sorted(
        str(version) for version, count in Counter(versions).items() if count > 1
    )
    if duplicate_versions:
        duplicate_text = ", ".join(str(version) for version in duplicate_versions)
        errors.append(f"Duplicate release versions: {duplicate_text}")

    valid_versions = [
        version for version in versions if isinstance(version, str) and SEMVER_RE.fullmatch(version)
    ]
    if len(valid_versions) == len(versions):
        ordered = sorted(valid_versions, key=_semver_tuple)
        if valid_versions != ordered:
            errors.append("Roadmap releases must be ordered by semantic version")

    current = [
        release.get("version")
        for release in releases
        if isinstance(release, dict) and release.get("status") == "current"
    ]
    if len(current) != 1:
        errors.append(f"Roadmap must contain exactly one current release; found {len(current)}")

    stable_release = roadmap.get("programme", {}).get("stable_release")
    if stable_release not in versions:
        errors.append(f"Stable release {stable_release!r} is not present in the release train")

    assignments: dict[str, list[str]] = {}
    release_status: dict[str, str] = {}
    for release in releases:
        if not isinstance(release, dict):
            continue
        version = release.get("version")
        if not isinstance(version, str):
            continue
        release_status[version] = str(release.get("status"))
        for track_id in release.get("tracks", []):
            assignments.setdefault(str(track_id), []).append(version)

    for track_id in sorted(tracks):
        assigned = assignments.get(track_id, [])
        if not assigned:
            errors.append(f"{track_id}: not assigned to a roadmap release")
        elif len(assigned) > 1:
            errors.append(f"{track_id}: assigned to multiple releases: {', '.join(assigned)}")
        elif tracks[track_id].get("target_release") != assigned[0]:
            errors.append(
                f"{track_id}: target_release {tracks[track_id].get('target_release')!r} "
                f"does not match roadmap assignment {assigned[0]!r}"
            )

    for track_id, assigned_versions in assignments.items():
        if track_id not in tracks:
            errors.append(
                f"Roadmap assigns unknown track {track_id} to {', '.join(assigned_versions)}"
            )

    status_rank = {"released": 0, "current": 1, "planned": 2, "cancelled": 3}
    seen_ranks = [status_rank.get(str(release.get("status")), 99) for release in releases]
    if seen_ranks != sorted(seen_ranks):
        errors.append("Release statuses must progress from released to current to planned")

    current_version = current[0] if len(current) == 1 else None
    for release in releases:
        if not isinstance(release, dict):
            continue
        version = release.get("version")
        status = release.get("status")
        release_tracks = [str(item) for item in release.get("tracks", [])]
        if status == "released":
            incomplete = [
                track_id
                for track_id in release_tracks
                if tracks.get(track_id, {}).get("status") not in {"complete", "archived"}
            ]
            if incomplete:
                errors.append(
                    f"Release {version} is released but tracks are not complete: "
                    f"{', '.join(sorted(incomplete))}"
                )
        if status == "cancelled":
            non_archived = [
                track_id
                for track_id in release_tracks
                if tracks.get(track_id, {}).get("status") != "archived"
            ]
            if non_archived:
                errors.append(
                    f"Release {version} is cancelled but tracks are not archived: "
                    f"{', '.join(sorted(non_archived))}"
                )

    for track_id, metadata in tracks.items():
        target = metadata.get("target_release")
        status = metadata.get("status")
        target_status = release_status.get(str(target))
        # Repository track completion may precede release activation. A planned
        # release still cannot consume incomplete work as released evidence,
        # but a completed track must not force an external release-state claim.
        if status == "complete" and target_status not in {"released", "current", "planned"}:
            errors.append(
                f"{track_id}: complete track targets release with status {target_status!r}"
            )
        if status in {"active", "ready", "in_review"} and target_status != "current":
            errors.append(
                f"{track_id}: {status} track must target the current release, not {target!r}"
            )
        if status in {"planned", "proposed"} and target_status not in {"planned", "current"}:
            errors.append(
                f"{track_id}: {status} track targets release with status {target_status!r}"
            )
        if status == "blocked" and target_status not in {"current", "planned"}:
            errors.append(
                f"{track_id}: blocked track targets release with status {target_status!r}"
            )
        if status == "archived" and target_status not in {"released", "current", "cancelled"}:
            errors.append(
                f"{track_id}: archived track must target a cancelled release, not {target!r}"
            )

    if current_version is not None:
        current_tuple = _semver_tuple(str(current_version))
        for version, status in release_status.items():
            version_tuple = _semver_tuple(version)
            if status == "released" and version_tuple >= current_tuple:
                errors.append(
                    f"Released version {version} must precede current version {current_version}"
                )
            if status == "planned" and version_tuple <= current_tuple:
                errors.append(
                    f"Planned version {version} must follow current version {current_version}"
                )

    programme = roadmap.get("programme", {})
    for field in ("roadmap_document", "stable_acceptance_contract"):
        relative = programme.get(field)
        if isinstance(relative, str) and not (root / relative).is_file():
            errors.append(f"programme.{field}: file does not exist: {relative}")

    roadmap_document = programme.get("roadmap_document")
    if isinstance(roadmap_document, str):
        document_path = root / roadmap_document
        if document_path.is_file():
            document = document_path.read_text(encoding="utf-8")
            for track_id, metadata in sorted(tracks.items()):
                archived_spec = root / "conductor" / "archive" / track_id / "spec.md"
                directory = "archive" if archived_spec.is_file() else "tracks"
                target = root / "conductor" / directory / track_id / "spec.md"
                relative_target = os.path.relpath(target, document_path.parent).replace(os.sep, "/")
                canonical_reference = f"[{track_id} — {metadata['title']}]({relative_target})"
                if canonical_reference not in document:
                    errors.append(
                        f"human roadmap missing canonical track reference: {canonical_reference}"
                    )

    return errors


def validate_roadmap_files(
    roadmap_path: Path,
    roadmap_schema_path: Path,
    tracks_root: Path,
    track_schema_path: Path,
) -> RoadmapSummary:
    """Validate roadmap, metadata, documents and dependency graph."""
    try:
        roadmap = load_yaml(roadmap_path)
        roadmap_schema = load_schema(roadmap_schema_path)
        track_schema = load_schema(track_schema_path)
    except ValueError as exc:
        raise RoadmapValidationError(str(exc)) from exc

    root = roadmap_path.resolve().parents[1]
    tracks, errors = _load_tracks(tracks_root, track_schema)
    errors = _schema_errors(roadmap, roadmap_schema, "roadmap") + errors
    errors.extend(_roadmap_invariant_errors(roadmap, tracks, root))

    if errors:
        formatted = "\n".join(f"- {message}" for message in errors)
        raise RoadmapValidationError(f"Roadmap validation failed:\n{formatted}")

    releases = roadmap["releases"]
    current_release = next(
        release["version"] for release in releases if release["status"] == "current"
    )
    return RoadmapSummary(
        release_count=len(releases),
        track_count=len(tracks),
        v1_critical_track_count=sum(bool(track["v1_critical"]) for track in tracks.values()),
        current_release=current_release,
        track_status_counts=dict(Counter(track["status"] for track in tracks.values())),
    )
