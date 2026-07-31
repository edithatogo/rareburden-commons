#!/usr/bin/env python3
"""Build and verify a deterministic, local-only federated-node wheel bundle."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import stat
import tempfile
import zipfile
from collections.abc import Sequence
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = "0.1.0"
MANIFEST_NAME = "manifest.json"
WHEEL_DIRECTORY = "wheels"
_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
_URL_PREFIXES = ("http://", "https://", "file://")
MAX_ARCHIVE_MEMBERS = 10_000
MAX_MEMBER_BYTES = 512_000_000
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 4_000_000_000
MAX_INPUT_WHEEL_BYTES = 512_000_000


class NodeBundleError(ValueError):
    """Raised when a node bundle or one of its local artifacts is unsafe."""


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_member_name(name: str) -> bool:
    if not name or "\x00" in name or "\\" in name:
        return False
    path = PurePosixPath(name)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def _check_archive_bounds(members: Sequence[zipfile.ZipInfo], *, label: str) -> None:
    if len(members) > MAX_ARCHIVE_MEMBERS:
        raise NodeBundleError(f"{label} contains too many archive members")
    total = 0
    for member in members:
        if member.file_size < 0 or member.file_size > MAX_MEMBER_BYTES:
            raise NodeBundleError(f"{label} contains an oversized archive member")
        total += member.file_size
        if total > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
            raise NodeBundleError(f"{label} exceeds the uncompressed-size limit")


def _wheel_identity(filename: str) -> tuple[str, str, str]:
    parts = filename.removesuffix(".whl").split("-")
    if len(parts) not in {5, 6} or any(not part for part in parts):
        raise NodeBundleError(f"wheel filename is not PEP 427 shaped: {filename}")
    return parts[0], parts[1], f"{parts[0]}-{parts[1]}.dist-info"


def _normalise_distribution(value: str) -> str:
    return value.lower().replace("-", "_").replace(".", "_")


def _metadata_value(data: bytes, field: str) -> str | None:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise NodeBundleError("wheel METADATA is not valid UTF-8") from exc
    prefix = f"{field}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return None


def _validate_wheel_bytes(filename: str, data: bytes, *, role: str) -> None:
    distribution, version, dist_info = _wheel_identity(filename)
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as wheel:
            members = wheel.infolist()
            _check_archive_bounds(members, label=f"wheel {filename}")
            names = [member.filename for member in members]
            if len(names) != len(set(names)):
                raise NodeBundleError(f"wheel contains duplicate members: {filename}")
            if any(not _safe_member_name(name) for name in names):
                raise NodeBundleError(f"wheel contains an unsafe member path: {filename}")
            required = {
                f"{dist_info}/METADATA",
                f"{dist_info}/WHEEL",
                f"{dist_info}/RECORD",
            }
            if not required.issubset(names):
                raise NodeBundleError(f"wheel is missing required metadata: {filename}")
            metadata = wheel.read(f"{dist_info}/METADATA")
            if (
                _normalise_distribution(_metadata_value(metadata, "Name") or "")
                != _normalise_distribution(distribution)
                or _metadata_value(metadata, "Version") != version
            ):
                raise NodeBundleError(
                    f"wheel metadata identity does not match filename: {filename}"
                )
            if role == "node" and _normalise_distribution(distribution) != "rareburden":
                raise NodeBundleError("node wheel must contain the rareburden distribution")
            bad_member = wheel.testzip()
            if bad_member is not None:
                raise NodeBundleError(f"wheel has a corrupt member: {filename}: {bad_member}")
    except zipfile.BadZipFile as exc:
        raise NodeBundleError(f"artifact is not a valid wheel archive: {filename}") from exc


def _validate_wheel(path_value: str | os.PathLike[str], *, role: str) -> tuple[Path, bytes]:
    raw = os.fspath(path_value)
    if raw.lower().startswith(_URL_PREFIXES):
        raise NodeBundleError(f"wheel must be supplied as a local path, not a URL: {raw}")

    path = Path(path_value)
    if not path.exists():
        raise NodeBundleError(f"wheel does not exist: {path}")
    if path.is_symlink():
        raise NodeBundleError(f"wheel must not be a symbolic link: {path}")
    if not path.is_file():
        raise NodeBundleError(f"wheel is not a regular file: {path}")
    if path.suffix != ".whl" or not _safe_member_name(path.name):
        raise NodeBundleError(f"artifact is not a safely named wheel: {path.name}")

    if path.stat().st_size > MAX_INPUT_WHEEL_BYTES:
        raise NodeBundleError(f"wheel exceeds the input-size limit: {path}")
    data = path.read_bytes()
    _validate_wheel_bytes(path.name, data, role=role)
    return path, data


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    return info


def build_node_bundle(
    output_path: str | os.PathLike[str],
    node_wheel: str | os.PathLike[str],
    dependency_wheels: Sequence[str | os.PathLike[str]] = (),
) -> dict[str, Any]:
    """Create a deterministic bundle from wheel files already present on disk."""

    supplied = [("node", node_wheel), *(("dependency", item) for item in dependency_wheels)]
    artifacts: list[tuple[str, Path, bytes]] = []
    seen_names: set[str] = set()
    seen_paths: set[Path] = set()
    for role, path_value in supplied:
        path, data = _validate_wheel(path_value, role=role)
        resolved = path.resolve()
        if path.name in seen_names:
            raise NodeBundleError(f"duplicate wheel filename: {path.name}")
        if resolved in seen_paths:
            raise NodeBundleError(f"duplicate wheel artifact: {path}")
        seen_names.add(path.name)
        seen_paths.add(resolved)
        artifacts.append((role, path, data))

    output = Path(output_path)
    if output.exists() and (output.is_symlink() or not output.is_file()):
        raise NodeBundleError(f"bundle output must be a regular file path: {output}")
    if output.resolve() in seen_paths:
        raise NodeBundleError("bundle output must not overwrite an input wheel")
    output.parent.mkdir(parents=True, exist_ok=True)

    artifact_records = [
        {
            "filename": path.name,
            "role": role,
            "sha256": _sha256(data),
            "size": len(data),
        }
        for role, path, data in artifacts
    ]
    artifact_records.sort(key=lambda record: str(record["filename"]))
    manifest: dict[str, Any] = {
        "artifacts": artifact_records,
        "bundle_format": "rareburden-offline-node-wheel-bundle",
        "schema_version": SCHEMA_VERSION,
    }

    file_by_name = {path.name: data for _, path, data in artifacts}
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output.parent, prefix=f".{output.name}.", suffix=".tmp", delete=False
        ) as temporary:
            temporary_name = temporary.name
        with zipfile.ZipFile(temporary_name, mode="w", allowZip64=True) as bundle:
            bundle.writestr(_zip_info(MANIFEST_NAME), _canonical_json(manifest))
            for filename in sorted(file_by_name):
                bundle.writestr(_zip_info(f"{WHEEL_DIRECTORY}/{filename}"), file_by_name[filename])
        Path(temporary_name).replace(output)
        temporary_name = None
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
    return manifest


def verify_node_bundle(bundle_path: str | os.PathLike[str]) -> dict[str, Any]:
    """Verify structure, roles, sizes and hashes without extracting the bundle."""

    path = Path(bundle_path)
    if not path.exists() or path.is_symlink() or not path.is_file():
        raise NodeBundleError(f"bundle is not a regular local file: {path}")
    try:
        with zipfile.ZipFile(path) as bundle:
            members = bundle.infolist()
            _check_archive_bounds(members, label="bundle")
            names = [member.filename for member in members]
            if len(names) != len(set(names)):
                raise NodeBundleError("bundle contains duplicate archive members")
            if any(
                not _safe_member_name(name) or member.is_dir()
                for name, member in zip(names, members, strict=True)
            ):
                raise NodeBundleError("bundle contains an unsafe archive member")
            if MANIFEST_NAME not in names:
                raise NodeBundleError("bundle manifest is missing")
            try:
                manifest = json.loads(bundle.read(MANIFEST_NAME))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise NodeBundleError("bundle manifest is not valid UTF-8 JSON") from exc
            if not isinstance(manifest, dict):
                raise NodeBundleError("bundle manifest must be a JSON object")
            if manifest.get("schema_version") != SCHEMA_VERSION:
                raise NodeBundleError("bundle manifest schema version is unsupported")
            if manifest.get("bundle_format") != "rareburden-offline-node-wheel-bundle":
                raise NodeBundleError("bundle format is unsupported")
            records = manifest.get("artifacts")
            if not isinstance(records, list) or not records:
                raise NodeBundleError("bundle manifest must contain artifacts")

            expected_members = {MANIFEST_NAME}
            seen_filenames: set[str] = set()
            node_count = 0
            for record in records:
                if not isinstance(record, dict) or set(record) != {
                    "filename",
                    "role",
                    "sha256",
                    "size",
                }:
                    raise NodeBundleError("bundle manifest has an invalid artifact record")
                filename = record["filename"]
                role = record["role"]
                digest = record["sha256"]
                size = record["size"]
                if (
                    not isinstance(filename, str)
                    or Path(filename).name != filename
                    or not filename.endswith(".whl")
                    or not _safe_member_name(filename)
                ):
                    raise NodeBundleError("bundle manifest has an unsafe artifact filename")
                if filename in seen_filenames:
                    raise NodeBundleError(f"bundle manifest repeats artifact: {filename}")
                seen_filenames.add(filename)
                if role not in {"node", "dependency"}:
                    raise NodeBundleError(f"bundle manifest has an invalid role: {filename}")
                node_count += role == "node"
                if not isinstance(size, int) or isinstance(size, bool) or size < 0:
                    raise NodeBundleError(f"bundle manifest has an invalid size: {filename}")
                if (
                    not isinstance(digest, str)
                    or len(digest) != 64
                    or any(character not in "0123456789abcdef" for character in digest)
                ):
                    raise NodeBundleError(f"bundle manifest has an invalid SHA-256: {filename}")
                member_name = f"{WHEEL_DIRECTORY}/{filename}"
                expected_members.add(member_name)
                if member_name not in names:
                    raise NodeBundleError(f"bundle artifact is missing: {filename}")
                data = bundle.read(member_name)
                if len(data) != size or _sha256(data) != digest:
                    raise NodeBundleError(f"bundle artifact integrity check failed: {filename}")
                _validate_wheel_bytes(filename, data, role=role)

            if node_count != 1:
                raise NodeBundleError("bundle must contain exactly one node wheel")
            if set(names) != expected_members:
                raise NodeBundleError("bundle contains unmanifested archive members")
            if records != sorted(records, key=lambda record: str(record["filename"])):
                raise NodeBundleError("bundle manifest artifacts are not in canonical order")
            if bundle.read(MANIFEST_NAME) != _canonical_json(manifest):
                raise NodeBundleError("bundle manifest is not canonically encoded")
            bad_member = bundle.testzip()
            if bad_member is not None:
                raise NodeBundleError(f"bundle has a corrupt member: {bad_member}")
    except zipfile.BadZipFile as exc:
        raise NodeBundleError(f"bundle is not a valid ZIP archive: {path}") from exc
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="build a bundle from local wheels")
    build.add_argument("--output", required=True, type=Path)
    build.add_argument("--node-wheel", required=True, type=Path)
    build.add_argument("--dependency-wheel", action="append", default=[], type=Path)
    check = subparsers.add_parser("check", help="verify an existing bundle")
    check.add_argument("bundle", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "build":
            manifest = build_node_bundle(args.output, args.node_wheel, args.dependency_wheel)
            verify_node_bundle(args.output)
        else:
            manifest = verify_node_bundle(args.bundle)
    except NodeBundleError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
