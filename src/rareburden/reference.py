"""Offline, end-to-end reference workflow for the public-data foundation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rareburden import __version__
from rareburden.assurance import (
    ScholarlyAssuranceError,
    ScholarlyAssuranceResult,
    build_reference_scholarly_assurance,
)
from rareburden.acquisition.adapters import (
    normalise_indicator_json,
    normalise_orphadata_xml,
    normalise_population_csv,
    normalise_who_csv,
)
from rareburden.acquisition.normalise import write_record_package
from rareburden.catalog import load_yaml
from rareburden.gapmap import build_domain_gap_map, render_gap_map_markdown
from rareburden.ledger import load_ledger
from rareburden.model import run_analysis_spec
from rareburden.quality import (
    build_evidence_assessment,
    build_quality_disposition,
    build_transportability_assessment,
    validate_evidence_assessment,
    validate_quality_disposition,
    validate_transportability_assessment,
    verify_parameter_assessment_closure,
)
from rareburden.provenance import (
    atomic_write_bytes,
    atomic_write_json,
    build_source_release,
    register_local_artifact,
    sha256_file,
    utc_now,
    write_json_record,
)
from rareburden.release import build_release_manifest, verify_release_manifest
from rareburden.reproducibility import verify_reproducibility_assessment
from rareburden.schema import load_mapping, validate_instance


class ReferenceWorkflowError(RuntimeError):
    """Raised when the offline reference workflow cannot complete safely."""


@dataclass(frozen=True)
class ReferenceWorkflowResult:
    """Paths and key outputs from a completed reference workflow."""

    output_directory: Path
    release_manifest_path: Path
    analysis_result_path: Path
    gap_map_path: Path
    generated_files: tuple[Path, ...]
    analysis_result: dict[str, Any]
    release_manifest: dict[str, Any]
    scholarly_assurance: ScholarlyAssuranceResult

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible summary with paths relative to the output directory."""
        return {
            "output_directory": str(self.output_directory),
            "release_manifest": self.release_manifest_path.relative_to(
                self.output_directory
            ).as_posix(),
            "analysis_result": self.analysis_result_path.relative_to(
                self.output_directory
            ).as_posix(),
            "gap_map": self.gap_map_path.relative_to(self.output_directory).as_posix(),
            "generated_file_count": len(self.generated_files),
            "analysis": self.analysis_result,
            "release_manifest_id": self.release_manifest["release_manifest_id"],
            "scholarly_assurance": self.scholarly_assurance.summary(self.output_directory),
        }


@dataclass(frozen=True)
class _FixtureSource:
    source_id: str
    release_id: str
    fixture_relative: str
    source_url: str


@dataclass(frozen=True)
class _QualityArtifacts:
    evidence_assessments: tuple[dict[str, Any], ...]
    transportability_assessments: tuple[dict[str, Any], ...]
    disposition: dict[str, Any]
    evidence_paths: tuple[Path, ...]
    transportability_paths: tuple[Path, ...]
    disposition_path: Path

    @property
    def generated_files(self) -> tuple[Path, ...]:
        return (*self.evidence_paths, *self.transportability_paths, self.disposition_path)


_FIXTURE_SOURCES = (
    _FixtureSource(
        "orphadata-science",
        "synthetic-2026-07",
        "examples/fixtures/orphadata-synthetic.xml",
        "https://example.org/rareburden/orphadata-synthetic.xml",
    ),
    _FixtureSource(
        "un-world-population-prospects",
        "synthetic-2026-07",
        "examples/fixtures/un-wpp-synthetic.csv",
        "https://example.org/rareburden/un-wpp-synthetic.csv",
    ),
    _FixtureSource(
        "who-global-health-estimates",
        "synthetic-2026-07",
        "examples/fixtures/who-ghe-synthetic.csv",
        "https://example.org/rareburden/who-ghe-synthetic.csv",
    ),
    _FixtureSource(
        "world-bank-indicators",
        "synthetic-2026-07",
        "examples/fixtures/world-bank-synthetic.json",
        "https://example.org/rareburden/world-bank-synthetic.json",
    ),
)


def _prepare_output_directory(output_directory: Path, *, overwrite: bool) -> Path:
    output = output_directory.expanduser().resolve()
    if output.is_symlink():
        raise ReferenceWorkflowError(f"Refusing symlink output directory: {output}")
    if output.exists() and any(output.iterdir()) and not overwrite:
        raise ReferenceWorkflowError(
            f"Output directory is not empty: {output}; use overwrite only for disposable outputs"
        )
    output.mkdir(parents=True, exist_ok=True)
    for name in (
        "acquisition",
        "normalised",
        "analysis",
        "analysis/evidence-assessments",
        "analysis/transportability-assessments",
        "reports",
    ):
        (output / name).mkdir(parents=True, exist_ok=True)
    return output


