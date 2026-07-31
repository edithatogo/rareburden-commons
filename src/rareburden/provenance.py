"""Immutable provenance records, checksums and atomic JSON writes."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, BinaryIO
from urllib.parse import urlsplit

from rareburden import __version__
from rareburden.schema import SchemaValidationError, load_mapping, validate_instance

_CHUNK_SIZE = 1024 * 1024
_SLUG_RE = re.compile(r"[^a-z0-9]+")
LICENCE_STATES = frozenset({"verified", "conditional", "unknown", "not_applicable", "restricted"})


class ProvenanceError(ValueError):
    """Raised when provenance cannot be represented or verified safely."""


@dataclass(frozen=True)
class ArtifactRecord:
    """Content identity for one immutable artefact."""

    name: str
    sha256: str
    size_bytes: int
    media_type: str

    def as_dict(self) -> dict[str, str | int]:
        """Return the JSON-compatible representation used in manifests."""
        return {
            "name": self.name,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "media_type": self.media_type,
        }


def validate_licence_evidence(
    *,
    licence_state: str,
    licence_reference: str | None,
    notes: str,
) -> None:
    """Require explicit, non-credentialled evidence for each licence assertion."""
    if licence_state not in LICENCE_STATES:
        raise ProvenanceError(f"Unsupported licence state: {licence_state}")
    if licence_state in {"verified", "conditional", "restricted"} and not licence_reference:
        raise ProvenanceError(
            f"Licence state {licence_state!r} requires a persistent HTTPS licence reference"
        )
    if licence_reference is not None:
        parsed = urlsplit(licence_reference)
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ProvenanceError("Licence reference must be a credential-free HTTPS URL")
    if licence_state == "unknown" and not notes.strip():
        raise ProvenanceError("Unknown licence state requires a substantive rationale in notes")


def require_automated_acquisition_licence(
    *,
    licence_state: str,
    licence_reference: str | None,
    notes: str,
) -> None:
    """Fail before network access when rights are unknown or restrict automation."""
    validate_licence_evidence(
        licence_state=licence_state,
        licence_reference=licence_reference,
        notes=notes,
    )
    if licence_state in {"unknown", "restricted"}:
        raise ProvenanceError(
            f"Licence state {licence_state!r} prohibits automated acquisition; "
            "use manual registration after authorised review"
        )


def utc_now() -> str:
    """Return an RFC 3339 UTC timestamp with second precision."""
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_stream(stream: BinaryIO) -> tuple[str, int]:
    """Return the SHA-256 digest and byte count for a binary stream."""
    digest = hashlib.sha256()
    size = 0
    while chunk := stream.read(_CHUNK_SIZE):
        digest.update(chunk)
        size += len(chunk)
    return digest.hexdigest(), size


def sha256_file(path: Path) -> tuple[str, int]:
    """Return the SHA-256 digest and byte count for *path*."""
    try:
        with path.open("rb") as handle:
            return sha256_stream(handle)
    except OSError as exc:
        raise ProvenanceError(f"Unable to hash artefact {path}: {exc}") from exc


def canonical_json_bytes(value: Any) -> bytes:
    """Serialise JSON deterministically for hashing and release records."""
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def content_id(prefix: str, value: Any, *, length: int = 24) -> str:
    """Create a stable, readable content-derived identifier."""
    if not prefix or any(
        character not in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in prefix
    ):
        raise ProvenanceError("prefix must contain lowercase letters, digits or hyphens")
    if not 8 <= length <= 64:
        raise ProvenanceError("length must be between 8 and 64")
    digest = hashlib.sha256(canonical_json_bytes(value)).hexdigest()[:length]
    return f"{prefix}-{digest}"


def stable_identifier(*parts: str, prefix: str | None = None, digest_length: int = 12) -> str:
    """Build a stable slug with a collision-resistant suffix.

    Human-readable components aid audit, while the suffix prevents punctuation and
    truncation choices from silently collapsing distinct source releases.
    """
    cleaned = [_SLUG_RE.sub("-", part.strip().lower()).strip("-") for part in parts]
    cleaned = [part for part in cleaned if part]
    if not cleaned:
        raise ProvenanceError("Cannot create a stable identifier from empty input")
    if prefix is not None:
        clean_prefix = _SLUG_RE.sub("-", prefix.strip().lower()).strip("-")
        if not clean_prefix:
            raise ProvenanceError("Identifier prefix is empty after normalisation")
        cleaned.insert(0, clean_prefix)
    core = "-".join(cleaned)
    digest = hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:digest_length]
    return f"{core}-{digest}"


def atomic_write_bytes(path: Path, content: bytes, *, mode: int = 0o644) -> None:
    """Atomically replace *path* after flushing content to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ProvenanceError(f"Refusing to replace symlink: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary_path.chmod(mode)
        temporary_path.replace(path)
        _fsync_directory(path.parent)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def _fsync_directory(path: Path) -> None:
    """Best-effort directory fsync after an atomic rename."""
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def atomic_write_json(path: Path, value: Any) -> None:
    """Atomically write canonical, UTF-8 JSON."""
    atomic_write_bytes(path, canonical_json_bytes(value))


def git_commit(repository_root: Path | None) -> str | None:
    """Return the current commit when *repository_root* is a Git work tree."""
    if repository_root is None:
        return None
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def git_tree_state(repository_root: Path | None) -> str:
    """Return ``clean``, ``dirty`` or ``unavailable`` for a Git work tree.

    Untracked files are included because an analysis executed beside untracked code or
    configuration is not a clean, fully reconstructible Git state.  Failures are reported
    conservatively as ``unavailable`` rather than being mistaken for a clean tree.
    """
    if repository_root is None:
        return "unavailable"
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=normal"],
            cwd=repository_root,
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "unavailable"
    return "dirty" if result.stdout.strip() else "clean"


def _normalise_digest(value: str | None) -> str | None:
    if value is None:
        return None
    digest = value.strip().lower()
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ProvenanceError("Expected SHA-256 must be exactly 64 hexadecimal characters")
    return digest


def build_manifest(
    *,
    source_id: str,
    release_id: str,
    method: str,
    requested_url: str,
    resolved_url: str,
    artifact: ArtifactRecord,
    expected_sha256: str | None,
    etag: str | None,
    last_modified: str | None,
    repository_root: Path | None = None,
    notes: str = "",
    retrieved_at: str | None = None,
) -> dict[str, Any]:
    """Build an acquisition manifest from verified artefact metadata."""
    expected = _normalise_digest(expected_sha256)
    if expected is not None and expected != artifact.sha256:
        raise ProvenanceError(f"Checksum mismatch: expected {expected}, received {artifact.sha256}")
    acquisition_identity = {
        "source_id": source_id,
        "release_id": release_id,
        "method": method,
        "requested_url": requested_url,
        "resolved_url": resolved_url,
        "artifact": artifact.as_dict(),
        "expected_sha256": expected,
    }
    acquisition_id = content_id("acq", acquisition_identity)
    return {
        "schema_version": "1.0.0",
        "acquisition_id": acquisition_id,
        "source_id": source_id,
        "release_id": release_id,
        "method": method,
        "requested_url": requested_url,
        "resolved_url": resolved_url,
        "retrieved_at": retrieved_at or utc_now(),
        "pinning": {
            "expected_sha256": expected,
            "status": "verified" if expected is not None else "candidate_unpinned",
        },
        "artifact": artifact.as_dict(),
        "response": {"etag": etag, "last_modified": last_modified},
        "tool": {
            "name": "rareburden",
            "version": __version__,
            "git_commit": git_commit(repository_root),
        },
        "notes": notes,
    }


def register_local_artifact(
    *,
    source_id: str,
    release_id: str,
    source_url: str,
    artifact_path: Path,
    expected_sha256: str | None,
    media_type: str | None = None,
    repository_root: Path | None = None,
    notes: str = "",
    retrieved_at: str | None = None,
) -> dict[str, Any]:
    """Register an existing local artefact without copying or modifying it."""
    if not artifact_path.is_file():
        raise ProvenanceError(f"Artefact is not a regular file: {artifact_path}")
    digest, size = sha256_file(artifact_path)
    expected = _normalise_digest(expected_sha256)
    if expected is not None and digest != expected:
        raise ProvenanceError(f"Checksum mismatch: expected {expected}, received {digest}")
    guessed_type = mimetypes.guess_type(artifact_path.name)[0] or "application/octet-stream"
    artifact = ArtifactRecord(
        name=artifact_path.name,
        sha256=digest,
        size_bytes=size,
        media_type=media_type or guessed_type,
    )
    return build_manifest(
        source_id=source_id,
        release_id=release_id,
        method="manual_registration",
        requested_url=source_url,
        resolved_url=source_url,
        artifact=artifact,
        expected_sha256=expected,
        etag=None,
        last_modified=None,
        repository_root=repository_root,
        notes=notes,
        retrieved_at=retrieved_at,
    )


def build_source_release(
    *,
    source_id: str,
    release_id: str,
    source_url: str,
    licence_state: str,
    licence_reference: str | None,
    acquisition_manifest: str,
    notes: str = "",
    registered_at: str | None = None,
) -> dict[str, Any]:
    """Build a compact source-release record linked to its acquisition manifest."""
    validate_licence_evidence(
        licence_state=licence_state,
        licence_reference=licence_reference,
        notes=notes,
    )
    return {
        "schema_version": "1.0.0",
        "source_release_id": stable_identifier(source_id, release_id, prefix="src"),
        "source_id": source_id,
        "release_id": release_id,
        "source_url": source_url,
        "licence_state": licence_state,
        "licence_reference": licence_reference,
        "acquisition_manifest": acquisition_manifest,
        "registered_at": registered_at or utc_now(),
        "notes": notes,
    }


def validate_json_record(record: dict[str, Any], schema_path: Path) -> None:
    """Validate *record* against a Draft 2020-12 schema."""
    try:
        validate_instance(record, load_mapping(schema_path), label=schema_path.stem)
    except SchemaValidationError as exc:
        raise ProvenanceError(str(exc)) from exc


def write_json_record(record: dict[str, Any], output_path: Path, schema_path: Path) -> None:
    """Validate and atomically write a provenance record."""
    validate_json_record(record, schema_path)
    atomic_write_json(output_path, record)


__all__ = [
    "ArtifactRecord",
    "ProvenanceError",
    "atomic_write_bytes",
    "atomic_write_json",
    "build_manifest",
    "build_source_release",
    "canonical_json_bytes",
    "content_id",
    "git_commit",
    "register_local_artifact",
    "require_automated_acquisition_licence",
    "sha256_file",
    "sha256_stream",
    "stable_identifier",
    "utc_now",
    "validate_json_record",
    "validate_licence_evidence",
    "write_json_record",
]
