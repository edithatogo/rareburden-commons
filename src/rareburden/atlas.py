"""Immutable aggregate projections for the Track 014 release surface."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from rareburden.provenance import content_id


class AtlasPackageError(ValueError):
    """Raised when a static/package projection is not release-safe."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ATLAS_RELEASE_FINGERPRINT = re.compile(r"^atlas-release-[0-9a-f]+$")
_RELEASE_DISPOSITIONS = {"correction", "withdrawal", "supersession"}


def _require_utc_timestamp(value: str) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise AtlasPackageError("effective_at must be an ISO-8601 UTC timestamp ending in Z")
    try:
        datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise AtlasPackageError("effective_at must be a valid ISO-8601 timestamp") from exc


def build_atlas_release_notice(
    candidate: Mapping[str, Any],
    *,
    notice_id: str,
    disposition: str,
    effective_at: str,
    reason: str,
    replacement_release_surface_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Create an immutable correction, withdrawal, or supersession notice.

    A notice records repository state only. It cannot authorize publication or
    mutate the candidate it references.
    """
    affected_fingerprint = candidate.get("release_surface_fingerprint")
    if (
        candidate.get("release_status") != "prepared"
        or candidate.get("publication_authorized") is not False
        or not isinstance(affected_fingerprint, str)
        or _ATLAS_RELEASE_FINGERPRINT.fullmatch(affected_fingerprint) is None
    ):
        raise AtlasPackageError("notice requires a valid prepared release candidate")
    if disposition not in _RELEASE_DISPOSITIONS:
        raise AtlasPackageError("unsupported release disposition")
    if (
        not isinstance(notice_id, str)
        or not notice_id.strip()
        or not isinstance(reason, str)
        or not reason.strip()
    ):
        raise AtlasPackageError("notice_id and reason are required")
    _require_utc_timestamp(effective_at)

    replacement_required = disposition in {"correction", "supersession"}
    if replacement_required and replacement_release_surface_fingerprint is None:
        raise AtlasPackageError(f"{disposition} requires a replacement release fingerprint")
    if replacement_release_surface_fingerprint is not None and (
        not isinstance(replacement_release_surface_fingerprint, str)
        or _ATLAS_RELEASE_FINGERPRINT.fullmatch(replacement_release_surface_fingerprint) is None
        or replacement_release_surface_fingerprint == affected_fingerprint
    ):
        raise AtlasPackageError("replacement must identify a different valid release surface")
    if disposition == "withdrawal" and replacement_release_surface_fingerprint is not None:
        raise AtlasPackageError("withdrawal cannot imply an unreviewed replacement")

    payload = {
        "schema_version": "0.1.0",
        "notice_id": notice_id,
        "disposition": disposition,
        "effective_at": effective_at,
        "reason": reason,
        "affected_release_id": candidate["release_id"],
        "affected_release_surface_fingerprint": affected_fingerprint,
        "replacement_release_surface_fingerprint": replacement_release_surface_fingerprint,
        "publication_authorized": False,
    }
    return {"notice_fingerprint": content_id("atlas-notice", payload), **payload}


def build_atlas_release_status(
    candidate: Mapping[str, Any], notices: list[Mapping[str, Any]]
) -> dict[str, Any]:
    """Project candidate lifecycle metadata for static and API consumers."""
    affected_fingerprint = candidate.get("release_surface_fingerprint")
    release_id = candidate.get("release_id")
    if (
        candidate.get("release_status") != "prepared"
        or candidate.get("publication_authorized") is not False
        or not isinstance(affected_fingerprint, str)
        or _ATLAS_RELEASE_FINGERPRINT.fullmatch(affected_fingerprint) is None
        or not isinstance(release_id, str)
        or not release_id.strip()
    ):
        raise AtlasPackageError("release status requires a valid prepared release candidate")
    if len(notices) > 1:
        raise AtlasPackageError("a candidate can have only one terminal lifecycle notice")

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for notice in notices:
        if notice.get("affected_release_surface_fingerprint") != affected_fingerprint:
            raise AtlasPackageError("release notice targets another candidate")
        notice_id = notice.get("notice_id")
        if not isinstance(notice_id, str) or notice_id in seen_ids:
            raise AtlasPackageError("release notices require unique notice IDs")
        expected = build_atlas_release_notice(
            candidate,
            notice_id=notice_id,
            disposition=str(notice.get("disposition", "")),
            effective_at=str(notice.get("effective_at", "")),
            reason=str(notice.get("reason", "")),
            replacement_release_surface_fingerprint=notice.get(
                "replacement_release_surface_fingerprint"
            ),
        )
        if dict(notice) != expected:
            raise AtlasPackageError("release notice fingerprint or content is invalid")
        seen_ids.add(notice_id)
        normalized.append(expected)

    normalized.sort(key=lambda item: (item["effective_at"], item["notice_id"]))
    latest = normalized[-1] if normalized else None
    status = "prepared" if latest is None else latest["disposition"]
    availability = "not_published" if latest is None else "do_not_use"
    text = (
        "Prepared release candidate; publication is not authorized."
        if latest is None
        else f"{status.title()} notice {latest['notice_id']}: {latest['reason']} Do not use."
    )
    payload = {
        "schema_version": "0.1.0",
        "release_id": release_id,
        "release_surface_fingerprint": affected_fingerprint,
        "release_status": status,
        "availability": availability,
        "publication_authorized": False,
        "notices": normalized,
        "text_alternative": text,
    }
    return {"status_fingerprint": content_id("atlas-status", payload), **payload}


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


def validate_accessibility_consistency(
    package: Mapping[str, Any],
    api_response: Mapping[str, Any],
    static_product_set: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate repository-owned accessibility and disclosure invariants.

    This checks the machine-readable design contract across projections. It
    does not assert keyboard, assistive-technology, or real-user conformance.
    """
    if package.get("missingness_policy") != "preserve_missing_not_zero":
        raise AtlasPackageError("accessibility check requires explicit missingness policy")
    if package.get("aggregate_only") is not True or api_response.get("read_only") is not True:
        raise AtlasPackageError("accessibility check requires aggregate-only read-only outputs")
    if api_response.get("rows") != package.get("rows"):
        raise AtlasPackageError("API rows differ from package rows")
    if api_response.get("package_fingerprint") != package.get("package_fingerprint"):
        raise AtlasPackageError("API package fingerprint differs")
    if static_product_set.get("package_fingerprint") != package.get("package_fingerprint"):
        raise AtlasPackageError("static product package fingerprint differs")
    products = static_product_set.get("products")
    if not isinstance(products, list) or len(products) != 3:
        raise AtlasPackageError("accessibility check requires three static products")
    for product in products:
        required = ("heading", "text_alternative", "limitations", "non_colour_status_labels")
        if any(not product.get(field) for field in required):
            raise AtlasPackageError("every static product requires accessible text and labels")
        if (
            product.get("aggregate_only") is not True
            or product.get("publication_authorized") is not False
        ):
            raise AtlasPackageError("static products must remain aggregate-only and unpublished")
        if product.get("rows") != package.get("rows"):
            raise AtlasPackageError("static product rows differ from package rows")
    return {
        "status": "repository_accessibility_contract_valid",
        "product_count": len(products),
        "package_fingerprint": package["package_fingerprint"],
        "missingness_policy": package["missingness_policy"],
        "human_conformance_assessed": False,
        "real_user_testing_observed": False,
    }


def build_static_gap_projection(
    package: Mapping[str, Any],
    candidate: Mapping[str, Any],
    status: Mapping[str, Any],
    *,
    page_id: str = "bounded-synthetic-gap",
) -> dict[str, Any]:
    """Project a prepared package into a static, non-publishable page model."""
    if not isinstance(page_id, str) or not page_id.strip():
        raise AtlasPackageError("static projection requires a page_id")
    if (
        package.get("package_type") != "aggregate_gap_map"
        or package.get("aggregate_only") is not True
    ):
        raise AtlasPackageError("static projection requires an aggregate gap package")
    if (
        candidate.get("package_fingerprint") != package.get("package_fingerprint")
        or candidate.get("release_id") != package.get("release_id")
        or candidate.get("publication_authorized") is not False
        or candidate.get("release_status") != "prepared"
    ):
        raise AtlasPackageError("static projection candidate differs from package")
    if (
        status.get("release_surface_fingerprint") != candidate.get("release_surface_fingerprint")
        or status.get("release_id") != candidate.get("release_id")
        or status.get("publication_authorized") is not False
    ):
        raise AtlasPackageError("static projection status differs from candidate")
    rows = package.get("rows")
    if not isinstance(rows, list) or not rows:
        raise AtlasPackageError("static projection requires rows")
    if any(row.get("sufficiency") != "not_assessed" for row in rows):
        raise AtlasPackageError("bounded static projection requires unassessed sufficiency")
    payload = {
        "static_schema_version": "0.1.0",
        "page_id": page_id,
        "release_id": package["release_id"],
        "source_manifest_id": package["source_manifest_id"],
        "package_fingerprint": package["package_fingerprint"],
        "release_surface_fingerprint": candidate["release_surface_fingerprint"],
        "status_fingerprint": status["status_fingerprint"],
        "lifecycle_status": status["release_status"],
        "availability": status["availability"],
        "publication_authorized": False,
        "aggregate_only": True,
        "missingness_policy": package["missingness_policy"],
        "rows": [dict(row) for row in rows],
        "limitations": list(package.get("limitations", [])),
        "text_alternative": status["text_alternative"],
    }
    return {"static_fingerprint": content_id("atlas-static", payload), **payload}


def build_static_product_set(
    package: Mapping[str, Any],
    candidate: Mapping[str, Any],
    status: Mapping[str, Any],
    *,
    country_scope_id: str,
    demonstrator_scope_id: str,
) -> dict[str, Any]:
    """Build bounded gap, synthetic-country, and demonstrator page models.

    The country scope must use the ISO 3166 user-assigned XAA-XZZ range so a
    synthetic fixture cannot be mistaken for a real geography.
    """
    if (
        not isinstance(country_scope_id, str)
        or re.fullmatch(r"X[A-Z]{2}", country_scope_id) is None
    ):
        raise AtlasPackageError("country scope must use a synthetic XAA-XZZ identifier")
    if not isinstance(demonstrator_scope_id, str) or not demonstrator_scope_id.strip():
        raise AtlasPackageError("demonstrator_scope_id is required")

    static = build_static_gap_projection(package, candidate, status)
    shared = {
        "availability": static["availability"],
        "publication_authorized": False,
        "aggregate_only": True,
        "estimate_status": "not_assessed",
        "rows": [dict(row) for row in static["rows"]],
        "limitations": [
            *static["limitations"],
            "Synthetic metadata-only design fixture; no empirical burden estimate is presented.",
            "Advisory accessibility/usability challenge and owner disposition remain pending.",
            "No actual user participation or independent review is claimed.",
        ],
        "non_colour_status_labels": [
            "Not assessed",
            "Synthetic only",
            "Not published",
        ],
    }
    definitions = (
        (
            "gap",
            "bounded-synthetic-gap",
            "public-data-gap",
            "Synthetic public-data gap product",
            "Gap product: all evidence sufficiency states are not assessed. "
            "No estimate is published.",
        ),
        (
            "country",
            f"bounded-synthetic-country-{country_scope_id.lower()}",
            country_scope_id,
            f"Synthetic country profile {country_scope_id}",
            f"Country profile {country_scope_id}: synthetic metadata-only fixture; "
            "all evidence sufficiency states are not assessed and no real geography "
            "is represented.",
        ),
        (
            "demonstrator",
            f"bounded-demonstrator-{demonstrator_scope_id}",
            demonstrator_scope_id,
            "Synthetic public-foundation demonstrator",
            "Demonstrator product: synthetic metadata-only fixture; no empirical "
            "validity, external review or publication is claimed.",
        ),
    )
    products: list[dict[str, Any]] = []
    for product_type, page_id, scope_id, heading, text_alternative in definitions:
        product = {
            "product_type": product_type,
            "page_id": page_id,
            "scope_id": scope_id,
            "heading": heading,
            **shared,
            "text_alternative": text_alternative,
        }
        products.append({"product_fingerprint": content_id("atlas-product", product), **product})

    payload = {
        "schema_version": "0.1.0",
        "release_id": static["release_id"],
        "source_manifest_id": static["source_manifest_id"],
        "package_fingerprint": static["package_fingerprint"],
        "release_surface_fingerprint": static["release_surface_fingerprint"],
        "status_fingerprint": static["status_fingerprint"],
        "publication_authorized": False,
        "aggregate_only": True,
        "synthetic_only": True,
        "missingness_policy": static["missingness_policy"],
        "products": products,
    }
    return {"product_set_fingerprint": content_id("atlas-product-set", payload), **payload}


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
    "build_atlas_release_notice",
    "build_atlas_release_status",
    "build_gap_api_response",
    "build_gap_package",
    "build_static_gap_projection",
    "build_static_product_set",
    "validate_accessibility_consistency",
]