def _register_fixtures(
    *, root: Path, output: Path, created_at: str
) -> tuple[dict[str, dict[str, Any]], list[Path]]:
    records: dict[str, dict[str, Any]] = {}
    generated: list[Path] = []
    acquisition_schema = root / "schemas/acquisition-manifest.schema.json"
    source_release_schema = root / "schemas/source-release.schema.json"
    for source in _FIXTURE_SOURCES:
        fixture = root / source.fixture_relative
        digest, _ = sha256_file(fixture)
        manifest = register_local_artifact(
            source_id=source.source_id,
            release_id=source.release_id,
            source_url=source.source_url,
            artifact_path=fixture,
            expected_sha256=digest,
            repository_root=root,
            notes="Synthetic, non-empirical fixture used only for offline workflow assurance.",
            retrieved_at=created_at,
        )
        manifest_path = output / "acquisition" / f"{source.source_id}.acquisition.json"
        write_json_record(manifest, manifest_path, acquisition_schema)
        source_release = build_source_release(
            source_id=source.source_id,
            release_id=source.release_id,
            source_url=source.source_url,
            licence_state="not_applicable",
            licence_reference=None,
            acquisition_manifest=manifest_path.relative_to(output).as_posix(),
            notes="Synthetic fixture; not an official custodian release.",
            registered_at=created_at,
        )
        source_release_path = output / "acquisition" / f"{source.source_id}.release.json"
        write_json_record(source_release, source_release_path, source_release_schema)
        records[source.source_id] = {
            "fixture": fixture,
            "manifest": manifest,
            "source_release": source_release,
        }
        generated.extend((manifest_path, source_release_path))
    return records, generated


