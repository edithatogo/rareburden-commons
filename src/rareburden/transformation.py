"""Retrospective, content-addressed records for scientific transformations.

The acquisition layer records how source artefacts entered the project.  This module
records what actually happened after acquisition: exact inputs and outputs, prospective
protocol linkage, software and environment identity, parameters, randomness and the
execution interval.  Prospective plans and retrospective execution evidence are kept
separate deliberately.
"""

from __future__ import annotations

import json
import mimetypes
import platform
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from rareburden import __version__
from rareburden.provenance import content_id, git_commit, git_tree_state, sha256_file

_SECRET_KEY_RE = re.compile(
    r"(?:^|[_-])(?:api[_-]?key|access[_-]?token|token|auth|bearer|credential|password|passwd|secret)(?:$|[_-])",
    re.IGNORECASE,
)
_SECRET_VALUE_PATTERNS = (
    re.compile(r"(?i)(?:password|passwd|secret|token|api[_-]?key)\s*[=:]\s*\S+"),
    re.compile(r"(?i)https?://[^/@\s:]+:[^/@\s]+@"),
    re.compile(r"(?i)(?:--(?:password|token|secret|api-key))(?:=|\s+)\S+"),
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class TransformationRecordError(ValueError):
    """Raised when a transformation record is unsafe or internally inconsistent."""


@dataclass(frozen=True)
class TransformationArtifact:
    """One content-addressed input or output in a transformation record."""

    path: str
    sha256: str
    size_bytes: int
    media_type: str
    role: str
    source_release_id: str | None = None
    acquisition_manifest_id: str | None = None
    licence_state: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        value: dict[str, Any] = {
            "path": self.path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "media_type": self.media_type,
            "role": self.role,
        }
        if self.source_release_id is not None:
            value["source_release_id"] = self.source_release_id
        if self.acquisition_manifest_id is not None:
            value["acquisition_manifest_id"] = self.acquisition_manifest_id
        if self.licence_state is not None:
            value["licence_state"] = self.licence_state
        return value


def _normalise_logical_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or value.startswith("./")
        or "\\" in value
        or any(ord(character) < 32 for character in value)
    ):
        raise TransformationRecordError(f"Unsafe logical artefact path: {value!r}")
    normalised = path.as_posix()
    if normalised in {"", "."}:
        raise TransformationRecordError("Logical artefact path must identify a file")
    return normalised


def artifact_from_file(
    path: Path,
    *,
    logical_path: str,
    role: str,
    media_type: str | None = None,
    source_release_id: str | None = None,
    acquisition_manifest_id: str | None = None,
    licence_state: str | None = None,
) -> TransformationArtifact:
    """Create an immutable artefact record from a regular, non-symlink file.

    ``logical_path`` is deliberately caller supplied.  It records the path within the
    research object rather than leaking host-specific absolute paths.
    """
    if path.is_symlink():
        raise TransformationRecordError(f"Symlink artefacts are not permitted: {path}")
    if not path.is_file():
        raise TransformationRecordError(f"Transformation artefact is not a file: {path}")
    digest, size = sha256_file(path)
    guessed = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return TransformationArtifact(
        path=_normalise_logical_path(logical_path),
        sha256=digest,
        size_bytes=size,
        media_type=media_type or guessed,
        role=role,
        source_release_id=source_release_id,
        acquisition_manifest_id=acquisition_manifest_id,
        licence_state=licence_state,
    )


