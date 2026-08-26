"""Command-line interface for RareBurden programme and scientific utilities."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path
from typing import Any

from rareburden import __version__
from rareburden.acquisition import (
    AcquisitionError,
    DownloadPolicy,
    SourceChangedError,
    download_public_artifact,
    redact_url,
)
from rareburden.acquisition.adapters import (
    OrphadataXMLInvalid,
    PopulationCSVError,
    WHOCSVError,
    WorldBankPayloadError,
    build_indicator_url,
    normalise_indicator_json,
    normalise_orphadata_xml,
    normalise_population_csv,
    normalise_who_csv,
)
from rareburden.acquisition.normalise import (
    NormalisationError,
    build_dataset,
    validate_dataset,
    write_dataset,
)
from rareburden.burden import BurdenInputError, IntervalEstimate, expected_affected_population
from rareburden.burden_assurance import run_bounded_synthetic_analysis
from rareburden.catalog import CatalogValidationError, validate_catalog_files
from rareburden.gapmap import GapMapError, build_domain_gap_map, render_gap_map_markdown
from rareburden.landscape import (
    LandscapeValidationError,
    render_landscape_markdown,
    validate_landscape_files,
)
from rareburden.ledger import LedgerError, load_ledger
from rareburden.model import ModelError
from rareburden.paths import (
    MARKERS,
    PathDiscoveryError,
    discover_repository_root,
    is_repository_root,
    packaged_repository_root,
    resolve_output_path,
    resolve_repository_path,
)
from rareburden.provenance import (
    ProvenanceError,
    atomic_write_bytes,
    atomic_write_json,
    build_source_release,
    register_local_artifact,
    require_automated_acquisition_licence,
    utc_now,
    write_json_record,
)
from rareburden.quality import validate_quality_disposition
from rareburden.reference import ReferenceWorkflowError, run_public_foundation_reference
from rareburden.release import (
    ReleaseManifestError,
    build_release_manifest,
    verify_release_manifest,
)
from rareburden.roadmap import RoadmapValidationError, validate_roadmap_files
from rareburden.schema import (
    SchemaValidationError,
    load_mapping,
    validate_document_files,
    validate_instance,
)
from rareburden.semantics import (
    SemanticValidationError,
    load_hierarchy,
    load_mapping_set,
)
from rareburden.verification import ReferenceVerificationError, verify_reference_release


def _add_root_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        type=Path,
        help="RareBurden repository root; otherwise discover it from the current directory",
    )


def _add_json_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")


def _add_catalog_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--catalog", type=Path, help="source-catalogue YAML path")
    parser.add_argument("--catalog-schema", type=Path, help="data-source JSON Schema path")


def _add_landscape_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--landscape", type=Path, help="initiative-landscape YAML path")
    parser.add_argument(
        "--landscape-schema", type=Path, help="initiative-landscape JSON Schema path"
    )


def _add_roadmap_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--roadmap", type=Path, help="release-roadmap YAML path")
    parser.add_argument("--roadmap-schema", type=Path, help="roadmap JSON Schema path")
    parser.add_argument("--tracks-root", type=Path, help="Conductor tracks directory")
    parser.add_argument("--track-schema", type=Path, help="track-metadata JSON Schema path")


def build_parser() -> argparse.ArgumentParser:
    """Build the complete CLI parser without performing repository I/O."""
    parser = argparse.ArgumentParser(prog="rareburden")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("validate-catalog", "validate data-source metadata"),
        ("validate-roadmap", "validate the release and Conductor track graph"),
        ("validate-landscape", "validate the initiative and adjacency landscape"),
        ("validate-programme", "validate catalogue, roadmap, and landscape controls together"),
    ):
        subparser = subparsers.add_parser(name, help=help_text)
        _add_root_argument(subparser)
        if name in {"validate-catalog", "validate-programme"}:
            _add_catalog_arguments(subparser)
        if name in {"validate-roadmap", "validate-programme"}:
            _add_roadmap_arguments(subparser)
        if name in {"validate-landscape", "validate-programme"}:
            _add_landscape_arguments(subparser)
        _add_json_argument(subparser)

    render_landscape = subparsers.add_parser(
        "render-landscape", help="render the validated initiative landscape as Markdown"
    )
    _add_root_argument(render_landscape)
    _add_landscape_arguments(render_landscape)
    render_landscape.add_argument("--output", type=Path, required=True)
    _add_json_argument(render_landscape)

    doctor = subparsers.add_parser("doctor", help="report local repository and runtime health")
    _add_root_argument(doctor)
    _add_json_argument(doctor)

    validate_schema = subparsers.add_parser(
        "validate-document", help="validate one JSON or YAML document against a schema"
    )
    _add_root_argument(validate_schema)
    validate_schema.add_argument("--document", type=Path, required=True)
    validate_schema.add_argument("--schema", type=Path, required=True)
    _add_json_argument(validate_schema)

    register = subparsers.add_parser(
        "register-release", help="register an existing artefact without copying it"
    )
    _add_root_argument(register)
    _add_release_record_arguments(register, include_fetch=False)

    fetch = subparsers.add_parser(
        "fetch-release", help="download a checksum-pinned public artefact"
    )
    _add_root_argument(fetch)
    _add_release_record_arguments(fetch, include_fetch=True)

    normalise = subparsers.add_parser(
        "normalise-source", help="normalise a registered public-source fixture or release"
    )
    _add_root_argument(normalise)
    normalise.add_argument(
        "--adapter",
        required=True,
        choices=("world-bank", "population-csv", "who-csv", "orphadata"),
    )
    normalise.add_argument("--input", required=True, type=Path)
    normalise.add_argument("--source-release-id", required=True)
    normalise.add_argument("--acquisition-manifest-id", required=True)
    normalise.add_argument("--dataset-id", required=True)
    normalise.add_argument("--output", required=True, type=Path)
    normalise.add_argument("--columns", type=Path, help="YAML mapping for CSV source columns")
    normalise.add_argument("--indicator", help="World Bank indicator code")
    normalise.add_argument("--multiplier", type=float, default=1.0)
    normalise.add_argument("--source-id")
    normalise.add_argument("--geography-code-system", default="ISO3")
    _add_json_argument(normalise)

    world_bank = subparsers.add_parser(
        "world-bank-url", help="build a canonical World Bank Indicators API query"
    )
    world_bank.add_argument("--country", action="append", required=True)
    world_bank.add_argument("--indicator", required=True)
    world_bank.add_argument("--year-start", type=int, required=True)
    world_bank.add_argument("--year-end", type=int, required=True)
    world_bank.add_argument("--source", type=int, default=2)
    world_bank.add_argument("--per-page", type=int, default=20_000)
    _add_json_argument(world_bank)

    ledger = subparsers.add_parser("validate-ledger", help="validate an evidence parameter ledger")
    _add_root_argument(ledger)
    ledger.add_argument("--ledger", type=Path, required=True)
    ledger.add_argument("--schema", type=Path)
    _add_json_argument(ledger)

    hierarchy = subparsers.add_parser(
        "validate-hierarchy", help="validate a burden-purpose disease hierarchy and mapping set"
    )
    _add_root_argument(hierarchy)
    hierarchy.add_argument("--hierarchy", type=Path, required=True)
    hierarchy.add_argument("--hierarchy-schema", type=Path)
    hierarchy.add_argument("--mapping", type=Path)
    hierarchy.add_argument("--mapping-schema", type=Path)
    _add_json_argument(hierarchy)

    aggregate = subparsers.add_parser(
        "aggregate-hierarchy", help="sum an explicitly mutually-exclusive hierarchy contract"
    )
    _add_root_argument(aggregate)
    aggregate.add_argument("--hierarchy", type=Path, required=True)
    aggregate.add_argument("--hierarchy-schema", type=Path)
    aggregate.add_argument("--counts", type=Path, required=True)
    aggregate.add_argument("--output", type=Path)
    _add_json_argument(aggregate)

    analysis = subparsers.add_parser("run-analysis", help="run a seeded ledger-based analysis")
    _add_root_argument(analysis)
    analysis.add_argument("--ledger", type=Path, required=True)
    analysis.add_argument("--analysis", type=Path, required=True)
    analysis.add_argument(
        "--quality-disposition",
        type=Path,
        required=True,
        help="exact synthetic fitness-for-use disposition",
    )
    analysis.add_argument(
        "--source-release-bindings",
        type=Path,
        required=True,
        help="exact Track 009 source-release binding receipt",
    )
    analysis.add_argument("--output", type=Path)
    analysis.add_argument("--created-at", help="RFC 3339 timestamp for deterministic output")
    _add_json_argument(analysis)

    estimate = subparsers.add_parser(
        "estimate-cases", help="calculate a deterministic affected-population estimate"
    )
    estimate.add_argument("--population", type=float, required=True)
    estimate.add_argument("--population-lower", type=float)
    estimate.add_argument("--population-upper", type=float)
    estimate.add_argument("--fraction", type=float, required=True)
    estimate.add_argument("--fraction-lower", type=float)
    estimate.add_argument("--fraction-upper", type=float)
    _add_json_argument(estimate)

    gap = subparsers.add_parser(
        "generate-gap-map", help="generate an access-capability and evidence-gap map"
    )
    _add_root_argument(gap)
    gap.add_argument("--catalog", type=Path)
    gap.add_argument("--requirements", type=Path, required=True)
    gap.add_argument("--output-json", type=Path)
    gap.add_argument("--output-markdown", type=Path)
    _add_json_argument(gap)

    release = subparsers.add_parser(
        "build-release-manifest", help="hash and manifest a bounded set of release artefacts"
    )
    _add_root_argument(release)
    release.add_argument("--release-id", required=True)
    release.add_argument("--software-version", default=__version__)
    release.add_argument("--created-at", required=True)
    release.add_argument(
        "--release-kind",
        choices=("software", "data", "software_or_data", "synthetic_assurance", "documentation"),
        default="software_or_data",
    )
    release.add_argument(
        "--data-classification",
        choices=("public", "synthetic", "mixed_public_synthetic"),
        default="public",
    )
    release.add_argument("--output", type=Path, required=True)
    release.add_argument("--artefact", type=Path, action="append", required=True)
    _add_json_argument(release)

    verify = subparsers.add_parser(
        "verify-release-manifest", help="verify release artefacts against a manifest"
    )
    _add_root_argument(verify)
    verify.add_argument("--manifest", type=Path, required=True)
    _add_json_argument(verify)

    reference = subparsers.add_parser(
        "demo-public-foundation",
        help="run the complete offline synthetic public-foundation workflow",
    )
    _add_root_argument(reference)
    reference.add_argument("--output", type=Path, required=True)
    reference.add_argument("--created-at", help="RFC 3339 timestamp for deterministic output")
    reference.add_argument("--overwrite", action="store_true")
    _add_json_argument(reference)

    verify_reference = subparsers.add_parser(
        "verify-reference-release",
        help="independently verify a closed synthetic reference release",
    )
    _add_root_argument(verify_reference)
    verify_reference.add_argument("--release", type=Path, required=True)
    verify_reference.add_argument(
        "--verified-at",
        required=True,
        help="RFC 3339 verification timestamp recorded in the report",
    )
    verify_reference.add_argument(
        "--schema-root",
        type=Path,
        help="optional verification schema directory; defaults to materials/schemas in the release",
    )
    _add_json_argument(verify_reference)
    return parser


def _add_release_record_arguments(parser: argparse.ArgumentParser, *, include_fetch: bool) -> None:
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--url", "--source-url", dest="source_url", required=True)
    target = "--destination" if include_fetch else "--file"
    parser.add_argument(target, required=True, type=Path, dest="artefact")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--source-release-record", required=True, type=Path)
    parser.add_argument(
        "--licence-state",
        required=True,
        choices=("verified", "conditional", "unknown", "restricted", "not_applicable"),
    )
    parser.add_argument("--licence-reference")
    parser.add_argument("--notes", default="")
    if include_fetch:
        parser.add_argument("--allow-network", action="store_true")
        parser.add_argument("--allow-unpinned", action="store_true")
        parser.add_argument("--allow-insecure-http", action="store_true")
        parser.add_argument("--allow-private-network", action="store_true")
        parser.add_argument("--overwrite", action="store_true")
        parser.add_argument("--timeout", type=float, default=30.0)
        parser.add_argument("--retries", type=int, default=2)
        parser.add_argument("--max-bytes", type=int, default=2 * 1024 * 1024 * 1024)
        parser.add_argument(
            "--source-change-report",
            type=Path,
            help="write a review-required incident record when pinned bytes change",
        )
    _add_json_argument(parser)


def _repository_root(args: argparse.Namespace) -> Path:
    supplied = getattr(args, "root", None)
    if supplied is None:
        try:
            return discover_repository_root()
        except PathDiscoveryError:
            packaged = packaged_repository_root()
            if packaged is not None:
                return packaged
            raise
    if not isinstance(supplied, Path):
        raise PathDiscoveryError("--root must be a filesystem path")
    root = supplied.expanduser().resolve()
    if not is_repository_root(root):
        markers = ", ".join(str(marker) for marker in MARKERS)
        raise PathDiscoveryError(f"Not a RareBurden repository root: {root}; expected {markers}")
    return root


def _catalog_payload(args: argparse.Namespace, root: Path) -> dict[str, object]:
    summary = validate_catalog_files(
        resolve_repository_path(root, getattr(args, "catalog", None), "catalog/data_sources.yml"),
        resolve_repository_path(
            root, getattr(args, "catalog_schema", None), "schemas/data-source.schema.json"
        ),
    )
    return {
        "source_count": summary.source_count,
        "access_class_counts": summary.access_class_counts,
        "status_counts": summary.status_counts,
    }


def _roadmap_payload(args: argparse.Namespace, root: Path) -> dict[str, object]:
    summary = validate_roadmap_files(
        resolve_repository_path(root, getattr(args, "roadmap", None), "conductor/roadmap.yml"),
        resolve_repository_path(
            root, getattr(args, "roadmap_schema", None), "schemas/roadmap.schema.json"
        ),
        resolve_repository_path(root, getattr(args, "tracks_root", None), "conductor/tracks"),
        resolve_repository_path(
            root, getattr(args, "track_schema", None), "schemas/track-metadata.schema.json"
        ),
    )
    return {
        "release_count": summary.release_count,
        "track_count": summary.track_count,
        "v1_critical_track_count": summary.v1_critical_track_count,
        "current_release": summary.current_release,
        "track_status_counts": summary.track_status_counts,
    }


def _landscape_payload(args: argparse.Namespace, root: Path) -> dict[str, object]:
    summary = validate_landscape_files(
        resolve_repository_path(root, getattr(args, "landscape", None), "catalog/initiatives.yml"),
        resolve_repository_path(
            root,
            getattr(args, "landscape_schema", None),
            "schemas/initiative-landscape.schema.json",
        ),
    )
    return {
        "initiative_count": summary.initiative_count,
        "review_status": summary.review_status,
        "decision_outcome": summary.decision_outcome,
        "external_review_status": summary.external_review_status,
        "status_counts": summary.status_counts,
        "relationship_counts": summary.relationship_counts,
        "overlap_dimension_counts": summary.overlap_dimension_counts,
    }


def _render_landscape_payload(args: argparse.Namespace, root: Path) -> dict[str, object]:
    landscape_path = resolve_repository_path(
        root, getattr(args, "landscape", None), "catalog/initiatives.yml"
    )
    schema_path = resolve_repository_path(
        root,
        getattr(args, "landscape_schema", None),
        "schemas/initiative-landscape.schema.json",
    )
    summary = validate_landscape_files(landscape_path, schema_path)
    landscape = load_mapping(landscape_path)
    output = resolve_output_path(root, args.output)
    atomic_write_bytes(output, render_landscape_markdown(landscape).encode("utf-8"))
    return {
        "output": str(output),
        "initiative_count": summary.initiative_count,
        "decision_outcome": summary.decision_outcome,
    }


def _doctor_payload(root: Path) -> dict[str, object]:
    required = [
        "pyproject.toml",
        "uv.lock",
        "catalog/data_sources.yml",
        "catalog/initiatives.yml",
        "conductor/roadmap.yml",
        "schemas/data-source.schema.json",
        "schemas/initiative-landscape.schema.json",
        "schemas/acquisition-manifest.schema.json",
        "schemas/normalised-record.schema.json",
        "schemas/parameter-ledger.schema.json",
        "schemas/disease-hierarchy.schema.json",
        "schemas/ontology-mapping.schema.json",
    ]
    checks = {relative: (root / relative).is_file() for relative in required}
    supported_python = sys.version_info[:2] >= (3, 11)
    return {
        "ok": supported_python and all(checks.values()),
        "rareburden_version": __version__,
        "python": platform.python_version(),
        "python_supported": supported_python,
        "root": str(root),
        "files": checks,
    }


def _write_release_records(
    *,
    root: Path,
    manifest: dict[str, Any],
    manifest_path: Path,
    source_release_path: Path,
    source_id: str,
    release_id: str,
    source_url: str,
    licence_state: str,
    licence_reference: str | None,
    notes: str,
) -> dict[str, Any]:
    write_json_record(manifest, manifest_path, root / "schemas/acquisition-manifest.schema.json")
    record = build_source_release(
        source_id=source_id,
        release_id=release_id,
        source_url=source_url,
        licence_state=licence_state,
        licence_reference=licence_reference,
        acquisition_manifest=(
            manifest_path.relative_to(root).as_posix()
            if manifest_path.is_relative_to(root)
            else manifest_path.name
        ),
        notes=notes,
    )
    write_json_record(record, source_release_path, root / "schemas/source-release.schema.json")
    return {"manifest": manifest, "source_release": record}


def _release_record_payload(args: argparse.Namespace, root: Path, *, fetch: bool) -> dict[str, Any]:
    safe_source_url = redact_url(args.source_url)
    artefact_path = resolve_repository_path(root, args.artefact, str(args.artefact))
    manifest_path = resolve_repository_path(root, args.manifest, str(args.manifest))
    source_release_path = resolve_repository_path(
        root, args.source_release_record, str(args.source_release_record)
    )
    if fetch:
        require_automated_acquisition_licence(
            licence_state=args.licence_state,
            licence_reference=args.licence_reference,
            notes=args.notes,
        )
        policy = DownloadPolicy(
            timeout_seconds=args.timeout,
            retries=args.retries,
            max_bytes=args.max_bytes,
            allow_unpinned=args.allow_unpinned,
            allow_insecure_http=args.allow_insecure_http,
            allow_private_network=args.allow_private_network,
            overwrite=args.overwrite,
        )
        try:
            manifest = download_public_artifact(
                source_id=args.source_id,
                release_id=args.release_id,
                url=args.source_url,
                destination=artefact_path,
                expected_sha256=args.expected_sha256,
                policy=policy,
                allow_network=args.allow_network,
                repository_root=root,
                notes=args.notes,
            )
        except SourceChangedError as exc:
            if args.source_change_report is not None:
                report_path = resolve_repository_path(
                    root,
                    args.source_change_report,
                    str(args.source_change_report),
                )
                write_json_record(
                    exc.as_record(),
                    report_path,
                    root / "schemas/source-change-incident.schema.json",
                )
            raise
    else:
        manifest = register_local_artifact(
            source_id=args.source_id,
            release_id=args.release_id,
            source_url=safe_source_url,
            artifact_path=artefact_path,
            expected_sha256=args.expected_sha256,
            repository_root=root,
            notes=args.notes,
        )
    return _write_release_records(
        root=root,
        manifest=manifest,
        manifest_path=manifest_path,
        source_release_path=source_release_path,
        source_id=args.source_id,
        release_id=args.release_id,
        source_url=safe_source_url,
        licence_state=args.licence_state,
        licence_reference=args.licence_reference,
        notes=args.notes,
    )


def _normalise_payload(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    input_path = resolve_repository_path(root, args.input, str(args.input))
    columns = (
        load_mapping(resolve_repository_path(root, args.columns, str(args.columns)))
        if args.columns
        else None
    )
    if args.adapter == "world-bank":
        if not args.indicator:
            raise NormalisationError("--indicator is required for the world-bank adapter")
        observations = normalise_indicator_json(
            input_path,
            source_release_id=args.source_release_id,
            acquisition_manifest_id=args.acquisition_manifest_id,
            indicator=args.indicator,
        )
    elif args.adapter == "population-csv":
        if columns is None:
            raise NormalisationError("--columns is required for population-csv")
        observations = normalise_population_csv(
            input_path,
            source_release_id=args.source_release_id,
            acquisition_manifest_id=args.acquisition_manifest_id,
            columns={str(key): str(value) for key, value in columns.items()},
            multiplier=args.multiplier,
            source_id=args.source_id or "un-world-population-prospects",
            geography_code_system=args.geography_code_system,
        )
    elif args.adapter == "who-csv":
        if columns is None:
            raise NormalisationError("--columns is required for who-csv")
        observations = normalise_who_csv(
            input_path,
            source_release_id=args.source_release_id,
            acquisition_manifest_id=args.acquisition_manifest_id,
            columns={str(key): str(value) for key, value in columns.items()},
            source_id=args.source_id or "who-global-health-estimates",
            geography_code_system=args.geography_code_system,
        )
    else:
        observations = normalise_orphadata_xml(
            input_path,
            source_release_id=args.source_release_id,
            acquisition_manifest_id=args.acquisition_manifest_id,
        )
    transformation_id = str(observations[0]["transformation_id"])
    dataset = build_dataset(
        dataset_id=args.dataset_id,
        source_release_id=args.source_release_id,
        acquisition_manifest_id=args.acquisition_manifest_id,
        transformation_id=transformation_id,
        observations=observations,
    )
    validated = validate_dataset(dataset, root / "schemas/normalised-dataset.schema.json")
    output_path = resolve_output_path(root, args.output)
    write_dataset(validated, output_path)
    return {
        "dataset_id": validated["dataset_id"],
        "record_count": len(validated["observations"]),
        "transformation_id": transformation_id,
        "output": str(output_path),
    }


def _validate_ledger_payload(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    ledger_path = resolve_repository_path(root, args.ledger, str(args.ledger))
    schema_path = resolve_repository_path(root, args.schema, "schemas/parameter-ledger.schema.json")
    ledger = load_ledger(ledger_path, schema_path)
    return {"ledger_id": ledger.document["ledger_id"], "parameter_count": len(ledger.records)}


def _hierarchy_payload(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    hierarchy_path = resolve_repository_path(root, args.hierarchy, str(args.hierarchy))
    hierarchy_schema = resolve_repository_path(
        root, args.hierarchy_schema, "schemas/disease-hierarchy.schema.json"
    )
    hierarchy = load_hierarchy(hierarchy_path, hierarchy_schema)
    payload: dict[str, Any] = {
        "hierarchy_id": hierarchy.document["hierarchy_id"],
        "version": hierarchy.document["version"],
        "entity_count": len(hierarchy.entities),
        "aggregation_count": len(hierarchy.aggregations),
        "fingerprint": hierarchy.fingerprint,
    }
    if args.mapping is not None:
        mapping_path = resolve_repository_path(root, args.mapping, str(args.mapping))
        mapping_schema = resolve_repository_path(
            root, args.mapping_schema, "schemas/ontology-mapping.schema.json"
        )
        mapping = load_mapping_set(mapping_path, mapping_schema)
        payload["mapping"] = {
            "mapping_set_id": mapping.document["mapping_set_id"],
            "mapping_count": len(mapping.document["mappings"]),
            "fingerprint": mapping.fingerprint,
        }
    elif args.mapping_schema is not None:
        raise SemanticValidationError("--mapping-schema requires --mapping")
    return payload


def _aggregate_hierarchy_payload(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    hierarchy = load_hierarchy(
        resolve_repository_path(root, args.hierarchy, str(args.hierarchy)),
        resolve_repository_path(
            root, args.hierarchy_schema, "schemas/disease-hierarchy.schema.json"
        ),
    )
    request = load_mapping(resolve_repository_path(root, args.counts, str(args.counts)))
    required = {"aggregation_id", "unit", "require_complete", "counts"}
    missing = sorted(required - request.keys())
    extras = sorted(request.keys() - required)
    if missing:
        raise SemanticValidationError(
            "Aggregation request lacks required fields: " + ", ".join(missing)
        )
    if extras:
        raise SemanticValidationError(
            "Aggregation request contains unsupported fields: " + ", ".join(extras)
        )
    counts = request["counts"]
    if not isinstance(counts, dict):
        raise SemanticValidationError("Aggregation request counts must be a mapping")
    require_complete = request["require_complete"]
    if not isinstance(require_complete, bool):
        raise SemanticValidationError("Aggregation request require_complete must be boolean")
    result = hierarchy.aggregate_counts(
        str(request["aggregation_id"]),
        {str(key): value for key, value in counts.items()},
        unit=str(request["unit"]),
        require_complete=require_complete,
    )
    validate_instance(
        result,
        load_mapping(root / "schemas/semantic-aggregation-result.schema.json"),
        label="semantic_aggregation_result",
    )
    if args.output:
        atomic_write_json(resolve_output_path(root, args.output), result)
    return result


def _analysis_payload(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    ledger = load_ledger(
        resolve_repository_path(root, args.ledger, str(args.ledger)),
        root / "schemas/parameter-ledger.schema.json",
    )
    analysis_path = resolve_repository_path(root, args.analysis, str(args.analysis))
    specification = load_mapping(analysis_path)
    validate_instance(
        specification,
        load_mapping(root / "schemas/analysis-specification.schema.json"),
        label="analysis_specification",
    )
    disposition_path = resolve_repository_path(
        root,
        args.quality_disposition,
        str(args.quality_disposition),
    )
    disposition = validate_quality_disposition(
        load_mapping(disposition_path),
        load_mapping(root / "schemas/quality-disposition.schema.json"),
    )
    bindings_path = resolve_repository_path(
        root,
        args.source_release_bindings,
        str(args.source_release_bindings),
    )
    result = run_bounded_synthetic_analysis(
        specification,
        ledger,
        load_mapping(bindings_path),
        disposition,
        created_at=args.created_at or utc_now(),
    )
    schema_projection = dict(result)
    for field in (
        "source_release_binding_sha256",
        "contract_frozen",
        "empirical_parameter_activation",
        "summary_precision_decimal_places",
    ):
        schema_projection.pop(field)
    schema_projection["activation_state"] = "not_activated"
    validate_instance(
        schema_projection,
        load_mapping(root / "schemas/analysis-result.schema.json"),
        label="analysis_result",
    )
    if args.output:
        atomic_write_json(resolve_output_path(root, args.output), result)
    return result


def _estimate_payload(args: argparse.Namespace) -> dict[str, object]:
    result = expected_affected_population(
        IntervalEstimate(
            args.population,
            args.population_lower,
            args.population_upper,
            "people",
            "observed",
        ),
        IntervalEstimate(
            args.fraction,
            args.fraction_lower,
            args.fraction_upper,
            "proportion",
            "modelled",
        ),
    )
    return {
        "estimate": result.estimate,
        "lower": result.lower,
        "upper": result.upper,
        "unit": result.unit,
        "evidence_status": result.evidence_status,
        "warning": "Endpoint bounds do not encode correlation; use a registered simulation.",
    }


def _gap_payload(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    catalog = load_mapping(resolve_repository_path(root, args.catalog, "catalog/data_sources.yml"))
    requirements = load_mapping(
        resolve_repository_path(root, args.requirements, str(args.requirements))
    )
    gap_map = build_domain_gap_map(catalog, requirements)
    validate_instance(gap_map, load_mapping(root / "schemas/gap-map.schema.json"), label="gap_map")
    if args.output_json:
        atomic_write_json(resolve_output_path(root, args.output_json), gap_map)
    if args.output_markdown:
        output = resolve_output_path(root, args.output_markdown)
        atomic_write_bytes(output, render_gap_map_markdown(gap_map).encode("utf-8"))
    return gap_map


def _release_manifest_payload(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    output = resolve_output_path(root, args.output)
    artefacts = [resolve_repository_path(root, path, str(path)) for path in args.artefact]
    manifest = build_release_manifest(
        root=root,
        artefact_paths=artefacts,
        release_id=args.release_id,
        software_version=args.software_version,
        created_at=args.created_at,
        output_path=output,
        release_kind=args.release_kind,
        data_classification=args.data_classification,
    )
    validate_instance(
        manifest,
        load_mapping(root / "schemas/release-manifest.schema.json"),
        label="release_manifest",
    )
    return manifest


def _verify_release_payload(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    manifest_path = resolve_repository_path(root, args.manifest, str(args.manifest))
    manifest = load_mapping(manifest_path)
    validate_instance(
        manifest,
        load_mapping(root / "schemas/release-manifest.schema.json"),
        label="release_manifest",
    )
    failures = verify_release_manifest(root, manifest)
    if failures:
        raise ReleaseManifestError("Release verification failed:\n- " + "\n- ".join(failures))
    return {
        "ok": True,
        "release_id": manifest["release_id"],
        "artefact_count": len(manifest["artefacts"]),
    }


def _dispatch(args: argparse.Namespace) -> dict[str, Any]:
    command = str(args.command)
    if command == "estimate-cases":
        return _estimate_payload(args)
    if command == "world-bank-url":
        url = build_indicator_url(
            countries=args.country,
            indicator=args.indicator,
            year_start=args.year_start,
            year_end=args.year_end,
            source=args.source,
            per_page=args.per_page,
        )
        return {"url": url}

    root = _repository_root(args)
    if command == "validate-catalog":
        return _catalog_payload(args, root)
    if command == "validate-roadmap":
        return _roadmap_payload(args, root)
    if command == "validate-landscape":
        return _landscape_payload(args, root)
    if command == "render-landscape":
        return _render_landscape_payload(args, root)
    if command == "validate-programme":
        return {
            "catalog": _catalog_payload(args, root),
            "roadmap": _roadmap_payload(args, root),
            "landscape": _landscape_payload(args, root),
        }
    if command == "doctor":
        return _doctor_payload(root)
    if command == "validate-document":
        document_path = resolve_repository_path(root, args.document, str(args.document))
        schema_path = resolve_repository_path(root, args.schema, str(args.schema))
        validate_document_files(document_path, schema_path)
        return {"valid": True, "document": str(document_path), "schema": str(schema_path)}
    if command == "register-release":
        return _release_record_payload(args, root, fetch=False)
    if command == "fetch-release":
        return _release_record_payload(args, root, fetch=True)
    if command == "normalise-source":
        return _normalise_payload(args, root)
    if command == "validate-ledger":
        return _validate_ledger_payload(args, root)
    if command == "validate-hierarchy":
        return _hierarchy_payload(args, root)
    if command == "aggregate-hierarchy":
        return _aggregate_hierarchy_payload(args, root)
    if command == "run-analysis":
        return _analysis_payload(args, root)
    if command == "generate-gap-map":
        return _gap_payload(args, root)
    if command == "build-release-manifest":
        return _release_manifest_payload(args, root)
    if command == "verify-release-manifest":
        return _verify_release_payload(args, root)
    if command == "demo-public-foundation":
        output = resolve_output_path(root, args.output)
        return run_public_foundation_reference(
            root=root,
            output_directory=output,
            created_at=args.created_at,
            overwrite=bool(args.overwrite),
        ).as_dict()
    if command == "verify-reference-release":
        release_root = resolve_output_path(root, args.release)
        schema_root = (
            resolve_repository_path(root, args.schema_root, str(args.schema_root))
            if args.schema_root is not None
            else None
        )
        report = verify_reference_release(
            release_root,
            schema_root=schema_root,
            verified_at=args.verified_at,
        )
        if report["status"] != "passed":
            failures = report.get("failures", [])
            detail = "\n- ".join(str(item) for item in failures)
            raise ReferenceVerificationError(
                "Reference release verification failed" + (f":\n- {detail}" if detail else "")
            )
        return report
    raise ValueError(f"Unsupported command: {command}")


def _print_payload(command: str, payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    summaries = {
        "validate-catalog": lambda: f"Catalogue valid: {payload['source_count']} sources",
        "validate-roadmap": lambda: (
            f"Roadmap valid: {payload['track_count']} tracks across "
            f"{payload['release_count']} releases"
        ),
        "validate-landscape": lambda: (
            f"Landscape valid: {payload['initiative_count']} initiatives; "
            f"decision {payload['decision_outcome']}"
        ),
        "render-landscape": lambda: (
            f"Rendered {payload['initiative_count']} initiatives to {payload['output']}"
        ),
        "doctor": lambda: f"Environment healthy: {payload['ok']} ({payload['root']})",
        "validate-document": lambda: f"Document valid: {payload['document']}",
        "validate-ledger": lambda: (
            f"Ledger valid: {payload['ledger_id']} ({payload['parameter_count']} parameters)"
        ),
        "validate-hierarchy": lambda: (
            f"Hierarchy valid: {payload['hierarchy_id']} ({payload['entity_count']} entities)"
        ),
        "normalise-source": lambda: (
            f"Normalised {payload['record_count']} records to {payload['output']}"
        ),
        "verify-release-manifest": lambda: (
            f"Release {payload['release_id']} verified ({payload['artefact_count']} artefacts)"
        ),
        "world-bank-url": lambda: str(payload["url"]),
        "demo-public-foundation": lambda: (
            f"Reference workflow complete: {payload['generated_file_count']} files in "
            f"{payload['output_directory']}"
        ),
        "verify-reference-release": lambda: (
            f"Reference release verified: {payload['summary']['passed_count']}/"
            f"{payload['summary']['check_count']} gates passed"
        ),
    }
    if command in summaries:
        print(summaries[command]())
    elif command in {"register-release", "fetch-release"}:
        manifest = payload["manifest"]
        print(f"Registered {manifest['acquisition_id']}: {manifest['artifact']['sha256']}")
    elif command == "aggregate-hierarchy":
        print(
            f"Aggregated {payload['aggregation_id']}: {payload['value']} {payload['unit']} "
            f"({payload['coverage']})"
        )
    elif command == "estimate-cases":
        print(
            f"Estimated cases: {payload['estimate']} ({payload['lower']} to {payload['upper']}) "
            f"{payload['unit']}"
        )
    elif command == "run-analysis":
        summary = payload["summary"]
        print(f"Analysis {payload['analysis_id']}: median {summary['median']}")
    elif command == "build-release-manifest":
        print(f"Built release manifest {payload['release_manifest_id']}")
    elif command == "generate-gap-map":
        print(f"Generated gap map with {len(payload['rows'])} rows")
    else:
        print("Programme validation passed")


def main(argv: list[str] | None = None) -> int:
    """Run the RareBurden CLI and return a process-compatible status code."""
    args = build_parser().parse_args(argv)
    try:
        payload = _dispatch(args)
    except (
        AcquisitionError,
        BurdenInputError,
        CatalogValidationError,
        GapMapError,
        LandscapeValidationError,
        LedgerError,
        ModelError,
        NormalisationError,
        OrphadataXMLInvalid,
        PathDiscoveryError,
        PopulationCSVError,
        ProvenanceError,
        ReferenceWorkflowError,
        ReferenceVerificationError,
        ReleaseManifestError,
        RoadmapValidationError,
        SchemaValidationError,
        SemanticValidationError,
        WHOCSVError,
        WorldBankPayloadError,
        ValueError,
    ) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    _print_payload(str(args.command), payload, bool(args.json))
    return 0
