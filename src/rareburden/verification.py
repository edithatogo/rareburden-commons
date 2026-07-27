"""Independent structural verification for a RareBurden synthetic research release.

The verifier distrusts status fields in the package.  It reloads schemas, recomputes
content identities and checksums, reconstructs the workflow graph, re-runs deterministic
scientific products where possible, and verifies exact release closure.  A successful
report establishes internal auditability (R2), not independent scientific reproduction
or empirical validity.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from rareburden import __version__
from rareburden.acquisition.normalise import validate_observations
from rareburden.catalog import load_yaml
from rareburden.gapmap import build_domain_gap_map, render_gap_map_markdown
from rareburden.ledger import load_ledger
from rareburden.lineage import build_lineage_audit
from rareburden.model import run_analysis_spec
from rareburden.prov import verify_prov_bundle
from rareburden.provenance import (
    canonical_json_bytes,
    content_id,
    sha256_file,
    stable_identifier,
)
from rareburden.quality import (
    build_evidence_assessment,
    build_quality_disposition,
    build_transportability_assessment,
    validate_evidence_assessment,
    validate_quality_disposition,
    validate_transportability_assessment,
    verify_parameter_assessment_closure,
)
from rareburden.release import verify_release_manifest
from rareburden.reporting import verify_gather_checklist
from rareburden.reproducibility import verify_reproducibility_assessment
from rareburden.research_object import verify_process_run_crate
from rareburden.schema import load_mapping, validate_instance
from rareburden.transformation import verify_transformation_run
from rareburden.transparency import (
    verify_analysis_decision_log,
    verify_protocol_registration,
)
from rareburden.workflow import verify_workflow_run


class ReferenceVerificationError(ValueError):
    """Raised when a release cannot be read safely enough to verify."""


def _safe_relative(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or value.startswith("./")
        or "\\" in value
        or any(ord(character) < 32 for character in value)
    ):
        raise ReferenceVerificationError(f"Unsafe release path: {value!r}")
    return path.as_posix()


def _path(root: Path, value: str, *, require_file: bool = True) -> Path:
    logical = _safe_relative(value)
    candidate = root / logical
    if candidate.is_symlink():
        raise ReferenceVerificationError(f"Symlink is not permitted in release: {logical}")
    try:
        candidate.resolve().relative_to(root)
    except ValueError as exc:
        raise ReferenceVerificationError(f"Release path escapes root: {logical}") from exc
    if require_file and not candidate.is_file():
        raise ReferenceVerificationError(f"Required release file is missing: {logical}")
    return candidate


def _load_json(root: Path, value: str, *, require_canonical: bool = True) -> dict[str, Any]:
    path = _path(root, value)
    try:
        raw = path.read_bytes()
        parsed = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReferenceVerificationError(f"Cannot parse {value}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ReferenceVerificationError(f"JSON document is not an object: {value}")
    if require_canonical and raw != canonical_json_bytes(parsed):
        raise ReferenceVerificationError(f"JSON document is not canonical: {value}")
    return parsed


def _schema(schema_root: Path, name: str) -> dict[str, Any]:
    path = schema_root / name
    if path.is_symlink() or not path.is_file():
        raise ReferenceVerificationError(f"Verification schema is missing or unsafe: {name}")
    return load_mapping(path)


def _check(
    check_id: str,
    title: str,
    operation: Callable[[], Sequence[str] | None],
) -> dict[str, Any]:
    try:
        result = operation()
        failures = sorted({str(item) for item in (result or []) if str(item)})
    except Exception as exc:  # verification boundary: preserve all failures in report
        failures = [f"{type(exc).__name__}: {exc}"]
    return {
        "check_id": check_id,
        "title": title,
        "status": "passed" if not failures else "failed",
        "failures": failures,
    }


def _validate_document(
    root: Path,
    schema_root: Path,
    path: str,
    schema_name: str,
) -> list[str]:
    document = _load_json(root, path)
    validate_instance(document, _schema(schema_root, schema_name), label=path)
    return []


def _verify_release_closure(root: Path, manifest: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    declared = {
        str(item.get("path"))
        for item in manifest.get("artefacts", [])
        if isinstance(item, Mapping) and isinstance(item.get("path"), str)
    }
    actual: set[str] = set()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            failures.append(f"release contains a symlink: {path.relative_to(root).as_posix()}")
            continue
        if path.is_file():
            logical = path.relative_to(root).as_posix()
            if logical != "release-manifest.json":
                actual.add(logical)
    undeclared = sorted(actual - declared)
    missing = sorted(declared - actual)
    failures.extend(f"undeclared release file: {path}" for path in undeclared)
    failures.extend(f"declared release file is missing: {path}" for path in missing)
    return failures


def _verify_source_records(root: Path, schema_root: Path) -> list[str]:
    failures: list[str] = []
    acquisition_ids: set[str] = set()
    release_ids: set[str] = set()
    for path in sorted((root / "acquisition").glob("*.acquisition.json")):
        logical = path.relative_to(root).as_posix()
        record = _load_json(root, logical)
        validate_instance(record, _schema(schema_root, "acquisition-manifest.schema.json"), label=logical)
        identity = {
            "source_id": record["source_id"],
            "release_id": record["release_id"],
            "method": record["method"],
            "requested_url": record["requested_url"],
            "resolved_url": record["resolved_url"],
            "artifact": record["artifact"],
            "expected_sha256": record["pinning"]["expected_sha256"],
        }
        if record["acquisition_id"] != content_id("acq", identity):
            failures.append(f"acquisition content identifier mismatch: {logical}")
        if (
            record["pinning"]["status"] == "verified"
            and record["pinning"]["expected_sha256"] != record["artifact"]["sha256"]
        ):
            failures.append(f"verified checksum pin differs from artefact: {logical}")
        acquisition_ids.add(str(record["acquisition_id"]))

    for path in sorted((root / "acquisition").glob("*.release.json")):
        logical = path.relative_to(root).as_posix()
        record = _load_json(root, logical)
        validate_instance(record, _schema(schema_root, "source-release.schema.json"), label=logical)
        expected_id = stable_identifier(str(record["source_id"]), str(record["release_id"]), prefix="src")
        if record["source_release_id"] != expected_id:
            failures.append(f"source-release identifier mismatch: {logical}")
        acquisition_path = str(record["acquisition_manifest"])
        try:
            acquisition = _load_json(root, acquisition_path)
        except ReferenceVerificationError as exc:
            failures.append(str(exc))
            continue
        if acquisition.get("source_id") != record["source_id"]:
            failures.append(f"source-release/acquisition source mismatch: {logical}")
        if acquisition.get("release_id") != record["release_id"]:
            failures.append(f"source-release/acquisition release mismatch: {logical}")
        release_ids.add(str(record["source_release_id"]))

    if not acquisition_ids:
        failures.append("release contains no acquisition records")
    if not release_ids:
        failures.append("release contains no source-release records")
    return failures


def _verify_normalised_packages(root: Path, schema_root: Path) -> list[str]:
    failures: list[str] = []
    record_schema = _schema(schema_root, "normalised-record.schema.json")
    manifest_schema = _schema(schema_root, "normalisation-manifest.schema.json")
    acquisition_ids = {
        str(_load_json(root, path.relative_to(root).as_posix())["acquisition_id"])
        for path in (root / "acquisition").glob("*.acquisition.json")
    }
    source_release_ids = {
        str(_load_json(root, path.relative_to(root).as_posix())["source_release_id"])
        for path in (root / "acquisition").glob("*.release.json")
    }
    manifests = sorted((root / "normalised").glob("*.normalisation.json"))
    if not manifests:
        return ["release contains no normalisation manifests"]
    for path in manifests:
        logical = path.relative_to(root).as_posix()
        manifest = _load_json(root, logical)
        validate_instance(manifest, manifest_schema, label=logical)
        records_name = str(manifest["records_file"])
        if PurePosixPath(records_name).name != records_name:
            failures.append(f"normalisation records_file must be a basename: {logical}")
            continue
        records_path = path.parent / records_name
        if records_path.is_symlink() or not records_path.is_file():
            failures.append(f"normalised records are missing or unsafe: {records_name}")
            continue
        digest, size = sha256_file(records_path)
        if digest != manifest["records_sha256"]:
            failures.append(f"normalised checksum mismatch: {records_name}")
        if size != manifest["size_bytes"]:
            failures.append(f"normalised size mismatch: {records_name}")
        rows: list[dict[str, Any]] = []
        try:
            for number, line in enumerate(records_path.read_bytes().splitlines(), start=1):
                parsed = json.loads(line.decode("utf-8"))
                if not isinstance(parsed, dict):
                    failures.append(f"normalised row is not an object: {records_name}:{number}")
                    continue
                if line + b"\n" != canonical_json_bytes(parsed):
                    failures.append(f"normalised row is not canonical: {records_name}:{number}")
                rows.append(parsed)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            failures.append(f"cannot parse normalised package {records_name}: {exc}")
            continue
        try:
            ordered = validate_observations(rows, record_schema)
        except Exception as exc:
            failures.append(f"normalised record validation failed for {records_name}: {exc}")
            continue
        if rows != ordered:
            failures.append(f"normalised records are not in canonical identifier order: {records_name}")
        if len(rows) != manifest["record_count"]:
            failures.append(f"normalised record count mismatch: {records_name}")
        stable_core = {
            "record_count": manifest["record_count"],
            "records_sha256": manifest["records_sha256"],
            "size_bytes": manifest["size_bytes"],
            "acquisition_manifest_id": manifest["acquisition_manifest_id"],
            "transformation_id": manifest["transformation_id"],
            "record_schema": manifest["record_schema"],
            "records_file": manifest["records_file"],
        }
        if manifest["normalisation_manifest_id"] != content_id("norm", stable_core):
            failures.append(f"normalisation manifest identifier mismatch: {logical}")
        if manifest["acquisition_manifest_id"] not in acquisition_ids:
            failures.append(f"unknown acquisition id in normalisation manifest: {logical}")
        for row in rows:
            if row["acquisition_manifest_id"] != manifest["acquisition_manifest_id"]:
                failures.append(f"row acquisition lineage mismatch: {row['record_id']}")
            if row["transformation_id"] != manifest["transformation_id"]:
                failures.append(f"row transformation lineage mismatch: {row['record_id']}")
            if row["source_release_id"] not in source_release_ids:
                failures.append(f"unknown source-release id in row: {row['record_id']}")
    return sorted(set(failures))


def _verify_fitness_for_use(root: Path, schema_root: Path) -> tuple[list[str], dict[str, Any] | None]:
    """Rebuild quality records and verify parameter-to-assessment closure."""
    failures: list[str] = []
    evidence_schema = _schema(schema_root, "evidence-assessment.schema.json")
    transport_schema = _schema(schema_root, "transportability-assessment.schema.json")
    disposition_schema = _schema(schema_root, "quality-disposition.schema.json")
    disposition_path = "analysis/quality-disposition.json"
    disposition = _load_json(root, disposition_path)
    created_at = str(disposition["created_at"])

    evidence: list[dict[str, Any]] = []
    for name in ("population-parameter-assessment", "fraction-parameter-assessment"):
        output_path = f"analysis/evidence-assessments/{name}.json"
        recorded = _load_json(root, output_path)
        validate_evidence_assessment(recorded, evidence_schema)
        core = load_mapping(root / "materials/quality" / f"{name}.yml")
        rebuilt = validate_evidence_assessment(build_evidence_assessment(core), evidence_schema)
        if rebuilt != recorded:
            failures.append(f"evidence assessment does not reproduce: {output_path}")
        evidence.append(recorded)

    transport_output = "analysis/transportability-assessments/fraction-transportability-assessment.json"
    transport_recorded = _load_json(root, transport_output)
    validate_transportability_assessment(transport_recorded, transport_schema)
    transport_core = load_mapping(root / "materials/quality/fraction-transportability-assessment.yml")
    transport_rebuilt = validate_transportability_assessment(
        build_transportability_assessment(transport_core), transport_schema
    )
    if transport_rebuilt != transport_recorded:
        failures.append(f"transportability assessment does not reproduce: {transport_output}")

    validate_quality_disposition(
        disposition,
        disposition_schema,
        evidence_assessments=evidence,
        transportability_assessments=[transport_recorded],
    )
    specification = load_mapping(root / "materials/analysis/expected-population-synthetic.yml")
    ledger_document = load_mapping(root / "materials/analysis/public-foundation-synthetic-ledger.yml")
    closure = verify_parameter_assessment_closure(
        parameters=list(ledger_document["parameters"]),
        parameter_ids=[
            str(specification["left_parameter_id"]),
            str(specification["right_parameter_id"]),
        ],
        evidence_assessments=evidence,
        transportability_assessments=[transport_recorded],
        disposition=disposition,
    )
    failures.extend(closure)
    rebuilt_disposition = build_quality_disposition(
        analysis_id=str(specification["analysis_id"]),
        created_at=created_at,
        intended_use=str(specification["intended_use"]),
        evidence_assessments=evidence,
        transportability_assessments=[transport_recorded],
    )
    if rebuilt_disposition != disposition:
        failures.append("quality disposition does not reproduce from packaged assessments")
    return sorted(set(failures)), disposition


def _verify_scientific_products(root: Path, schema_root: Path) -> list[str]:
    failures: list[str] = []
    quality_failures, disposition = _verify_fitness_for_use(root, schema_root)
    failures.extend(quality_failures)
    analysis_path = "analysis/expected-population-synthetic.json"
    result = _load_json(root, analysis_path)
    validate_instance(result, _schema(schema_root, "analysis-result.schema.json"), label=analysis_path)
    ledger = load_ledger(
        root / "materials/analysis/public-foundation-synthetic-ledger.yml",
        schema_root / "parameter-ledger.schema.json",
    )
    specification = load_mapping(root / "materials/analysis/expected-population-synthetic.yml")
    rerun = run_analysis_spec(
        specification,
        ledger,
        created_at=str(result["created_at"]),
        quality_disposition=disposition,
    )
    comparable_keys = set(result) - {"runtime"}
    if {key: result[key] for key in comparable_keys} != {key: rerun[key] for key in comparable_keys}:
        failures.append("deterministic analysis does not reproduce from packaged materials")
    if result.get("runtime", {}).get("random_engine") != rerun.get("runtime", {}).get("random_engine"):
        failures.append("analysis random-engine identity differs from verifier")

    gap_path = "reports/public-data-gap-map.json"
    gap = _load_json(root, gap_path)
    validate_instance(gap, _schema(schema_root, "gap-map.schema.json"), label=gap_path)
    rebuilt_gap = build_domain_gap_map(
        load_yaml(root / "materials/catalog/data_sources.yml"),
        load_mapping(root / "materials/analysis/gap-map-needs.yml"),
    )
    if gap != rebuilt_gap:
        failures.append("gap map does not reproduce from packaged catalogue and requirements")
    markdown = _path(root, "reports/public-data-gap-map.md").read_text(encoding="utf-8")
    if markdown != render_gap_map_markdown(rebuilt_gap):
        failures.append("gap-map Markdown differs from deterministic rendering")
    return failures


def _verify_scholarly_assurance(root: Path, schema_root: Path) -> list[str]:
    failures: list[str] = []
    registration_path = "materials/protocols/protocol-registration.json"
    decision_path = "analysis/analysis-decision-log.json"
    workflow_path = "provenance/workflow-run.json"
    prov_path = "provenance/prov.jsonld"
    lineage_path = "provenance/lineage-audit.json"
    reporting_path = "reports/gather-checklist.json"
    reproducibility_path = "reproducibility-assessment.json"
    crate_path = "ro-crate-metadata.json"

    registration = _load_json(root, registration_path)
    validate_instance(
        registration,
        _schema(schema_root, "protocol-registration.schema.json"),
        label=registration_path,
    )
    failures.extend(verify_protocol_registration(registration, root=root))

    decisions = _load_json(root, decision_path)
    validate_instance(
        decisions,
        _schema(schema_root, "analysis-decision-log.schema.json"),
        label=decision_path,
    )
    failures.extend(
        verify_analysis_decision_log(
            decisions,
            expected_protocol_registration_id=str(registration["protocol_registration_id"]),
        )
    )

    run_paths = sorted((root / "provenance/runs").glob("*.json"))
    if not run_paths:
        failures.append("no transformation-run records are present")
    runs: list[dict[str, Any]] = []
    for path in run_paths:
        logical = path.relative_to(root).as_posix()
        run = _load_json(root, logical)
        validate_instance(run, _schema(schema_root, "transformation-run.schema.json"), label=logical)
        failures.extend(f"{logical}: {failure}" for failure in verify_transformation_run(run, artefact_roots=[root]))
        runs.append(run)

    workflow = _load_json(root, workflow_path)
    validate_instance(workflow, _schema(schema_root, "workflow-run.schema.json"), label=workflow_path)
    failures.extend(verify_workflow_run(root, workflow))

    prov = _load_json(root, prov_path)
    validate_instance(prov, _schema(schema_root, "prov-bundle.schema.json"), label=prov_path)
    failures.extend(verify_prov_bundle(prov, workflow=workflow, transformation_runs=runs))

    lineage = _load_json(root, lineage_path)
    validate_instance(lineage, _schema(schema_root, "lineage-audit.schema.json"), label=lineage_path)
    rebuilt_lineage = build_lineage_audit(
        root=root,
        release_id=str(lineage["release_id"]),
        transformation_runs=runs,
        expected_outputs=[str(item) for item in lineage["expected_outputs"]],
        created_at=str(lineage["created_at"]),
        exempt_outputs=[str(item) for item in lineage["exempt_outputs"]],
    )
    if lineage != rebuilt_lineage:
        failures.append("lineage audit differs from recomputed audit")

    reporting = _load_json(root, reporting_path)
    validate_instance(reporting, _schema(schema_root, "reporting-checklist.schema.json"), label=reporting_path)
    failures.extend(verify_gather_checklist(reporting, root=root))

    crate = _load_json(root, crate_path)
    validate_instance(crate, _schema(schema_root, "research-object-profile.schema.json"), label=crate_path)
    failures.extend(verify_process_run_crate(root, crate))

    reproducibility = _load_json(root, reproducibility_path)
    validate_instance(
        reproducibility,
        _schema(schema_root, "reproducibility-assessment.schema.json"),
        label=reproducibility_path,
    )
    failures.extend(
        verify_reproducibility_assessment(
            reproducibility,
            root=root,
            expected_release_id="public-foundation-synthetic",
            expected_workflow_run_id=str(workflow["workflow_run_id"]),
        )
    )
    return sorted(set(failures))


def verify_reference_release(
    root: Path,
    *,
    schema_root: Path | None = None,
    verified_at: str,
) -> dict[str, Any]:
    """Return a content-addressed verification report for a closed synthetic release."""
    requested_root = root.expanduser()
    if requested_root.is_symlink() or not requested_root.is_dir():
        raise ReferenceVerificationError(f"Release root is missing or unsafe: {root}")
    release_root = requested_root.resolve()
    requested_schemas = schema_root.expanduser() if schema_root is not None else release_root / "materials/schemas"
    if requested_schemas.is_symlink() or not requested_schemas.is_dir():
        raise ReferenceVerificationError(f"Schema root is missing or unsafe: {requested_schemas}")
    schemas = requested_schemas.resolve()

    manifest = _load_json(release_root, "release-manifest.json")
    checks = [
        _check(
            "release_manifest",
            "Release manifest schema, identities, checksums and summary",
            lambda: (
                validate_instance(
                    manifest,
                    _schema(schemas, "release-manifest.schema.json"),
                    label="release-manifest.json",
                ),
                *verify_release_manifest(release_root, manifest),
            )[1:],
        ),
        _check(
            "release_closure",
            "Every regular release file is declared and no symlink is present",
            lambda: _verify_release_closure(release_root, manifest),
        ),
        _check(
            "source_provenance",
            "Source acquisitions and releases have valid content identities",
            lambda: _verify_source_records(release_root, schemas),
        ),
        _check(
            "normalisation",
            "Normalised packages are canonical, schema-valid and lineage closed",
            lambda: _verify_normalised_packages(release_root, schemas),
        ),
        _check(
            "fitness_for_use",
            "Evidence quality, transportability and parameter-assessment closure reproduce",
            lambda: _verify_fitness_for_use(release_root, schemas)[0],
        ),
        _check(
            "scientific_reexecution",
            "Deterministic analysis and gap map reproduce from packaged materials",
            lambda: _verify_scientific_products(release_root, schemas),
        ),
        _check(
            "scholarly_assurance",
            "Protocol, decisions, transformations, workflow, PROV, lineage, reporting and crate",
            lambda: _verify_scholarly_assurance(release_root, schemas),
        ),
    ]
    failures = [f"{check['check_id']}: {failure}" for check in checks for failure in check["failures"]]
    core = {
        "release_id": str(manifest.get("release_id", "")),
        "release_manifest_id": str(manifest.get("release_manifest_id", "")),
        "software_version": str(manifest.get("software_version", "")),
        "verifier_version": __version__,
        "verified_at": verified_at,
        "verification_scope": "synthetic_reference_R2_structural_and_deterministic",
        "status": "passed" if not failures else "failed",
        "checks": checks,
        "summary": {
            "check_count": len(checks),
            "passed_count": sum(check["status"] == "passed" for check in checks),
            "failed_count": sum(check["status"] == "failed" for check in checks),
            "failure_count": len(failures),
        },
        "failures": failures,
        "claims": {
            "internal_auditability": not failures,
            "independent_reproduction": False,
            "external_replication": False,
            "empirical_validity": False,
            "external_approval": False,
        },
        "limitations": [
            "A passed report establishes internal structural and deterministic auditability only.",
            (
                "The verifier does not establish external preregistration, independent reproduction, "
                "empirical validity, custodian approval, or community governance."
            ),
        ],
    }
    return {
        "schema_version": "1.0.0",
        "verification_report_id": content_id("verify", core),
        **core,
    }


__all__ = [
    "ReferenceVerificationError",
    "verify_reference_release",
]