def _parse_timestamp(value: str, *, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TransformationRecordError(f"{field} is not a valid RFC 3339 timestamp") from exc
    if parsed.tzinfo is None:
        raise TransformationRecordError(f"{field} must include a timezone")
    return parsed


def _assert_secret_safe(value: Any, *, location: str = "parameters") -> None:
    if isinstance(value, Mapping):
        for raw_key, nested in value.items():
            key = str(raw_key)
            if _SECRET_KEY_RE.search(key):
                raise TransformationRecordError(
                    f"Secret-like key is not permitted in transformation records: {location}.{key}"
                )
            _assert_secret_safe(nested, location=f"{location}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, nested in enumerate(value):
            _assert_secret_safe(nested, location=f"{location}[{index}]")
        return
    if isinstance(value, str):
        for pattern in _SECRET_VALUE_PATTERNS:
            if pattern.search(value):
                raise TransformationRecordError(
                    f"Secret-like value is not permitted in transformation records: {location}"
                )


def _normalise_json(value: Any) -> Any:
    """Round-trip through canonical JSON-compatible types and reject non-finite data."""
    try:
        encoded = json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":"))
        return json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise TransformationRecordError(f"Value is not finite canonical JSON: {exc}") from exc


def capture_environment(
    *,
    repository_root: Path | None = None,
    lockfile_path: Path | None = None,
    container_image_digest: str | None = None,
) -> dict[str, Any]:
    """Capture portable execution-environment identity without host-specific paths."""
    environment: dict[str, Any] = {
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
    }
    if lockfile_path is not None:
        if lockfile_path.is_symlink() or not lockfile_path.is_file():
            raise TransformationRecordError(f"Lockfile is unavailable or unsafe: {lockfile_path}")
        digest, size = sha256_file(lockfile_path)
        logical_name = lockfile_path.name
        environment["lockfile"] = {
            "path": logical_name,
            "sha256": digest,
            "size_bytes": size,
        }
    if container_image_digest is not None:
        digest = container_image_digest.lower()
        valid_prefix = digest.startswith("sha256:")
        valid_digest = _SHA256_RE.fullmatch(digest.removeprefix("sha256:"))
        if not valid_prefix or not valid_digest:
            raise TransformationRecordError(
                "container_image_digest must use the sha256:<64 hexadecimal> form"
            )
        environment["container_image_digest"] = digest
    if repository_root is not None:
        environment["repository_commit"] = git_commit(repository_root)
    return environment


def build_transformation_run(
    *,
    activity_id: str,
    title: str,
    prospective_plan: Mapping[str, Any],
    started_at: str,
    ended_at: str,
    inputs: Sequence[TransformationArtifact],
    outputs: Sequence[TransformationArtifact],
    parameters: Mapping[str, Any],
    command: Sequence[str],
    environment: Mapping[str, Any],
    repository_root: Path | None = None,
    randomness: Mapping[str, Any] | None = None,
    agents: Sequence[Mapping[str, Any]] = (),
    limitations: Sequence[str] = (),
    assertions: Sequence[str] = (),
    status: str = "completed",
) -> dict[str, Any]:
    """Build a content-addressed retrospective transformation record.

    The prospective protocol is linked but not rewritten as retrospective evidence.
    Timestamps are supplied explicitly so the record can be reconstructed exactly.
    """
    start = _parse_timestamp(started_at, field="started_at")
    end = _parse_timestamp(ended_at, field="ended_at")
    if end < start:
        raise TransformationRecordError("ended_at precedes started_at")
    if not inputs:
        raise TransformationRecordError("A transformation run must record at least one input")
    if not outputs:
        raise TransformationRecordError("A transformation run must record at least one output")
    if status not in {"completed", "failed", "cancelled"}:
        raise TransformationRecordError(f"Unsupported transformation status: {status}")

    input_records = sorted((item.as_dict() for item in inputs), key=lambda item: str(item["path"]))
    output_records = sorted(
        (item.as_dict() for item in outputs), key=lambda item: str(item["path"])
    )
    input_paths = [str(item["path"]) for item in input_records]
    output_paths = [str(item["path"]) for item in output_records]
    if len(set(input_paths)) != len(input_paths):
        raise TransformationRecordError("Duplicate input logical paths are not permitted")
    if len(set(output_paths)) != len(output_paths):
        raise TransformationRecordError("Duplicate output logical paths are not permitted")
    if set(input_paths) & set(output_paths):
        raise TransformationRecordError("An artefact cannot be both an input and an output")

    plan = _normalise_json(dict(prospective_plan))
    parameter_values = _normalise_json(dict(parameters))
    command_values = [str(item) for item in command]
    environment_values = _normalise_json(dict(environment))
    randomness_values = _normalise_json(dict(randomness)) if randomness is not None else None
    agent_values = [_normalise_json(dict(item)) for item in agents]
    _assert_secret_safe(plan, location="prospective_plan")
    _assert_secret_safe(parameter_values)
    _assert_secret_safe(command_values, location="command")
    _assert_secret_safe(environment_values, location="environment")
    _assert_secret_safe(agent_values, location="agents")

    if not command_values or any(not item for item in command_values):
        raise TransformationRecordError("command must be a non-empty argv sequence")
    if not isinstance(plan, dict) or not plan.get("plan_id"):
        raise TransformationRecordError("prospective_plan.plan_id is required")

    software: dict[str, Any] = {
        "name": "rareburden",
        "version": __version__,
        "entry_point": command_values[0],
        "command": command_values,
        "git_commit": git_commit(repository_root),
        "git_tree_state": git_tree_state(repository_root),
    }
    core: dict[str, Any] = {
        "activity_id": activity_id,
        "title": title,
        "status": status,
        "prospective_plan": plan,
        "execution": {"started_at": started_at, "ended_at": ended_at},
        "inputs": input_records,
        "outputs": output_records,
        "parameters": parameter_values,
        "software": software,
        "environment": environment_values,
        "agents": sorted(agent_values, key=lambda item: str(item.get("id", item.get("name", "")))),
        "limitations": sorted(set(limitations)),
        "assertions": sorted(set(assertions)),
    }
    if randomness_values is not None:
        core["randomness"] = randomness_values
    return {
        "schema_version": "1.0.0",
        "transformation_run_id": content_id("run", core),
        **core,
    }


