import copy
import json
from pathlib import Path

import pytest

from rareburden.atlas import (
    AtlasPackageError,
    build_atlas_release_candidate,
    build_atlas_release_notice,
    build_atlas_release_status,
    build_gap_api_response,
    build_gap_package,
    build_static_gap_projection,
)
from rareburden.gapmap import build_domain_gap_map
from rareburden.schema import load_mapping, validate_instance
from scripts.check_track014_release_surface import (
    ReleaseSurfaceError,
    validate_release_surface_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/atlas/track-014-bounded-release-surface-2026-08-16.json"
PLAN = ROOT / "conductor/tracks/014-atlas-api-release/plan.md"


def test_track014_plan_reconciles_bounded_work_without_closing_release_gates() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert plan.count("- [x]") == 23
    assert plan.count("- [ ]") == 10
    assert "Define user journeys" in plan
    assert "Complete accessibility design review" in plan
    assert "Add immutable archive/DOI" in plan
    assert "Publish v0.8 beta only after Track 013 approval" in plan
    assert "Activate real sources or publish any beta/stable surface" in plan
    assert "do not activate a hosted API or public atlas" in plan


def _surface() -> tuple[dict, dict, dict, dict]:
    gap_map = build_domain_gap_map(
        load_mapping(ROOT / "catalog/data_sources.yml"),
        load_mapping(ROOT / "examples/config/gap-map-needs.yml"),
    )
    package = build_gap_package(
        gap_map,
        release_id="track-014-synthetic-static-v1",
        source_manifest_id="track-013-bounded-reconciliation-2026-08-16",
    )
    api = build_gap_api_response(package)
    candidate = build_atlas_release_candidate(
        package,
        api,
        reviewed_artifacts=[
            {
                "artifact_id": "track-013-bounded-reconciliation",
                "sha256": "52f61977b932fb9162e60f8ebf210b72b4bacc3a15c8cd446b724a556982677e",
                "package_fingerprint": package["package_fingerprint"],
                "review_receipt_id": "track-013-repository-bounded-pass",
                "review_state": "repository_reviewed_bounded",
                "licence_state": "metadata_only",
            }
        ],
        citation_id="citation-track-014-synthetic",
        provenance_id="prov-track-014-synthetic",
    )
    status = build_atlas_release_status(candidate, [])
    static = build_static_gap_projection(package, candidate, status)
    return package, api, candidate, static


def test_static_package_api_and_status_share_exact_identity() -> None:
    package, api, candidate, static = _surface()
    assert static["publication_authorized"] is False
    assert static["availability"] == "not_published"
    assert (
        static["package_fingerprint"]
        == package["package_fingerprint"]
        == api["package_fingerprint"]
    )
    assert static["release_surface_fingerprint"] == candidate["release_surface_fingerprint"]
    assert all(row["sufficiency"] == "not_assessed" for row in static["rows"])
    validate_instance(static, load_mapping(ROOT / "schemas/atlas-static-projection.schema.json"))


def test_static_projection_carries_withdrawal_to_text_and_availability() -> None:
    package, _api, candidate, _static = _surface()
    notice = build_atlas_release_notice(
        candidate,
        notice_id="track-014-synthetic-withdrawal",
        disposition="withdrawal",
        effective_at="2026-08-16T00:00:00Z",
        reason="Synthetic exercise of the fail-closed withdrawal route.",
    )
    static = build_static_gap_projection(
        package, candidate, build_atlas_release_status(candidate, [notice])
    )
    assert static["lifecycle_status"] == "withdrawal"
    assert static["availability"] == "do_not_use"
    assert "Do not use" in static["text_alternative"]


def test_static_projection_rejects_identity_drift_and_sufficiency_upgrade() -> None:
    package, _api, candidate, _static = _surface()
    status = build_atlas_release_status(candidate, [])
    drifted = copy.deepcopy(package)
    drifted["rows"][0]["sufficiency"] = "sufficient"
    with pytest.raises(AtlasPackageError, match="unassessed sufficiency"):
        build_static_gap_projection(drifted, candidate, status)
    drifted_candidate = dict(candidate, publication_authorized=True)
    with pytest.raises(AtlasPackageError, match="differs from package"):
        build_static_gap_projection(package, drifted_candidate, status)


@pytest.mark.parametrize("page_id", ["", "   ", None])
def test_static_projection_requires_nonempty_string_page_id(page_id: object) -> None:
    package, _api, candidate, _static = _surface()
    status = build_atlas_release_status(candidate, [])
    with pytest.raises(AtlasPackageError, match="requires a page_id"):
        build_static_gap_projection(package, candidate, status, page_id=page_id)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value"),
    [("package_type", "raw_records"), ("aggregate_only", False)],
)
def test_static_projection_rejects_nonaggregate_packages(field: str, value: object) -> None:
    package, _api, candidate, _static = _surface()
    status = build_atlas_release_status(candidate, [])
    unsafe = dict(package, **{field: value})
    with pytest.raises(AtlasPackageError, match="aggregate gap package"):
        build_static_gap_projection(unsafe, candidate, status)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("package_fingerprint", "atlas-other"),
        ("release_id", "another-release"),
        ("publication_authorized", True),
        ("release_status", "published"),
    ],
)
def test_static_projection_rejects_candidate_identity_or_authority_drift(
    field: str, value: object
) -> None:
    package, _api, candidate, _static = _surface()
    status = build_atlas_release_status(candidate, [])
    unsafe = dict(candidate, **{field: value})
    with pytest.raises(AtlasPackageError, match="candidate differs from package"):
        build_static_gap_projection(package, unsafe, status)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("release_surface_fingerprint", "atlas-release-other"),
        ("release_id", "another-release"),
        ("publication_authorized", True),
    ],
)
def test_static_projection_rejects_status_identity_or_authority_drift(
    field: str, value: object
) -> None:
    package, _api, candidate, _static = _surface()
    status = build_atlas_release_status(candidate, [])
    unsafe = dict(status, **{field: value})
    with pytest.raises(AtlasPackageError, match="status differs from candidate"):
        build_static_gap_projection(package, candidate, unsafe)


