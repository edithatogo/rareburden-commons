#!/usr/bin/env python3
"""Validate public, immutable uv lockfile sources and project identity."""

from __future__ import annotations

import argparse
import ipaddress
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


class LockfilePolicyError(ValueError):
    """Raised when lockfile policy is violated."""


@dataclass(frozen=True)
class LockfileSummary:
    package_count: int
    registry_count: int
    distribution_url_count: int
    project_version: str | None


_PUBLIC_HOSTS = {"pypi.org", "files.pythonhosted.org"}
_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _is_private_host(host: str) -> bool:
    lowered = host.lower().rstrip(".")
    if lowered in {"localhost"} or lowered.endswith((".local", ".internal", ".localhost")):
        return True
    try:
        address = ipaddress.ip_address(lowered)
    except ValueError:
        return lowered not in _PUBLIC_HOSTS
    return not address.is_global


def _url_errors(url: str, *, label: str) -> list[str]:
    errors: list[str] = []
    parsed = urlparse(url)
    if parsed.scheme != "https":
        errors.append(f"{label}: only HTTPS URLs are permitted")
    if parsed.username or parsed.password:
        errors.append(f"{label}: credentials are forbidden in URLs")
    host = parsed.hostname or ""
    if not host or _is_private_host(host):
        errors.append(f"{label}: private or local host is forbidden: {host or '<missing>'}")
    return errors


def _pyproject_version(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        value = tomllib.loads(path.read_text(encoding="utf-8"))["project"]["version"]
    except (OSError, tomllib.TOMLDecodeError, KeyError, TypeError) as exc:
        raise LockfilePolicyError(f"Cannot read pyproject: {exc}") from exc
    if not isinstance(value, str):
        raise LockfilePolicyError("pyproject project.version must be a string")
    return value


def validate_lockfile(path: Path, pyproject: Path | None = None) -> LockfileSummary:
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise LockfilePolicyError(f"Cannot read lockfile: {exc}") from exc
    packages = document.get("package")
    if not isinstance(packages, list) or not packages:
        raise LockfilePolicyError("Cannot read lockfile package records")
    expected_project = _pyproject_version(pyproject)
    errors: list[str] = []
    registry_urls: set[str] = set()
    distribution_count = 0
    project_version: str | None = None
    identities: set[tuple[str, str]] = set()
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            errors.append(f"package[{index}] is not an object")
            continue
        name, version = package.get("name"), package.get("version")
        if not isinstance(name, str) or not isinstance(version, str):
            errors.append(f"package[{index}] lacks name or version")
            continue
        identity = (name.lower().replace("_", "-"), version)
        if identity in identities:
            errors.append(f"duplicate package identity: {name}=={version}")
        identities.add(identity)
        source = package.get("source")
        if not isinstance(source, dict):
            errors.append(f"{name}: source is missing")
            continue
        if name == "rareburden":
            project_version = version
            if source.get("editable") != ".":
                errors.append("rareburden project entry must be editable from '.'")
        registry = source.get("registry")
        if registry is not None:
            if not isinstance(registry, str):
                errors.append(f"{name}: registry must be a string")
            else:
                registry_urls.add(registry)
                errors.extend(_url_errors(registry, label=f"{name} registry"))
        for kind in ("sdist",):
            item = package.get(kind)
            if item is None:
                continue
            if not isinstance(item, dict):
                errors.append(f"{name}: {kind} is malformed")
                continue
            url, digest = item.get("url"), item.get("hash")
            if not isinstance(url, str):
                errors.append(f"{name}: {kind} URL is missing")
            else:
                errors.extend(_url_errors(url, label=f"{name} {kind}"))
                distribution_count += 1
            if not isinstance(digest, str) or not _HASH_RE.fullmatch(digest):
                errors.append(f"{name}: {kind} SHA-256 is missing or malformed")
        wheels = package.get("wheels", [])
        if not isinstance(wheels, list):
            errors.append(f"{name}: wheels must be a list")
            continue
        for wheel_index, item in enumerate(wheels):
            if not isinstance(item, dict):
                errors.append(f"{name}: wheel[{wheel_index}] is malformed")
                continue
            url, digest = item.get("url"), item.get("hash")
            if not isinstance(url, str):
                errors.append(f"{name}: wheel[{wheel_index}] URL is missing")
            else:
                errors.extend(_url_errors(url, label=f"{name} wheel[{wheel_index}]"))
                distribution_count += 1
            if not isinstance(digest, str) or not _HASH_RE.fullmatch(digest):
                errors.append(f"{name}: wheel[{wheel_index}] SHA-256 is missing or malformed")
    if expected_project is not None and project_version != expected_project:
        errors.append(
            f"lockfile project version {project_version!r} does not match "
            f"pyproject {expected_project!r}"
        )
    if errors:
        raise LockfilePolicyError("Lockfile policy failed:\n- " + "\n- ".join(sorted(set(errors))))
    return LockfileSummary(len(packages), len(registry_urls), distribution_count, project_version)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lockfile", type=Path, nargs="?", default=Path("uv.lock"))
    parser.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    args = parser.parse_args()
    try:
        summary = validate_lockfile(args.lockfile, args.pyproject)
    except LockfilePolicyError as exc:
        print(str(exc))
        return 1
    print(
        f"Lockfile passed: {summary.package_count} packages, "
        f"{summary.distribution_url_count} pinned distributions."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