def verify_transformation_run(
    record: Mapping[str, Any],
    *,
    artefact_roots: Sequence[Path],
) -> list[str]:
    """Verify content identity and artefact digests against one or more roots.

    A logical path may resolve in exactly one supplied root.  Ambiguity is rejected so a
    verifier cannot silently choose between different files with the same logical name.
    """
    failures: list[str] = []
    identity_keys = {"schema_version", "transformation_run_id"}
    core = {key: value for key, value in record.items() if key not in identity_keys}
    try:
        expected_id = content_id("run", core)
    except Exception as exc:  # defensive verification boundary
        failures.append(f"unable to recompute transformation identifier: {exc}")
    else:
        if record.get("transformation_run_id") != expected_id:
            failures.append("transformation run content identifier mismatch")

    roots = [root.expanduser().resolve() for root in artefact_roots]
    for collection in ("inputs", "outputs"):
        values = record.get(collection)
        if not isinstance(values, list):
            failures.append(f"{collection} is not a list")
            continue
        for item in values:
            if not isinstance(item, Mapping) or not isinstance(item.get("path"), str):
                failures.append(f"invalid {collection} artefact record")
                continue
            logical_path = str(item["path"])
            try:
                normalised = _normalise_logical_path(logical_path)
            except TransformationRecordError as exc:
                failures.append(str(exc))
                continue
            candidates: list[Path] = []
            for root in roots:
                candidate = root / normalised
                if candidate.is_file() and not candidate.is_symlink():
                    candidates.append(candidate)
            if len(candidates) != 1:
                failures.append(
                    f"{collection} artefact {normalised} resolved {len(candidates)} times; "
                    "expected exactly one"
                )
                continue
            digest, size = sha256_file(candidates[0])
            if digest != item.get("sha256"):
                failures.append(f"checksum mismatch: {normalised}")
            if size != item.get("size_bytes"):
                failures.append(f"size mismatch: {normalised}")
    return failures


__all__ = [
    "TransformationArtifact",
    "TransformationRecordError",
    "artifact_from_file",
    "build_transformation_run",
    "capture_environment",
    "verify_transformation_run",
]
