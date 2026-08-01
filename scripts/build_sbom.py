#!/usr/bin/env python3
"""Generate a deterministic CycloneDX 1.5 SBOM from uv.lock."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
import uuid
from pathlib import Path
from typing import Any


class SbomError(ValueError):
    """Raised when a lockfile cannot be represented as an SBOM."""


def _normalise(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def build_sbom(
    lockfile: Path, *, name: str = "rareburden", version: str | None = None
) -> dict[str, Any]:
    try:
        document = tomllib.loads(lockfile.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SbomError(f"Cannot read lockfile: {exc}") from exc
    packages = document.get("package")
    if not isinstance(packages, list) or not packages:
        raise SbomError("Lockfile contains no package records")
    components: list[dict[str, str]] = []
    dependency_names: dict[str, list[str]] = {}
    refs: dict[str, str] = {}
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            raise SbomError(f"package[{index}] is not an object")
        raw_name, raw_version = package.get("name"), package.get("version")
        if not isinstance(raw_name, str) or not isinstance(raw_version, str):
            raise SbomError(f"package[{index}] lacks name or version")
        normalised = _normalise(raw_name)
        ref = f"pkg:pypi/{normalised}@{raw_version}"
        refs[normalised] = ref
        components.append(
            {
                "type": "library",
                "bom-ref": ref,
                "name": normalised,
                "version": raw_version,
                "purl": ref,
            }
        )
        dependencies = package.get("dependencies", [])
        if not isinstance(dependencies, list):
            raise SbomError(f"{raw_name}: dependencies must be a list")
        names: list[str] = []
        for item in dependencies:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                raise SbomError(f"{raw_name}: dependency record is malformed")
            names.append(_normalise(item["name"]))
        dependency_names[normalised] = sorted(set(names))
    components.sort(key=lambda item: (item["name"], item["version"]))
    dependencies = [
        {
            "ref": component["bom-ref"],
            "dependsOn": sorted(
                refs[item] for item in dependency_names[component["name"]] if item in refs
            ),
        }
        for component in components
    ]
    metadata_component = next(
        (item for item in components if item["name"] == _normalise(name)), None
    )
    if metadata_component is None:
        metadata_component = {
            "type": "application",
            "bom-ref": f"pkg:pypi/{_normalise(name)}@{version or 'unknown'}",
            "name": _normalise(name),
            "version": version or "unknown",
            "purl": f"pkg:pypi/{_normalise(name)}@{version or 'unknown'}",
        }
    canonical_identity = json.dumps(
        {"name": name, "version": version, "components": components, "dependencies": dependencies},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    serial_uuid = uuid.UUID(bytes=hashlib.sha256(canonical_identity).digest()[:16])
    return {
        "$schema": "https://cyclonedx.org/schema/bom-1.5.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{serial_uuid}",
        "version": 1,
        "metadata": {"component": metadata_component},
        "components": components,
        "dependencies": dependencies,
    }


def write_sbom(
    lockfile: Path, output: Path, *, name: str = "rareburden", version: str | None = None
) -> dict[str, Any]:
    document = build_sbom(lockfile, name=name, version=version)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", type=Path, default=Path("uv.lock"))
    parser.add_argument("--output", type=Path, default=Path("rareburden.cdx.json"))
    parser.add_argument("--name", default="rareburden")
    parser.add_argument("--version")
    args = parser.parse_args()
    try:
        document = write_sbom(args.lock, args.output, name=args.name, version=args.version)
    except SbomError as exc:
        print(str(exc))
        return 1
    print(f"SBOM written: {len(document['components'])} component(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
