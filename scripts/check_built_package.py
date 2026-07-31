#!/usr/bin/env python3
"""Inspect Python wheel and source-distribution safety, integrity and runtime assets."""

from __future__ import annotations

import argparse
import base64
import csv
import email
import hashlib
import io
import json
import sys
import tarfile
import zipfile
from pathlib import Path, PurePosixPath


class PackageCheckError(ValueError):
    """Raised when a built distribution is unsafe or inconsistent."""


_FORBIDDEN_PARTS = {".git", ".env", "__pycache__", ".pytest_cache", "raw", "controlled"}
_FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".pem", ".key", ".p12", ".pfx"}
_REQUIRED_RUNTIME_ASSETS = {
    "catalog/data_sources.yml",
    "catalog/initiatives.yml",
    "conductor/roadmap.yml",
    "schemas/release-manifest.schema.json",
    "schemas/node-input.schema.json",
    "schemas/node-output.schema.json",
    "schemas/node-execution-manifest.schema.json",
    "schemas/node-disclosure-policy.schema.json",
    "schemas/transformation-run.schema.json",
    "examples/node-input-synthetic.yml",
    "examples/node-output-synthetic.yml",
    "docs/federated-node-004-operator-guide.md",
    "examples/fixtures/orphadata-synthetic.xml",
    "pyproject.toml",
    "uv.lock",
}


def _unsafe(name: str) -> bool:
    pure = PurePosixPath(name)
    return (
        not name
        or pure.is_absolute()
        or ".." in pure.parts
        or "\\" in name
        or any(part in _FORBIDDEN_PARTS for part in pure.parts)
        or pure.suffix.lower() in _FORBIDDEN_SUFFIXES
        or any(ord(character) < 32 for character in name)
    )


def _metadata_fields(content: bytes) -> dict[str, str]:
    message = email.message_from_bytes(content)
    return {key.lower(): value for key, value in message.items()}


def _sha256_urlsafe(data: bytes) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")


def _single_member(names: list[str], suffix: str, *, label: str) -> str:
    matches = [name for name in names if name.endswith(suffix)]
    if len(matches) != 1:
        raise PackageCheckError(f"wheel must contain exactly one {label} file")
    return matches[0]


def _validate_wheel_record(archive: zipfile.ZipFile, names: list[str], record_name: str) -> None:
    try:
        rows = list(csv.reader(io.StringIO(archive.read(record_name).decode("utf-8"))))
    except (KeyError, UnicodeDecodeError, csv.Error) as exc:
        raise PackageCheckError(f"cannot parse wheel RECORD: {exc}") from exc
    records: dict[str, tuple[str, str]] = {}
    for row in rows:
        if len(row) != 3 or not row[0] or row[0] in records:
            raise PackageCheckError("wheel RECORD contains malformed or duplicate entries")
        records[row[0]] = (row[1], row[2])
    if set(records) != set(names):
        missing = sorted(set(names) - set(records))
        extra = sorted(set(records) - set(names))
        raise PackageCheckError(f"wheel RECORD closure failed: missing={missing}; extra={extra}")
    for name in names:
        digest, declared_size = records[name]
        if name == record_name:
            if digest or declared_size:
                raise PackageCheckError("wheel RECORD self-entry must have empty hash and size")
            continue
        data = archive.read(name)
        if digest != f"sha256={_sha256_urlsafe(data)}":
            raise PackageCheckError(f"wheel RECORD hash mismatch: {name}")
        if declared_size != str(len(data)):
            raise PackageCheckError(f"wheel RECORD size mismatch: {name}")


def _validate_runtime_assets(archive: zipfile.ZipFile, names: list[str]) -> None:
    manifest_name = _single_member(
        names,
        "rareburden/resources/repository/runtime-assets.json",
        label="runtime-assets manifest",
    )
    prefix = manifest_name.removesuffix("runtime-assets.json")
    try:
        manifest = json.loads(archive.read(manifest_name).decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageCheckError(f"cannot parse runtime-assets manifest: {exc}") from exc
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, list) or manifest.get("file_count") != len(files):
        raise PackageCheckError("runtime-assets manifest has invalid file_count or files")
    logicals: set[str] = set()
    for raw in files:
        if not isinstance(raw, dict):
            raise PackageCheckError("runtime-assets manifest contains a malformed entry")
        logical = raw.get("path")
        digest = raw.get("sha256")
        size = raw.get("size_bytes")
        if not isinstance(logical, str) or _unsafe(logical) or logical in logicals:
            raise PackageCheckError(
                f"runtime-assets manifest has unsafe or duplicate path: {logical!r}"
            )
        member = prefix + logical
        if member not in names:
            raise PackageCheckError(f"runtime asset is missing from wheel: {logical}")
        data = archive.read(member)
        if digest != hashlib.sha256(data).hexdigest() or size != len(data):
            raise PackageCheckError(f"runtime asset hash or size mismatch: {logical}")
        logicals.add(logical)
    missing_required = sorted(_REQUIRED_RUNTIME_ASSETS - logicals)
    if missing_required:
        raise PackageCheckError(f"wheel omits required runtime assets: {missing_required}")


