"""Immutable aggregate projections for the Track 014 release surface."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from rareburden.provenance import content_id


class AtlasPackageError(ValueError):
    """Raised when a static/package projection is not release-safe."""


def build_gap_api_response(
    package: Mapping[str, Any], *, endpoint: str = "/v1/gaps"
) -> dict[str, Any]:
    """Build a read-only API-shaped response without enabling a network server."""
    if (
        package.get("package_type") != "aggregate_gap_map"
        or package.get("aggregate_only") is not True
    ):
        raise AtlasPackageError("API projection requires an aggregate gap package")
    if not isinstance(endpoint, str) or not endpoint.startswith("/"):
        raise AtlasPackageError("API endpoint must be a relative read-only path")
    rows = package.get("rows")
    if not isinstance(rows, list) or not rows:
        raise AtlasPackageError("API projection requires package rows")
    return {
        "api_schema_version": "0.1.0",
        "endpoint": endpoint,
        "read_only": True,
        "release_id": package.get("release_id"),
        "source_manifest_id": package.get("source_manifest_id"),
        "package_fingerprint": package.get("package_fingerprint"),
        "missingness_policy": package.get("missingness_policy"),
        "rows": [dict(row) for row in rows],
        "limitations": list(package.get("limitations", [])),
    }


def build_gap_package(
    gap_map: Mapping[str, Any], *, release_id: str, source_manifest_id: str
) -> dict[str, Any]:
    """Build a deterministic aggregate package projection from a validated gap map."""
    if not release_id.strip() or not source_manifest_id.strip():
        raise AtlasPackageError("release_id and source_manifest_id are required")
    rows = gap_map.get("rows")
    if not isinstance(rows, list) or not rows:
        raise AtlasPackageError("gap map must contain non-empty rows")
    if any(not isinstance(row, Mapping) for row in rows):
        raise AtlasPackageError("gap map rows must be mappings")
    payload = {
        "schema_version": "0.1.0",
        "package_type": "aggregate_gap_map",
        "release_id": release_id,
        "source_manifest_id": source_manifest_id,
        "aggregate_only": True,
        "missingness_policy": "preserve_missing_not_zero",
        "rows": [dict(row) for row in rows],
        "limitations": list(gap_map.get("limitations", [])),
    }
    return {"package_fingerprint": content_id("atlas", payload), **payload}


__all__ = ["AtlasPackageError", "build_gap_api_response", "build_gap_package"]
