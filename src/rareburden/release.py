"""Build and verify immutable release manifests for public artefacts."""

from __future__ import annotations

import mimetypes
import subprocess
from pathlib import Path
from typing import Any

from rareburden.provenance import atomic_write_json, content_id, sha256_file


class ReleaseManifestError(ValueError):
    """Raised when release artefacts or metadata are unsafe or inconsistent."""


def _run_git(root: Path, arguments: list[str]) -> str | None:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def _git_metadata(root: Path, explicit_commit: str | None) -> dict[str, Any]:
    commit = explicit_commit or _run_git(root, ["rev-parse", "HEAD"])
    if commit is None:
        return {"commit": None, "tree_state": "unavailable", "tag": None}
    status = _run_git(root, ["status", "--porcelain=v1", "--untracked-files=normal"])
    exact_tag = _run_git(root, ["describe", "--tags", "--exact-match", commit])
    return {
        "commit": commit,
        "tree_state": "clean" if status == "" else "dirty",
        "tag": exact_tag,
    }


def _safe_relative_file(root: Path, path: Path, *, label: str) -> tuple[Path, str]:
    if path.is_symlink():
        raise ReleaseManifestError(f"{label} cannot be a symlink: {path}")
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise ReleaseManifestError(f"{label} is outside release root: {path}") from exc
    if not resolved.is_file():
        raise ReleaseManifestError(f"{label} is not a regular file: {path}")
    relative_text = relative.as_posix()
    if not relative_text or relative.is_absolute() or ".." in relative.parts:
        raise ReleaseManifestError(f"Unsafe {label.lower()} path: {relative_text!r}")
    if any(ord(character) < 32 for character in relative_text):
        raise ReleaseManifestError(f"Control character in {label.lower()} path: {relative_text!r}")
    return resolved, relative_text


def _file_record(root: Path, path: Path, *, label: str) -> dict[str, Any]:
    resolved, relative_text = _safe_relative_file(root, path, label=label)
    digest, size = sha256_file(resolved)
    return {
        "path": relative_text,
        "sha256": digest,
        "size_bytes": size,
        "media_type": mimetypes.guess_type(relative_text)[0] or "application/octet-stream",
    }


def _default_material_paths(root: Path) -> list[Path]:
    return [path for name in ("pyproject.toml", "uv.lock") if (path := root / name).is_file()]


def build_release_manifest(
    *,
    root: Path,
    artefact_paths: list[Path],
    release_id: str,
    software_version: str,
    created_at: str,
    output_path: Path | None = None,
    git_commit: str | None = None,
    release_kind: str = "software_or_data",
    data_classification: str = "public",
    material_paths: list[Path] | None = None,
    repository_root: Path | None = None,
) -> dict[str, Any]:
    """Create a deterministic manifest for existing files beneath *root*.

    Creation timestamps are caller-supplied.  Content identity covers artefacts, materials,
    repository state and classification, preventing a manifest from being relabelled without
    changing its identifier.
    """
    resolved_root = root.expanduser().resolve()
    resolved_repository_root = (
        repository_root.expanduser().resolve() if repository_root is not None else resolved_root
    )
    if not resolved_root.is_dir():
        raise ReleaseManifestError(f"Release root is not a directory: {root}")
    if not artefact_paths:
        raise ReleaseManifestError("At least one release artefact is required")

    artefacts: list[dict[str, Any]] = []
    seen: set[str] = set()
    resolved_output = output_path.resolve() if output_path is not None else None
    for path in artefact_paths:
        record = _file_record(resolved_root, path, label="Release artefact")
        relative_text = str(record["path"])
        if relative_text in seen:
            raise ReleaseManifestError(f"Duplicate release artefact: {relative_text}")
        seen.add(relative_text)
        if resolved_output is not None and path.resolve() == resolved_output:
            raise ReleaseManifestError("A release manifest cannot include itself")
        artefacts.append(record)
    artefacts.sort(key=lambda item: str(item["path"]))

    materials: list[dict[str, Any]] = []
    material_seen: set[str] = set()
    for path in (
        material_paths if material_paths is not None else _default_material_paths(resolved_root)
    ):
        record = _file_record(resolved_root, path, label="Release material")
        relative_text = str(record["path"])
        if relative_text in material_seen:
            raise ReleaseManifestError(f"Duplicate release material: {relative_text}")
        material_seen.add(relative_text)
        materials.append(record)
    materials.sort(key=lambda item: str(item["path"]))

    core = {
        "release_id": release_id,
        "software_version": software_version,
        "created_at": created_at,
        "release_kind": release_kind,
        "data_classification": data_classification,
        "repository": _git_metadata(resolved_repository_root, git_commit),
        "materials": materials,
        "artefacts": artefacts,
        "summary": {
            "artefact_count": len(artefacts),
            "artefact_bytes": sum(int(item["size_bytes"]) for item in artefacts),
            "material_count": len(materials),
        },
    }
    manifest = {
        "schema_version": "1.0.0",
        "release_manifest_id": content_id("rel", core),
        **core,
    }
    if output_path is not None:
        output_parent = output_path.parent.resolve()
        try:
            output_parent.relative_to(resolved_root)
        except ValueError as exc:
            raise ReleaseManifestError(
                "Release manifest output must be within the release root"
            ) from exc
        atomic_write_json(output_path, manifest)
    return manifest


