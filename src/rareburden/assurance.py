"""Scholarly assurance packaging for the synthetic reference workflow.

This module joins prospective transparency, activity-level retrospective provenance,
lineage closure, PROV-O projection, GATHER evidence, RO-Crate packaging, and a
conservative reproducibility assessment.  It does not claim external preregistration,
independent reproduction, peer review, or empirical validation.
"""

from __future__ import annotations

import json
import shutil
import zipfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rareburden.lineage import build_lineage_audit, require_lineage_audit_pass
from rareburden.prov import build_prov_bundle, verify_prov_bundle
from rareburden.provenance import atomic_write_json
from rareburden.reporting import GATHER_ITEMS, build_gather_checklist
from rareburden.reproducibility import (
    build_reproducibility_assessment,
    reference_assessment_criteria,
    verify_reproducibility_assessment,
)
from rareburden.research_object import (
    build_workflow_run_crate,
    verify_process_run_crate,
    write_process_run_crate,
)
from rareburden.schema import load_mapping, validate_instance
from rareburden.transformation import (
    TransformationArtifact,
    artifact_from_file,
    build_transformation_run,
    capture_environment,
    verify_transformation_run,
)
from rareburden.transparency import (
    build_analysis_decision_log,
    build_protocol_registration,
    verify_analysis_decision_log,
    verify_protocol_registration,
)
from rareburden.workflow import (
    TransformationRecordReference,
    build_workflow_run,
    verify_workflow_run,
)


class ScholarlyAssuranceError(RuntimeError):
    """Raised when the reference assurance package cannot be closed and verified."""


@dataclass(frozen=True)
class ScholarlyAssuranceResult:
    """Paths and identifiers created by scholarly assurance packaging."""

    generated_files: tuple[Path, ...]
    workflow_path: Path
    workflow_run_id: str
    lineage_path: Path
    prov_path: Path
    crate_path: Path
    reporting_path: Path
    reproducibility_path: Path
    reproducibility_level: str
    transformation_run_count: int

    def summary(self, output_root: Path) -> dict[str, Any]:
        return {
            "workflow_run_id": self.workflow_run_id,
            "workflow": self.workflow_path.relative_to(output_root).as_posix(),
            "lineage_audit": self.lineage_path.relative_to(output_root).as_posix(),
            "prov_o": self.prov_path.relative_to(output_root).as_posix(),
            "research_object": self.crate_path.relative_to(output_root).as_posix(),
            "reporting_checklist": self.reporting_path.relative_to(output_root).as_posix(),
            "reproducibility_assessment": self.reproducibility_path.relative_to(
                output_root
            ).as_posix(),
            "reproducibility_level": self.reproducibility_level,
            "transformation_run_count": self.transformation_run_count,
        }


_SOURCE_FIXTURES = {
    "orphadata-science": "orphadata-synthetic.xml",
    "un-world-population-prospects": "un-wpp-synthetic.csv",
    "who-global-health-estimates": "who-ghe-synthetic.csv",
    "world-bank-indicators": "world-bank-synthetic.json",
}


def _copy_file(source: Path, destination: Path) -> Path:
    if source.is_symlink() or not source.is_file():
        raise ScholarlyAssuranceError(f"Assurance source is missing or unsafe: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.partial")
    try:
        shutil.copyfile(source, temporary)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def _resolve_environment_file(root: Path, name: str) -> Path:
    candidates = (root / name, root / "environment" / name)
    for candidate in candidates:
        if candidate.is_file() and not candidate.is_symlink():
            return candidate
    raise ScholarlyAssuranceError(f"Required environment snapshot is unavailable: {name}")