def inspect_wheel(path: Path, *, expected_name: str, expected_version: str) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise PackageCheckError("wheel contains duplicate member names")
            unsafe = [name for name in names if _unsafe(name)]
            if unsafe:
                raise PackageCheckError(f"wheel contains forbidden or unsafe members: {unsafe}")
            corrupt = archive.testzip()
            if corrupt is not None:
                raise PackageCheckError(f"wheel CRC verification failed: {corrupt}")
            metadata_name = _single_member(names, ".dist-info/METADATA", label="METADATA")
            wheel_name = _single_member(names, ".dist-info/WHEEL", label="WHEEL")
            record_name = _single_member(names, ".dist-info/RECORD", label="RECORD")
            fields = _metadata_fields(archive.read(metadata_name))
            wheel_fields = _metadata_fields(archive.read(wheel_name))
            _validate_wheel_record(archive, names, record_name)
            _validate_runtime_assets(archive, names)
    except PackageCheckError:
        raise
    except (OSError, zipfile.BadZipFile, KeyError) as exc:
        raise PackageCheckError(f"cannot inspect wheel {path}: {exc}") from exc
    normalised_expected = expected_name.lower().replace("_", "-")
    if fields.get("name", "").lower().replace("_", "-") != normalised_expected:
        raise PackageCheckError("wheel project name does not match expected name")
    if fields.get("version") != expected_version:
        raise PackageCheckError("wheel version does not match expected version")
    licence = fields.get("license-expression") or fields.get("license")
    if licence != "Apache-2.0":
        raise PackageCheckError("wheel must declare Apache-2.0 licence expression")
    if not wheel_fields.get("wheel-version", "").startswith("1."):
        raise PackageCheckError("wheel declares an unsupported Wheel-Version")
    if wheel_fields.get("root-is-purelib", "").lower() != "true":
        raise PackageCheckError("RareBurden wheel must be platform-independent pure Python")


def inspect_sdist(path: Path) -> None:
    required_suffixes = {
        "pyproject.toml",
        "src/rareburden/resources/repository/runtime-assets.json",
        "src/rareburden/verification.py",
        "README.md",
        "LICENSE",
    }
    try:
        with tarfile.open(path, "r:*") as archive:
            members = archive.getmembers()
            names = [member.name for member in members]
            if len(names) != len(set(names)):
                raise PackageCheckError("source distribution contains duplicate member names")
            roots = {PurePosixPath(member.name).parts[0] for member in members if member.name}
            if len(roots) != 1:
                raise PackageCheckError("source distribution must contain one top-level directory")
            root = next(iter(roots))
            for member in members:
                if _unsafe(member.name) or member.issym() or member.islnk() or member.isdev():
                    raise PackageCheckError(f"unsafe member in source distribution: {member.name}")
                if member.isfile() and member.size < 0:
                    raise PackageCheckError(
                        f"invalid member size in source distribution: {member.name}"
                    )
            missing = sorted(
                suffix for suffix in required_suffixes if f"{root}/{suffix}" not in names
            )
            if missing:
                raise PackageCheckError(f"source distribution omits required files: {missing}")
    except PackageCheckError:
        raise
    except (OSError, tarfile.TarError) as exc:
        raise PackageCheckError(f"cannot inspect source distribution {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--sdist", type=Path)
    parser.add_argument("--name", default="rareburden")
    parser.add_argument("--version")
    args = parser.parse_args()
    try:
        if args.wheel:
            if not args.version:
                parser.error("--version is required with --wheel")
            inspect_wheel(args.wheel, expected_name=args.name, expected_version=args.version)
        if args.sdist:
            inspect_sdist(args.sdist)
        if not args.wheel and not args.sdist:
            parser.error("at least one of --wheel or --sdist is required")
    except PackageCheckError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Built-package inspection passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