def _verify_file_records(
    *, root: Path, records: Any, collection_name: str, require_nonempty: bool
) -> list[str]:
    failures: list[str] = []
    if not isinstance(records, list):
        return [f"invalid manifest: {collection_name} must be a list"]
    if require_nonempty and not records:
        return [f"invalid manifest: {collection_name} must not be empty"]
    seen: set[str] = set()
    item_name = collection_name.removesuffix("s")
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            failures.append(f"invalid {item_name} entry at index {index}")
            continue
        relative_text = record["path"]
        relative = Path(relative_text)
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or any(ord(character) < 32 for character in relative_text)
        ):
            failures.append(f"unsafe path: {relative_text}")
            continue
        if relative_text in seen:
            failures.append(f"duplicate path in {collection_name}: {relative_text}")
            continue
        seen.add(relative_text)
        path = root / relative
        if path.is_symlink():
            failures.append(f"symlink not permitted: {relative_text}")
            continue
        try:
            path.resolve().relative_to(root)
        except ValueError:
            failures.append(f"unsafe path: {relative_text}")
            continue
        if not path.is_file():
            failures.append(f"missing: {relative_text}")
            continue
        digest, size = sha256_file(path)
        if digest != record.get("sha256"):
            failures.append(f"checksum mismatch: {relative_text}")
        if size != record.get("size_bytes"):
            failures.append(f"size mismatch: {relative_text}")
    return failures


def verify_release_manifest(root: Path, manifest: dict[str, Any]) -> list[str]:
    """Return identity, path, digest, size and summary failures for a release manifest."""
    failures: list[str] = []
    resolved_root = root.expanduser().resolve()
    artefacts = manifest.get("artefacts", [])
    materials = manifest.get("materials", [])
    failures.extend(
        _verify_file_records(
            root=resolved_root,
            records=artefacts,
            collection_name="artefacts",
            require_nonempty=True,
        )
    )
    failures.extend(
        _verify_file_records(
            root=resolved_root,
            records=materials,
            collection_name="materials",
            require_nonempty=False,
        )
    )

    core_keys = (
        "release_id",
        "software_version",
        "created_at",
        "release_kind",
        "data_classification",
        "repository",
        "materials",
        "artefacts",
        "summary",
    )
    if all(key in manifest for key in core_keys):
        core = {key: manifest[key] for key in core_keys}
        expected_id = content_id("rel", core)
        if manifest.get("release_manifest_id") != expected_id:
            failures.append("release manifest content identifier mismatch")

    if isinstance(artefacts, list) and isinstance(manifest.get("summary"), dict):
        summary = manifest["summary"]
        expected_count = len(artefacts)
        expected_bytes = sum(
            int(item.get("size_bytes", 0)) for item in artefacts if isinstance(item, dict)
        )
        if summary.get("artefact_count") != expected_count:
            failures.append("summary artefact_count mismatch")
        if summary.get("artefact_bytes") != expected_bytes:
            failures.append("summary artefact_bytes mismatch")
        if isinstance(materials, list) and summary.get("material_count") != len(materials):
            failures.append("summary material_count mismatch")

    repository = manifest.get("repository")
    if isinstance(repository, dict) and repository.get("tree_state") == "clean":
        commit = repository.get("commit")
        current_commit = _run_git(resolved_root, ["rev-parse", "HEAD"])
        if commit is not None and current_commit is not None and commit != current_commit:
            failures.append("repository commit differs from clean release manifest")
    return failures


__all__ = ["ReleaseManifestError", "build_release_manifest", "verify_release_manifest"]