def _copy_software_snapshot(destination: Path) -> list[Path]:
    package_root = Path(__file__).resolve().parent
    generated: list[Path] = []
    copied: list[tuple[Path, Path]] = []
    for source in sorted(package_root.rglob("*"), key=lambda item: item.as_posix()):
        if source.is_symlink() or not source.is_file():
            continue
        if "__pycache__" in source.parts or source.suffix in {".pyc", ".pyo"}:
            continue
        relative = source.relative_to(package_root)
        target = _copy_file(source, destination / "rareburden" / relative)
        generated.append(target)
        copied.append((relative, target))
    if not generated:
        raise ScholarlyAssuranceError("Software snapshot contains no source files")

    # Preserve a deterministic, content-addressable archive in addition to the
    # inspectable source tree. ZIP metadata are fixed so repeated executions on
    # supported platforms produce identical bytes.
    archive = destination / "rareburden-source-snapshot.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    temporary = archive.with_name(f".{archive.name}.partial")
    try:
        with zipfile.ZipFile(
            temporary, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as bundle:
            for relative, target in copied:
                info = zipfile.ZipInfo(
                    filename=(Path("rareburden") / relative).as_posix(),
                    date_time=(1980, 1, 1, 0, 0, 0),
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                bundle.writestr(info, target.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
        temporary.replace(archive)
    finally:
        temporary.unlink(missing_ok=True)
    generated.append(archive)
    return generated


def _prepare_materials(root: Path, output: Path) -> tuple[dict[str, Path], list[Path]]:
    generated: list[Path] = []
    paths: dict[str, Path] = {}
    for source_id, filename in _SOURCE_FIXTURES.items():
        path = _copy_file(
            root / "examples" / "fixtures" / filename,
            output / "materials" / "source" / filename,
        )
        paths[f"source:{source_id}"] = path
        generated.append(path)

    copies = {
        "protocol": (
            root / "docs/protocols/public-data-foundation.md",
            output / "materials/protocols/public-data-foundation.md",
        ),
        "ledger": (
            root / "examples/ledger/public-foundation-synthetic.yml",
            output / "materials/analysis/public-foundation-synthetic-ledger.yml",
        ),
        "analysis_spec": (
            root / "examples/analyses/expected-population-synthetic.yml",
            output / "materials/analysis/expected-population-synthetic.yml",
        ),
        "gap_needs": (
            root / "examples/config/gap-map-needs.yml",
            output / "materials/analysis/gap-map-needs.yml",
        ),
        "un_columns": (
            root / "examples/config/un-wpp-columns.yml",
            output / "materials/analysis/un-wpp-columns.yml",
        ),
        "who_columns": (
            root / "examples/config/who-ghe-columns.yml",
            output / "materials/analysis/who-ghe-columns.yml",
        ),
        "catalog": (
            root / "catalog/data_sources.yml",
            output / "materials/catalog/data_sources.yml",
        ),
        "quality_population": (
            root / "examples/quality/population-parameter-assessment.yml",
            output / "materials/quality/population-parameter-assessment.yml",
        ),
        "quality_fraction": (
            root / "examples/quality/fraction-parameter-assessment.yml",
            output / "materials/quality/fraction-parameter-assessment.yml",
        ),
        "quality_transport": (
            root / "examples/quality/fraction-transportability-assessment.yml",
            output / "materials/quality/fraction-transportability-assessment.yml",
        ),
    }
    for key, (source, destination) in copies.items():
        paths[key] = _copy_file(source, destination)
        generated.append(paths[key])

    paths["pyproject"] = _copy_file(
        _resolve_environment_file(root, "pyproject.toml"),
        output / "materials/environment/pyproject.toml",
    )
    paths["lockfile"] = _copy_file(
        _resolve_environment_file(root, "uv.lock"),
        output / "materials/environment/uv.lock",
    )
    generated.extend((paths["pyproject"], paths["lockfile"]))

    schema_destination = output / "materials/schemas"
    for schema in sorted((root / "schemas").glob("*.json")):
        generated.append(_copy_file(schema, schema_destination / schema.name))
    generated.extend(_copy_software_snapshot(output / "materials/software"))
    return paths, generated


def _logical(output: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(output.resolve()).as_posix()
    except ValueError as exc:
        raise ScholarlyAssuranceError(f"Assurance artefact escapes output root: {path}") from exc


def _artifact(
    output: Path,
    path: Path,
    *,
    role: str,
    source_release_id: str | None = None,
    acquisition_manifest_id: str | None = None,
    licence_state: str | None = None,
) -> TransformationArtifact:
    return artifact_from_file(
        path,
        logical_path=_logical(output, path),
        role=role,
        source_release_id=source_release_id,
        acquisition_manifest_id=acquisition_manifest_id,
        licence_state=licence_state,
    )


def _write_validated(value: dict[str, Any], path: Path, schema: Path) -> Path:
    validate_instance(value, load_mapping(schema), label=path.name)
    atomic_write_json(path, value)
    return path


def _transparency_records(
    *, root: Path, output: Path, materials: Mapping[str, Path], created_at: str
) -> tuple[dict[str, Any], Path, dict[str, Any], Path]:
    registration = build_protocol_registration(
        protocol_id="RBC-P001",
        title="Public-data foundation and federated extension protocol",
        version="0.1.0",
        protocol_path=materials["protocol"],
        logical_path=_logical(output, materials["protocol"]),
        status="internally_frozen",
        created_at=created_at,
        frozen_at=created_at,
        registration_url=None,
        registration_service=None,
        research_questions=[
            "What rare-disease burden components can be estimated reproducibly "
            "from public data alone?",
            "Which conclusions remain non-estimable without controlled or newly collected data?",
            "How can rare aetiologies within common disease envelopes be estimated "
            "without invalid outcome allocation?",
        ],
        estimands=[
            "Expected affected population from a population denominator and prevalence fraction",
            "Evidence-gap readiness by parameter domain and access class",
        ],
        planned_analyses=[
            "Normalise four synthetic public-source fixtures under explicit column "
            "and semantic contracts",
            "Run a seeded expected-population simulation using a versioned parameter ledger",
            "Generate a constraint-aware public-data evidence-gap map",
        ],
        exclusions=[
            "Empirical burden claims",
            "Participant-level data",
            "Direct allocation of a case fraction to DALY, cost, or severity envelopes",
        ],
        limitations=[
            "This reference freeze is internal and is not an external preregistration.",
            "All data in the executable reference are synthetic assurance fixtures.",
        ],
    )
    registration_path = _write_validated(
        registration,
        output / "materials/protocols/protocol-registration.json",
        root / "schemas/protocol-registration.schema.json",
    )
    decisions = build_analysis_decision_log(
        analysis_id="public-foundation-synthetic-v1",
        protocol_registration_id=str(registration["protocol_registration_id"]),
        created_at=created_at,
        decisions=[
            {
                "decision_id": "D001",
                "decision_type": "design",
                "timing": "prospective",
                "description": "Use only synthetic fixtures in the reference workflow.",
                "rationale": (
                    "The workflow must be executable without controlled data or "
                    "empirical interpretation."
                ),
                "consequence": (
                    "Outputs demonstrate mechanics and assurance, not population burden."
                ),
                "recorded_at": created_at,
                "status": "accepted",
                "evidence": [_logical(output, materials["protocol"])],
            },
            {
                "decision_id": "D002",
                "decision_type": "uncertainty",
                "timing": "prospective",
                "description": "Use a versioned deterministic stochastic stream and fixed seed.",
                "rationale": (
                    "Simulation results must be exactly rerunnable across supported environments."
                ),
                "consequence": (
                    "The random algorithm, version, seed, and iteration count are recorded."
                ),
                "recorded_at": created_at,
                "status": "accepted",
                "evidence": [_logical(output, materials["analysis_spec"])],
            },
            {
                "decision_id": "D003",
                "decision_type": "reporting",
                "timing": "implementation",
                "description": (
                    "Classify unresolved GATHER items explicitly rather than asserting "
                    "blanket compliance."
                ),
                "rationale": (
                    "A synthetic assurance package cannot satisfy empirical interpretation "
                    "and validation items."
                ),
                "consequence": (
                    "The reporting checklist contains satisfied, partial, and "
                    "not-applicable states."
                ),
                "recorded_at": created_at,
                "status": "accepted",
                "evidence": [_logical(output, materials["protocol"])],
            },
        ],
        deviations=[],
        limitations=[
            "The decision log documents the synthetic reference workflow only.",
        ],
    )
    decision_path = _write_validated(
        decisions,
        output / "analysis/analysis-decision-log.json",
        root / "schemas/analysis-decision-log.schema.json",
    )
    failures = verify_protocol_registration(registration, root=output)
    failures.extend(
        verify_analysis_decision_log(
            decisions,
            expected_protocol_registration_id=str(registration["protocol_registration_id"]),
        )
    )
    if failures:
        raise ScholarlyAssuranceError("Transparency verification failed: " + "; ".join(failures))
    return registration, registration_path, decisions, decision_path


def _source_records(output: Path, source_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    acquisition_path = output / "acquisition" / f"{source_id}.acquisition.json"
    release_path = output / "acquisition" / f"{source_id}.release.json"
    return (
        json.loads(acquisition_path.read_text(encoding="utf-8")),
        json.loads(release_path.read_text(encoding="utf-8")),
    )


def _plan(registration: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "plan_id": str(registration["protocol_registration_id"]),
        "protocol": "materials/protocols/protocol-registration.json",
        "protocol_version": str(registration["version"]),
        "registered_at": None,
        "preregistration": None,
        "deviations": [],
    }


def _build_run(
    *,
    root: Path,
    output: Path,
    registration: Mapping[str, Any],
    created_at: str,
    activity_id: str,
    title: str,
    inputs: Sequence[TransformationArtifact],
    outputs: Sequence[TransformationArtifact],
    parameters: Mapping[str, Any],
    command: Sequence[str],
    randomness: Mapping[str, Any] | None = None,
    limitations: Sequence[str] = (),
    assertions: Sequence[str] = (),
) -> tuple[dict[str, Any], Path, TransformationRecordReference]:
    environment = capture_environment(
        repository_root=root if (root / ".git").exists() else None,
        lockfile_path=output / "materials/environment/uv.lock",
    )
    record = build_transformation_run(
        activity_id=activity_id,
        title=title,
        prospective_plan=_plan(registration),
        started_at=created_at,
        ended_at=created_at,
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        command=command,
        environment=environment,
        repository_root=root if (root / ".git").exists() else None,
        randomness=randomness,
        agents=[
            {
                "id": "urn:rareburden:agent:reference-workflow",
                "name": "RareBurden Commons synthetic reference workflow",
                "role": "software_agent",
            }
        ],
        limitations=limitations,
        assertions=assertions,
    )
    path = output / "provenance/runs" / f"{activity_id}.json"
    _write_validated(record, path, root / "schemas/transformation-run.schema.json")
    failures = verify_transformation_run(record, artefact_roots=[output])
    if failures:
        raise ScholarlyAssuranceError(
            f"Transformation verification failed for {activity_id}: " + "; ".join(failures)
        )
    reference = TransformationRecordReference.from_file(
        record, path, logical_path=_logical(output, path)
    )
    return record, path, reference


def _gather_evidence(*, output: Path, created_at: str) -> dict[str, Any]:
    satisfied: dict[int, list[str]] = {
        1: ["materials/protocols/public-data-foundation.md"],
        3: ["materials/catalog/data_sources.yml", "acquisition/"],
        4: ["materials/protocols/public-data-foundation.md", "analysis/analysis-decision-log.json"],
        5: ["acquisition/", "normalised/"],
        7: [
            "materials/analysis/public-foundation-synthetic-ledger.yml",
            "analysis/evidence-assessments/",
            "analysis/transportability-assessments/",
            "analysis/quality-disposition.json",
        ],
        8: ["materials/source/", "acquisition/"],
        9: ["materials/protocols/public-data-foundation.md"],
        10: ["provenance/runs/", "provenance/workflow-run.json"],
        13: [
            "analysis/expected-population-synthetic.json",
            "analysis/analysis-decision-log.json",
            "analysis/quality-disposition.json",
        ],
        14: ["materials/software/"],
        15: ["analysis/expected-population-synthetic.json"],
        16: ["analysis/expected-population-synthetic.json"],
        18: [
            "materials/protocols/public-data-foundation.md",
            "analysis/expected-population-synthetic.json",
        ],
    }
    not_applicable = {
        2: (
            "The synthetic reference has no external funding award; programme funding "
            "disclosure belongs to empirical releases."
        ),
        11: "No candidate-model comparison is performed in this bounded synthetic calculation.",
        17: "Synthetic outputs are not interpreted against external epidemiological evidence.",
    }
    partial = {
        6: (
            "Domain-level evidence-quality records expose synthetic limitations but "
            "cannot characterize empirical source bias."
        ),
        12: (
            "Deterministic and tamper tests are included, but empirical calibration "
            "and predictive validation are not applicable."
        ),
    }
    evidence: dict[int, dict[str, Any]] = {}
    for number, _, _ in GATHER_ITEMS:
        if number in satisfied:
            evidence[number] = {"status": "satisfied", "evidence": satisfied[number]}
        elif number in not_applicable:
            evidence[number] = {
                "status": "not_applicable",
                "evidence": [],
                "rationale": not_applicable[number],
            }
        else:
            evidence[number] = {
                "status": "partially_satisfied",
                "evidence": ["materials/protocols/public-data-foundation.md"],
                "rationale": partial.get(
                    number,
                    "The synthetic reference exposes the required structure but cannot "
                    "supply empirical evidence.",
                ),
            }
    return build_gather_checklist(
        report_id="public-foundation-synthetic-v1",
        title="GATHER evidence for the RareBurden synthetic reference release",
        created_at=created_at,
        evidence=evidence,
        scope_statement=(
            "Structural reporting evidence for a synthetic assurance workflow; not a claim "
            "that an empirical global health estimate has been completed."
        ),
    )


def build_reference_scholarly_assurance(
    *,
    root: Path,
    output: Path,
    created_at: str,
    analysis_path: Path,
    quality_evidence_paths: Sequence[Path],
    quality_transportability_paths: Sequence[Path],
    quality_disposition_path: Path,
    gap_json_path: Path,
    gap_markdown_path: Path,
) -> ScholarlyAssuranceResult:
    """Build and verify the complete R2 scholarly-assurance layer."""
    for directory in (
        "materials/source",
        "materials/protocols",
        "materials/analysis",
        "materials/catalog",
        "materials/environment",
        "materials/quality",
        "materials/software",
        "materials/schemas",
        "provenance/runs",
    ):
        (output / directory).mkdir(parents=True, exist_ok=True)
    materials, generated = _prepare_materials(root, output)
    registration, registration_path, _decisions, decision_path = _transparency_records(
        root=root, output=output, materials=materials, created_at=created_at
    )
    generated.extend((registration_path, decision_path))

    runs: list[dict[str, Any]] = []
    references: list[TransformationRecordReference] = []
    run_paths: list[Path] = []

    def add_run(result: tuple[dict[str, Any], Path, TransformationRecordReference]) -> None:
        record, path, reference = result
        runs.append(record)
        run_paths.append(path)
        references.append(reference)
        generated.append(path)

    add_run(
        _build_run(
            root=root,
            output=output,
            registration=registration,
            created_at=created_at,
            activity_id="protocol-transparency",
            title="Freeze protocol and analytic decision evidence",
            inputs=[
                _artifact(output, materials["protocol"], role="prospective_protocol"),
                _artifact(output, materials["analysis_spec"], role="analysis_specification"),
            ],
            outputs=[
                _artifact(output, registration_path, role="protocol_registration"),
                _artifact(output, decision_path, role="analysis_decision_log"),
            ],
            parameters={"protocol_status": "internally_frozen", "deviation_count": 0},
            command=["rareburden", "assurance", "protocol-transparency"],
            limitations=["Internal freeze is not an external preregistration."],
            assertions=["No external registration identifier is claimed."],
        )
    )

    source_inputs: list[TransformationArtifact] = []
    source_outputs: list[TransformationArtifact] = []
    for source_id in sorted(_SOURCE_FIXTURES):
        acquisition, source_release = _source_records(output, source_id)
        source_inputs.append(
            _artifact(output, materials[f"source:{source_id}"], role="source_fixture")
        )
        source_outputs.extend(
            [
                _artifact(
                    output,
                    output / "acquisition" / f"{source_id}.acquisition.json",
                    role="acquisition_manifest",
                ),
                _artifact(
                    output,
                    output / "acquisition" / f"{source_id}.release.json",
                    role="source_release",
                ),
            ]
        )
    add_run(
        _build_run(
            root=root,
            output=output,
            registration=registration,
            created_at=created_at,
            activity_id="source-registration",
            title="Register content-addressed synthetic source releases",
            inputs=source_inputs,
            outputs=source_outputs,
            parameters={"source_count": len(_SOURCE_FIXTURES), "network_used": False},
            command=["rareburden", "assurance", "source-registration"],
            limitations=["Synthetic fixtures are not official custodian releases."],
            assertions=["Every source fixture is checksum pinned."],
        )
    )

    for source_id in sorted(_SOURCE_FIXTURES):
        acquisition, source_release = _source_records(output, source_id)
        normalised = output / "normalised" / f"{source_id}.jsonl"
        manifest = output / "normalised" / f"{source_id}.jsonl.normalisation.json"
        normalisation_inputs = [
            _artifact(
                output,
                materials[f"source:{source_id}"],
                role="source_data",
                source_release_id=str(source_release["source_release_id"]),
                acquisition_manifest_id=str(acquisition["acquisition_id"]),
                licence_state="not_applicable",
            ),
            _artifact(
                output,
                output / "acquisition" / f"{source_id}.acquisition.json",
                role="acquisition_manifest",
            ),
            _artifact(
                output,
                output / "acquisition" / f"{source_id}.release.json",
                role="source_release",
            ),
        ]
        if source_id == "un-world-population-prospects":
            normalisation_inputs.append(
                _artifact(output, materials["un_columns"], role="column_mapping")
            )
        if source_id == "who-global-health-estimates":
            normalisation_inputs.append(
                _artifact(output, materials["who_columns"], role="column_mapping")
            )
        add_run(
            _build_run(
                root=root,
                output=output,
                registration=registration,
                created_at=created_at,
                activity_id=f"normalise-{source_id}",
                title=f"Normalise the {source_id} synthetic source",
                inputs=normalisation_inputs,
                outputs=[
                    _artifact(output, normalised, role="normalised_observations"),
                    _artifact(output, manifest, role="normalisation_manifest"),
                ],
                parameters={"source_id": source_id, "synthetic_fixture": True},
                command=["rareburden", "assurance", "normalise", source_id],
                limitations=["The adapter is fixture-tested; no live custodian access is claimed."],
                assertions=[
                    "Normalised records retain source-release and acquisition identifiers."
                ],
            )
        )

    quality_outputs = [
        *[
            _artifact(output, path, role="evidence_quality_assessment")
            for path in quality_evidence_paths
        ],
        *[
            _artifact(output, path, role="transportability_assessment")
            for path in quality_transportability_paths
        ],
        _artifact(output, quality_disposition_path, role="fitness_for_use_disposition"),
    ]
    add_run(
        _build_run(
            root=root,
            output=output,
            registration=registration,
            created_at=created_at,
            activity_id="fitness-for-use-assessment",
            title="Assess evidence quality, transportability, and release fitness",
            inputs=[
                _artifact(output, materials["ledger"], role="parameter_ledger"),
                _artifact(output, materials["analysis_spec"], role="analysis_specification"),
                _artifact(
                    output, materials["quality_population"], role="quality_assessment_template"
                ),
                _artifact(
                    output, materials["quality_fraction"], role="quality_assessment_template"
                ),
                _artifact(
                    output,
                    materials["quality_transport"],
                    role="transportability_assessment_template",
                ),
            ],
            outputs=quality_outputs,
            parameters={
                "framework": "RareBurden-EQA-1.0.0",
                "intended_use": "synthetic_assurance",
                "numeric_composite_score": False,
            },
            command=["rareburden", "assurance", "fitness-for-use"],
            limitations=[
                "Producer assessments are internal and do not replace independent "
                "scientific review."
            ],
            assertions=[
                "Domain judgements and rationales remain visible rather than being "
                "collapsed into an opaque score.",
                "Sensitivity-only evidence blocks a primary empirical claim but not "
                "the synthetic assurance run.",
            ],
        )
    )

    add_run(
        _build_run(
            root=root,
            output=output,
            registration=registration,
            created_at=created_at,
            activity_id="expected-population-analysis",
            title="Run the seeded synthetic expected-population analysis",
            inputs=[
                _artifact(output, materials["ledger"], role="parameter_ledger"),
                _artifact(output, materials["analysis_spec"], role="analysis_specification"),
                _artifact(output, decision_path, role="analysis_decision_log"),
                *[
                    _artifact(output, path, role="evidence_quality_assessment")
                    for path in quality_evidence_paths
                ],
                *[
                    _artifact(output, path, role="transportability_assessment")
                    for path in quality_transportability_paths
                ],
                _artifact(output, quality_disposition_path, role="fitness_for_use_disposition"),
            ],
            outputs=[_artifact(output, analysis_path, role="analysis_result")],
            parameters={
                "analysis_id": "expected-population-synthetic-v1",
                "intended_use": "synthetic_assurance",
                "fitness_for_use_assessed": True,
            },
            command=["rareburden", "assurance", "run-analysis"],
            randomness={
                "algorithm": "rareburden.pcg32-box-muller-marsaglia-tsang.v1",
                "deterministic": True,
                "seed": 20260719,
            },
            limitations=["The parameter values are synthetic and non-empirical."],
            assertions=[
                "A case fraction is not applied to a DALY or cost envelope.",
                "The result carries the exact quality-disposition and assessment identifiers used.",
            ],
        )
    )

    add_run(
        _build_run(
            root=root,
            output=output,
            registration=registration,
            created_at=created_at,
            activity_id="public-data-gap-map",
            title="Generate the public-data capability and evidence-gap map",
            inputs=[
                _artifact(output, materials["catalog"], role="data_source_catalogue"),
                _artifact(output, materials["gap_needs"], role="gap_map_requirements"),
            ],
            outputs=[
                _artifact(output, gap_json_path, role="gap_map_data"),
                _artifact(output, gap_markdown_path, role="gap_map_report"),
            ],
            parameters={"classification": "capability_and_access_readiness"},
            command=["rareburden", "assurance", "generate-gap-map"],
            limitations=["Readiness classifications are based on metadata, not live access tests."],
            assertions=["Controlled data are not relabelled as public data."],
        )
    )

    checklist = _gather_evidence(output=output, created_at=created_at)
    reporting_path = _write_validated(
        checklist,
        output / "reports/gather-checklist.json",
        root / "schemas/reporting-checklist.schema.json",
    )
    generated.append(reporting_path)
    add_run(
        _build_run(
            root=root,
            output=output,
            registration=registration,
            created_at=created_at,
            activity_id="reporting-evidence",
            title="Generate explicit GATHER reporting evidence",
            inputs=[
                _artifact(output, registration_path, role="protocol_registration"),
                _artifact(output, decision_path, role="analysis_decision_log"),
                _artifact(output, analysis_path, role="analysis_result"),
                _artifact(output, gap_json_path, role="gap_map_data"),
                _artifact(output, quality_disposition_path, role="fitness_for_use_disposition"),
            ],
            outputs=[_artifact(output, reporting_path, role="reporting_checklist")],
            parameters={"standard": "GATHER", "item_count": 18},
            command=["rareburden", "assurance", "reporting-evidence"],
            limitations=["Unresolved and non-applicable items remain explicitly visible."],
            assertions=["No blanket GATHER-compliance claim is made."],
        )
    )

    workflow = build_workflow_run(
        workflow_id="public-foundation-synthetic-workflow-v1",
        title="RareBurden synthetic public-foundation workflow",
        prospective_plan=_plan(registration),
        transformation_records=references,
        created_at=created_at,
        assertions=[
            "All empirical-looking values are synthetic fixtures.",
            "Every transformation output has one declared producer.",
            "Fitness-for-use decisions preserve domain-level rationales and do not use "
            "an opaque composite score.",
        ],
        limitations=[
            "No external scientific review or independent reproduction is claimed.",
        ],
    )
    workflow_path = _write_validated(
        workflow,
        output / "provenance/workflow-run.json",
        root / "schemas/workflow-run.schema.json",
    )
    generated.append(workflow_path)
    workflow_failures = verify_workflow_run(output, workflow)
    if workflow_failures:
        raise ScholarlyAssuranceError(
            "Workflow provenance verification failed: " + "; ".join(workflow_failures)
        )

    prov = build_prov_bundle(
        workflow=workflow,
        transformation_runs=runs,
        release_id="public-foundation-synthetic",
        title="RareBurden synthetic public-foundation provenance",
        generated_at=created_at,
    )
    prov_path = _write_validated(
        prov,
        output / "provenance/prov.jsonld",
        root / "schemas/prov-bundle.schema.json",
    )
    generated.append(prov_path)
    prov_failures = verify_prov_bundle(prov, workflow=workflow, transformation_runs=runs)
    if prov_failures:
        raise ScholarlyAssuranceError("PROV verification failed: " + "; ".join(prov_failures))

    expected_outputs = sorted(
        {str(item["path"]) for run in runs for item in run["outputs"] if isinstance(item, Mapping)}
    )
    lineage = build_lineage_audit(
        root=output,
        release_id="public-foundation-synthetic",
        transformation_runs=runs,
        expected_outputs=expected_outputs,
        created_at=created_at,
        exempt_outputs=[
            "provenance/workflow-run.json",
            "provenance/prov.jsonld",
            "provenance/lineage-audit.json",
            "reproducibility-assessment.json",
            "ro-crate-metadata.json",
            "release-manifest.json",
        ],
    )
    require_lineage_audit_pass(lineage)
    lineage_path = _write_validated(
        lineage,
        output / "provenance/lineage-audit.json",
        root / "schemas/lineage-audit.schema.json",
    )
    generated.append(lineage_path)

    assessment = build_reproducibility_assessment(
        release_id="public-foundation-synthetic",
        workflow_run_id=str(workflow["workflow_run_id"]),
        created_at=created_at,
        criteria=reference_assessment_criteria(),
        claimed_level="R2_auditable",
        limitations=[
            "This is an internal structural assessment.",
            "Independent reproduction and empirical replication remain uncompleted gates.",
            "External scientific, community, legal, and custodian reviews are not claimed.",
        ],
    )
    reproducibility_path = _write_validated(
        assessment,
        output / "reproducibility-assessment.json",
        root / "schemas/reproducibility-assessment.schema.json",
    )
    generated.append(reproducibility_path)

    additional_paths = sorted(
        {
            *generated,
            workflow_path,
            prov_path,
            lineage_path,
            reporting_path,
            reproducibility_path,
        },
        key=lambda item: _logical(output, item),
    )
    run_artifact_paths = {
        str(item["path"])
        for run in runs
        for collection in ("inputs", "outputs")
        for item in run[collection]
        if isinstance(item, Mapping)
    }
    additional_artifacts = [
        _artifact(output, path, role="research_object_evidence").as_dict()
        for path in additional_paths
        if _logical(output, path) not in run_artifact_paths
    ]
    crate = build_workflow_run_crate(
        title="RareBurden synthetic public-foundation research object",
        description=(
            "Self-contained synthetic assurance package with activity-level provenance; "
            "it contains no empirical rare-disease burden estimate."
        ),
        release_id="public-foundation-synthetic",
        created_at=created_at,
        licence="https://spdx.org/licenses/Apache-2.0.html",
        transformation_runs=runs,
        additional_files=additional_artifacts,
        keywords=["rare disease", "burden estimation", "provenance", "synthetic data"],
        creators=[
            {
                "id": "https://rareburden.org/",
                "type": "Organization",
                "name": "RareBurden Commons",
            }
        ],
        workflow_run_id=str(workflow["workflow_run_id"]),
    )
    crate_path = output / "ro-crate-metadata.json"
    write_process_run_crate(crate_path, crate)
    validate_instance(
        crate,
        load_mapping(root / "schemas/research-object-profile.schema.json"),
        label="ro_crate",
    )
    generated.append(crate_path)
    crate_failures = verify_process_run_crate(output, crate)
    if crate_failures:
        raise ScholarlyAssuranceError(
            "Research-object verification failed: " + "; ".join(crate_failures)
        )

    repro_failures = verify_reproducibility_assessment(
        assessment,
        root=output,
        expected_release_id="public-foundation-synthetic",
        expected_workflow_run_id=str(workflow["workflow_run_id"]),
    )
    # release-manifest.json is created immediately after this function; defer only that path.
    repro_failures = [
        item
        for item in repro_failures
        if item != "evidence file is missing or unsafe: release-manifest.json"
    ]
    if repro_failures:
        raise ScholarlyAssuranceError(
            "Reproducibility assessment verification failed: " + "; ".join(repro_failures)
        )

    return ScholarlyAssuranceResult(
        generated_files=tuple(sorted(set(generated), key=lambda item: _logical(output, item))),
        workflow_path=workflow_path,
        workflow_run_id=str(workflow["workflow_run_id"]),
        lineage_path=lineage_path,
        prov_path=prov_path,
        crate_path=crate_path,
        reporting_path=reporting_path,
        reproducibility_path=reproducibility_path,
        reproducibility_level=str(assessment["claimed_level"]),
        transformation_run_count=len(runs),
    )


__all__ = [
    "ScholarlyAssuranceError",
    "ScholarlyAssuranceResult",
    "build_reference_scholarly_assurance",
]
