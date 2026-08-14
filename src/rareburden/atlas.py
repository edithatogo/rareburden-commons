"""Immutable aggregate projections for the Track 014 release surface."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from rareburden.provenance import content_id


class AtlasPackageError(ValueError):
    """Raised when a static/package projection is not release-safe."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def build_atlas_release_candidate(
    package: Mapping[str, Any],
    api_response: Mapping[str, Any],
    *,
    reviewed_artifacts: list[Mapping[str, Any]],
    citation_id: str,
    provenance_id: str,
) -> dict[str, Any]:
    """Bind reviewed aggregate projections into a non-publishable candidate.

    This repository-owned boundary proves identity, parity and explicit rights
    disposition. It deliberately cannot authorize publication or represent an
    independent review.
    """
    if (
        package.get("package_type") != "aggregate_gap_map"
        or package.get("aggregate_only") is not True
    ):
        raise AtlasPackageError("release candidate requires an aggregate gap package")
    if api_response.get("read_only") is not True:
        raise AtlasPackageError("release candidate requires a read-only API projection")
    parity_fields = (
        "release_id",
        "source_manifest_id",
        "package_fingerprint",
        "missingness_policy",
        "rows",
        "limitations",
    )
    if any(api_response.get(field) != package.get(field) for field in parity_fields):
        raise AtlasPackageError("package and API projection differ")
    if not citation_id.strip() or not provenance_id.strip():
        raise AtlasPackageError("citation_id and provenance_id are required")
    if not reviewed_artifacts:
        raise AtlasPackageError("at least one reviewed artifact is required")

    artifacts: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, artifact in enumerate(reviewed_artifacts):
        artifact_id = artifact.get("artifact_id")
        receipt_id = artifact.get("review_receipt_id")
        digest = artifact.get("sha256")
        if not isinstance(artifact_id, str) or not artifact_id.strip():
            raise AtlasPackageError(f"reviewed artifact {index} has no artifact_id")
        if artifact_id in seen_ids:
            raise AtlasPackageError(f"duplicate reviewed artifact_id: {artifact_id}")
        if not isinstance(receipt_id, str) or not receipt_id.strip():
            raise AtlasPackageError(f"reviewed artifact {artifact_id} has no review receipt")
        if artifact.get("review_state") != "repository_reviewed_bounded":
            raise AtlasPackageError(f"reviewed artifact {artifact_id} is not repository reviewed")
        if artifact.get("licence_state") not in {"redistributable", "metadata_only"}:
            raise AtlasPackageError(f"reviewed artifact {artifact_id} has unresolved licence state")
        if artifact.get("package_fingerprint") != package.get("package_fingerprint"):
            raise AtlasPackageError(f"reviewed artifact {artifact_id} targets another package")
        if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
            raise AtlasPackageError(f"reviewed artifact {artifact_id} has invalid sha256")
        seen_ids.add(artifact_id)
        artifacts.append(dict(artifact))

    payload = {
        "schema_version": "0.1.0",
        "release_status": "prepared",
        "publication_authorized": False,
        "review_boundary": "repository_reviewed_inputs_only",
        "release_id": package["release_id"],
        "source_manifest_id": package["source_manifest_id"],
        "package_fingerprint": package["package_fingerprint"],
        "citation_id": citation_id,
        "provenance_id": provenance_id,
        "missingness_policy": package["missingness_policy"],
        "reviewed_artifacts": sorted(artifacts, key=lambda item: str(item["artifact_id"])),
        "pending_gates": [
            "accessibility",
            "independent_reproduction",
            "release_authority",
        ],
    }
    return {
        "release_surface_fingerprint": content_id("atlas-release", payload),
        **payload,
    }


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


__all__ = [
    "AtlasPackageError",
    "build_atlas_release_candidate",
    "build_gap_api_response",
    "build_gap_package",
]