def _normalised_records(
    *, root: Path, fixture_records: dict[str, dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    def identifiers(source_id: str) -> tuple[str, str]:
        source = fixture_records[source_id]
        return (
            str(source["source_release"]["source_release_id"]),
            str(source["manifest"]["acquisition_id"]),
        )

    orpha_release, orpha_manifest = identifiers("orphadata-science")
    un_release, un_manifest = identifiers("un-world-population-prospects")
    who_release, who_manifest = identifiers("who-global-health-estimates")
    world_bank_release, world_bank_manifest = identifiers("world-bank-indicators")
    return {
        "orphadata-science": normalise_orphadata_xml(
            root / "examples/fixtures/orphadata-synthetic.xml",
            source_release_id=orpha_release,
            acquisition_manifest_id=orpha_manifest,
        ),
        "un-world-population-prospects": normalise_population_csv(
            root / "examples/fixtures/un-wpp-synthetic.csv",
            source_release_id=un_release,
            acquisition_manifest_id=un_manifest,
            columns={
                str(key): str(value)
                for key, value in load_mapping(
                    root / "examples/config/un-wpp-columns.yml"
                ).items()
            },
            multiplier=1000.0,
            geography_code_system="UN_M49",
        ),
        "who-global-health-estimates": normalise_who_csv(
            root / "examples/fixtures/who-ghe-synthetic.csv",
            source_release_id=who_release,
            acquisition_manifest_id=who_manifest,
            columns={
                str(key): str(value)
                for key, value in load_mapping(
                    root / "examples/config/who-ghe-columns.yml"
                ).items()
            },
        ),
        "world-bank-indicators": normalise_indicator_json(
            root / "examples/fixtures/world-bank-synthetic.json",
            source_release_id=world_bank_release,
            acquisition_manifest_id=world_bank_manifest,
            indicator="NY.GDP.PCAP.CD",
        ),
    }


def _write_normalised_packages(
    *, root: Path, output: Path, records: dict[str, list[dict[str, Any]]], created_at: str
) -> list[Path]:
    generated: list[Path] = []
    for source_id, source_records in sorted(records.items()):
        first = source_records[0]
        records_path, manifest_path, _ = write_record_package(
            observations=source_records,
            output_path=output / "normalised" / f"{source_id}.jsonl",
            record_schema_path=root / "schemas/normalised-record.schema.json",
            acquisition_manifest_id=str(first["acquisition_manifest_id"]),
            transformation_id=str(first["transformation_id"]),
            created_at=created_at,
            manifest_schema_path=root / "schemas/normalisation-manifest.schema.json",
        )
        generated.extend((records_path, manifest_path))
    return generated


def _write_quality_records(
    *, root: Path, output: Path, created_at: str
) -> _QualityArtifacts:
    evidence_schema = load_mapping(root / "schemas/evidence-assessment.schema.json")
    transport_schema = load_mapping(root / "schemas/transportability-assessment.schema.json")
    disposition_schema = load_mapping(root / "schemas/quality-disposition.schema.json")
    evidence_assessments: list[dict[str, Any]] = []
    evidence_paths: list[Path] = []
    for name in ("population-parameter-assessment", "fraction-parameter-assessment"):
        core = load_mapping(root / "examples/quality" / f"{name}.yml")
        assessment = validate_evidence_assessment(
            build_evidence_assessment(core), evidence_schema
        )
        path = output / "analysis/evidence-assessments" / f"{name}.json"
        atomic_write_json(path, assessment)
        evidence_assessments.append(assessment)
        evidence_paths.append(path)

    transport_core = load_mapping(
        root / "examples/quality/fraction-transportability-assessment.yml"
    )
    transport = validate_transportability_assessment(
        build_transportability_assessment(transport_core), transport_schema
    )
    transport_path = (
        output
        / "analysis/transportability-assessments/fraction-transportability-assessment.json"
    )
    atomic_write_json(transport_path, transport)

    specification = load_mapping(
        root / "examples/analyses/expected-population-synthetic.yml"
    )
    disposition = build_quality_disposition(
        analysis_id=str(specification["analysis_id"]),
        created_at=created_at,
        intended_use=str(specification["intended_use"]),
        evidence_assessments=evidence_assessments,
        transportability_assessments=[transport],
    )
    validate_quality_disposition(
        disposition,
        disposition_schema,
        evidence_assessments=evidence_assessments,
        transportability_assessments=[transport],
    )
    ledger_document = load_mapping(
        root / "examples/ledger/public-foundation-synthetic.yml"
    )
    closure_failures = verify_parameter_assessment_closure(
        parameters=list(ledger_document["parameters"]),
        parameter_ids=[
            str(specification["left_parameter_id"]),
            str(specification["right_parameter_id"]),
        ],
        evidence_assessments=evidence_assessments,
        transportability_assessments=[transport],
        disposition=disposition,
    )
    if closure_failures:
        raise ReferenceWorkflowError(
            "Fitness-for-use closure failed: " + "; ".join(closure_failures)
        )
    disposition_path = output / "analysis/quality-disposition.json"
    atomic_write_json(disposition_path, disposition)
    return _QualityArtifacts(
        evidence_assessments=tuple(evidence_assessments),
        transportability_assessments=(transport,),
        disposition=disposition,
        evidence_paths=tuple(evidence_paths),
        transportability_paths=(transport_path,),
        disposition_path=disposition_path,
    )


def _run_reference_analysis(
    *,
    root: Path,
    output: Path,
    created_at: str,
    quality_disposition: dict[str, Any],
) -> tuple[dict[str, Any], Path]:
    ledger = load_ledger(
        root / "examples/ledger/public-foundation-synthetic.yml",
        root / "schemas/parameter-ledger.schema.json",
    )
    specification = load_mapping(root / "examples/analyses/expected-population-synthetic.yml")
    validate_instance(
        specification,
        load_mapping(root / "schemas/analysis-specification.schema.json"),
        label="reference_analysis_specification",
    )
    result = run_analysis_spec(
        specification,
        ledger,
        created_at=created_at,
        quality_disposition=quality_disposition,
    )
    validate_instance(
        result,
        load_mapping(root / "schemas/analysis-result.schema.json"),
        label="reference_analysis_result",
    )
    path = output / "analysis" / "expected-population-synthetic.json"
    atomic_write_json(path, result)
    return result, path


def _write_gap_map(*, root: Path, output: Path) -> tuple[dict[str, Any], Path, Path]:
    gap_map = build_domain_gap_map(
        load_yaml(root / "catalog/data_sources.yml"),
        load_mapping(root / "examples/config/gap-map-needs.yml"),
    )
    validate_instance(
        gap_map,
        load_mapping(root / "schemas/gap-map.schema.json"),
        label="reference_gap_map",
    )
    json_path = output / "reports" / "public-data-gap-map.json"
    markdown_path = output / "reports" / "public-data-gap-map.md"
    atomic_write_json(json_path, gap_map)
    atomic_write_bytes(markdown_path, render_gap_map_markdown(gap_map).encode("utf-8"))
    return gap_map, json_path, markdown_path


def run_public_foundation_reference(
    *,
    root: Path,
    output_directory: Path,
    created_at: str | None = None,
    overwrite: bool = False,
) -> ReferenceWorkflowResult:
    """Run the complete public-foundation workflow using synthetic offline fixtures.

    The workflow proves acquisition registration, schema-validated provenance, four source
    adapters, canonical record packages, a parameter-ledger simulation, a gap map and a
    content-hashed release manifest. It does not produce an empirical burden estimate.
    """
    repository_root = root.expanduser().resolve()
    required_assets = (
        "schemas/acquisition-manifest.schema.json",
        "schemas/release-manifest.schema.json",
        "examples/fixtures/orphadata-synthetic.xml",
        "examples/ledger/public-foundation-synthetic.yml",
        "examples/quality/population-parameter-assessment.yml",
        "schemas/quality-disposition.schema.json",
        "catalog/data_sources.yml",
    )
    missing_assets = [item for item in required_assets if not (repository_root / item).is_file()]
    if missing_assets:
        raise ReferenceWorkflowError(
            "Reference asset root is incomplete: " + ", ".join(missing_assets)
        )
    output = _prepare_output_directory(output_directory, overwrite=overwrite)
    timestamp = created_at or utc_now()
    fixture_records, generated = _register_fixtures(
        root=repository_root, output=output, created_at=timestamp
    )
    records = _normalised_records(root=repository_root, fixture_records=fixture_records)
    generated.extend(
        _write_normalised_packages(
            root=repository_root, output=output, records=records, created_at=timestamp
        )
    )
    quality = _write_quality_records(
        root=repository_root, output=output, created_at=timestamp
    )
    generated.extend(quality.generated_files)
    analysis_result, analysis_path = _run_reference_analysis(
        root=repository_root,
        output=output,
        created_at=timestamp,
        quality_disposition=quality.disposition,
    )
    generated.append(analysis_path)
    _, gap_json, gap_markdown = _write_gap_map(root=repository_root, output=output)
    generated.extend((gap_json, gap_markdown))

    try:
        assurance = build_reference_scholarly_assurance(
            root=repository_root,
            output=output,
            created_at=timestamp,
            analysis_path=analysis_path,
            quality_evidence_paths=quality.evidence_paths,
            quality_transportability_paths=quality.transportability_paths,
            quality_disposition_path=quality.disposition_path,
            gap_json_path=gap_json,
            gap_markdown_path=gap_markdown,
        )
    except ScholarlyAssuranceError as exc:
        raise ReferenceWorkflowError(f"Scholarly assurance failed: {exc}") from exc
    generated.extend(assurance.generated_files)

    release_manifest_path = output / "release-manifest.json"
    release_manifest = build_release_manifest(
        root=output,
        artefact_paths=generated,
        release_id="public-foundation-synthetic",
        software_version=__version__,
        created_at=timestamp,
        output_path=release_manifest_path,
        release_kind="synthetic_assurance",
        data_classification="synthetic",
        repository_root=repository_root,
    )
    validate_instance(
        release_manifest,
        load_mapping(repository_root / "schemas/release-manifest.schema.json"),
        label="reference_release_manifest",
    )
    failures = verify_release_manifest(output, release_manifest)
    if failures:
        raise ReferenceWorkflowError("Release verification failed: " + "; ".join(failures))
    assessment = json.loads(assurance.reproducibility_path.read_text(encoding="utf-8"))
    assessment_failures = verify_reproducibility_assessment(
        assessment,
        root=output,
        expected_release_id="public-foundation-synthetic",
        expected_workflow_run_id=assurance.workflow_run_id,
    )
    if assessment_failures:
        raise ReferenceWorkflowError(
            "Reproducibility verification failed after release closure: "
            + "; ".join(assessment_failures)
        )
    generated.append(release_manifest_path)
    return ReferenceWorkflowResult(
        output_directory=output,
        release_manifest_path=release_manifest_path,
        analysis_result_path=analysis_path,
        gap_map_path=gap_json,
        generated_files=tuple(generated),
        analysis_result=analysis_result,
        release_manifest=release_manifest,
        scholarly_assurance=assurance,
    )


__all__ = [
    "ReferenceWorkflowError",
    "ReferenceWorkflowResult",
    "run_public_foundation_reference",
]
