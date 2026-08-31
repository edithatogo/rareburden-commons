"""Check retained dependency staging provenance offline; never fetch or install wheels."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

DEFAULT_RECORD = "manifests/node/track004-staging-provenance-20260831.json"
SOURCE_BASIS = "locked_url_and_sha256_not_observed_cache_origin"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _keys(value: Any, expected: set[str], label: str) -> None:
    require(isinstance(value, dict) and set(value) == expected, f"invalid {label} fields")


def _sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _relative(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and "\\" not in value
        and not PurePosixPath(value).is_absolute()
        and all(part not in {"", ".", ".."} for part in value.split("/"))
    )


def validate_record(record: Any, receipt_bytes: bytes, lock_bytes: bytes) -> None:
    """Validate byte bindings and declared lock provenance, not publisher permission."""
    _keys(
        record,
        {
            "schema_version",
            "receipt_path",
            "receipt_sha256",
            "lock_path",
            "lock_sha256",
            "artifacts",
        },
        "record",
    )
    require(record["schema_version"] == "1.0.0", "unsupported provenance schema")
    for field in ("receipt_path", "lock_path"):
        require(_relative(record[field]), "unsafe evidence path")
    require(record["receipt_sha256"] == digest(receipt_bytes), "receipt hash differs")
    require(record["lock_sha256"] == digest(lock_bytes), "lock hash differs")
    receipt = json.loads(receipt_bytes)
    lock = tomllib.loads(lock_bytes.decode("utf-8"))
    require(isinstance(receipt, dict), "invalid offline receipt")
    hashes = receipt.get("artifact_sha256")
    node = receipt.get("node_wheel")
    require(
        isinstance(hashes, dict) and isinstance(node, str) and node in hashes,
        "invalid receipt artifact inventory",
    )
    expected = {name: sha for name, sha in hashes.items() if name != node}
    require(
        bool(expected) and all(_sha(sha) for sha in expected.values()), "invalid dependency hashes"
    )
    require(
        type(receipt.get("dependency_wheel_count")) is int
        and receipt["dependency_wheel_count"] == len(expected),
        "dependency count differs",
    )
    artifacts = record["artifacts"]
    require(isinstance(artifacts, list), "artifacts must be an array")
    seen: set[str] = set()
    for artifact in artifacts:
        _keys(
            artifact,
            {
                "filename",
                "sha256",
                "name",
                "version",
                "source_registry",
                "source_url",
                "source_basis",
                "staging_event",
                "wheel_metadata",
                "transformation",
            },
            "artifact",
        )
        filename = artifact["filename"]
        require(
            isinstance(filename, str) and filename in expected and filename not in seen,
            "dependency inventory differs",
        )
        seen.add(filename)
        require(artifact["sha256"] == expected[filename], "dependency hash differs")
        require(artifact["source_basis"] == SOURCE_BASIS, "unsupported source-origin claim")
        require(artifact["transformation"] == "none", "unexpected wheel transformation")
        packages = [
            package
            for package in lock.get("package", [])
            if package.get("name") == artifact["name"]
            and package.get("version") == artifact["version"]
        ]
        require(len(packages) == 1, "locked package identity differs")
        package = packages[0]
        require(
            artifact["source_registry"] == package.get("source", {}).get("registry")
            and isinstance(artifact["source_registry"], str),
            "registry differs",
        )
        require(isinstance(artifact["source_url"], str), "invalid source URL")
        matches = [
            wheel
            for wheel in package.get("wheels", [])
            if wheel.get("url") == artifact["source_url"]
            and wheel.get("hash") == "sha256:" + expected[filename]
        ]
        require(
            len(matches) == 1
            and PurePosixPath(unquote(urlsplit(artifact["source_url"]).path)).name == filename,
            "locked wheel URL or hash differs",
        )
        event = artifact["staging_event"]
        _keys(event, {"observed_on", "cache_use", "original_retrieval"}, "staging event")
        require(isinstance(event["observed_on"], str), "invalid staging observation date")
        require(
            date.fromisoformat(event["observed_on"]).isoformat() == event["observed_on"],
            "invalid staging observation date",
        )
        require(
            event["cache_use"] is True and event["original_retrieval"] == "unknown",
            "unsupported original retrieval claim",
        )
        metadata = artifact["wheel_metadata"]
        _keys(
            metadata,
            {"sha256", "licence_expression", "licence_text", "licence_files"},
            "wheel metadata",
        )
        require(_sha(metadata["sha256"]), "invalid metadata hash")
        for field in ("licence_expression", "licence_text"):
            require(
                metadata[field] is None or isinstance(metadata[field], str),
                "invalid observed licence metadata",
            )
        require(isinstance(metadata["licence_files"], list), "invalid licence file inventory")
        licence_names: set[str] = set()
        for item in metadata["licence_files"]:
            _keys(item, {"path", "sha256"}, "licence file")
            require(
                _relative(item["path"])
                and item["path"] not in licence_names
                and _sha(item["sha256"]),
                "invalid licence file identity",
            )
            licence_names.add(item["path"])
    require(seen == set(expected), "dependency inventory differs")


def _read(root: Path, relative: str) -> bytes:
    require(_relative(relative), "unsafe evidence path")
    path = root / relative
    require(
        not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),
        "evidence path escapes root",
    )
    return path.read_bytes()


def validate(root: Path, record_path: str = DEFAULT_RECORD) -> None:
    record = json.loads(_read(root, record_path))
    require(isinstance(record, dict), "invalid provenance record")
    validate_record(
        record, _read(root, record.get("receipt_path")), _read(root, record.get("lock_path"))
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", nargs="?", default=DEFAULT_RECORD)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    validate(args.root, args.record)
    print("Retained node dependency staging provenance passed (no network or execution).")


if __name__ == "__main__":
    main()