@pytest.mark.parametrize("rows", [None, [], "not-a-row-list"])
def test_static_projection_requires_nonempty_row_list(rows: object) -> None:
    package, _api, candidate, _static = _surface()
    status = build_atlas_release_status(candidate, [])
    unsafe = dict(package, rows=rows)
    with pytest.raises(AtlasPackageError, match="requires rows"):
        build_static_gap_projection(unsafe, candidate, status)


def test_release_surface_manifest_binds_dependencies_and_gates() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = validate_release_surface_manifest(payload, ROOT)
    assert result["tracks"] == ["008", "009", "010", "011", "012", "013"]
    assert result["publication_authorized"] is False


def test_release_surface_manifest_rejects_hash_or_release_claim_drift() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["dependency_artifacts"][0]["sha256"] = "0" * 64
    with pytest.raises(ReleaseSurfaceError, match="hash mismatch"):
        validate_release_surface_manifest(payload, ROOT)
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["claims"]["public_release"] = True
    with pytest.raises(ReleaseSurfaceError, match="must remain false"):
        validate_release_surface_manifest(payload, ROOT)


def test_release_surface_manifest_rejects_scope_dependency_and_gate_drift() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["scope"] = "real_source_release"
    with pytest.raises(ReleaseSurfaceError, match="scope must remain synthetic"):
        validate_release_surface_manifest(payload, ROOT)

    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["dependency_artifacts"].append(copy.deepcopy(payload["dependency_artifacts"][0]))
    with pytest.raises(ReleaseSurfaceError, match="duplicate dependency"):
        validate_release_surface_manifest(payload, ROOT)

    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["dependency_artifacts"][0]["artifact"] = "../outside.json"
    with pytest.raises(ReleaseSurfaceError, match="unsafe dependency path"):
        validate_release_surface_manifest(payload, ROOT)

    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["dependency_artifacts"] = payload["dependency_artifacts"][1:]
    with pytest.raises(ReleaseSurfaceError, match="Tracks 008 through 013 exactly"):
        validate_release_surface_manifest(payload, ROOT)

    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["pending_gates"] = payload["pending_gates"][:-1]
    with pytest.raises(ReleaseSurfaceError, match="all release gates must remain pending"):
        validate_release_surface_manifest(payload, ROOT)
