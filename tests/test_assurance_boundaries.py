from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

import rareburden.uncertainty as uncertainty_module
import rareburden.verification as verification_module
from rareburden.lineage import (
    LineageAuditError,
    build_lineage_audit,
    require_lineage_audit_pass,
)
from rareburden.model import ModelError
from rareburden.prov import verify_prov_bundle
from rareburden.quality import (
    QualityAssessmentError,
    build_evidence_assessment,
    build_quality_disposition,
    build_transportability_assessment,
    release_eligibility,
    validate_evidence_assessment,
    validate_quality_disposition,
    validate_transportability_assessment,
    verify_parameter_assessment_closure,
)
from rareburden.reference import run_public_foundation_reference
from rareburden.reporting import (
    GATHER_ITEMS,
    GATHER_SOURCE,
    ReportingChecklistError,
    build_gather_checklist,
    require_no_unresolved_reporting_items,
    verify_gather_checklist,
)
from rareburden.reproducibility import (
    ReproducibilityAssessmentError,
    build_reproducibility_assessment,
    reference_assessment_criteria,
    verify_reproducibility_assessment,
)
from rareburden.research_object import verify_process_run_crate
from rareburden.runtime_assets import verify_runtime_assets
from rareburden.schema import load_mapping
from rareburden.transformation import (
    TransformationArtifact,
    TransformationRecordError,
    artifact_from_file,
    build_transformation_run,
    capture_environment,
    verify_transformation_run,
)
from rareburden.transparency import (
    TransparencyRecordError,
    build_analysis_decision_log,
    build_protocol_registration,
    verify_analysis_decision_log,
    verify_protocol_registration,
)
from rareburden.uncertainty import decompose_independent_product
from rareburden.verification import verify_reference_release
from rareburden.workflow import (
    TransformationRecordReference,
    WorkflowProvenanceError,
    build_workflow_run,
    verify_workflow_run,
)


def _digest(path: Path) -> tuple[str, int]:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


def test_uncertainty_decomposition_is_deterministic_and_validates_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    left = {"type": "uniform", "lower": 10.0, "upper": 20.0}
    right = {"type": "beta", "alpha": 2.0, "beta": 8.0}
    first = decompose_independent_product(left, right, iterations=200, seed=7)
    second = decompose_independent_product(left, right, iterations=200, seed=7)
    assert first == second
    assert first["moment_derived_total_variance"] > 0
    fractions = [
        first["left_parameter"]["fraction_of_moment_variance"],
        first["right_parameter"]["fraction_of_moment_variance"],
        first["interaction"]["fraction_of_moment_variance"],
    ]
    assert sum(fractions) == pytest.approx(1.0)

    fixed = decompose_independent_product(
        {"type": "fixed", "value": 2},
        {"type": "fixed", "value": 3},
        iterations=100,
        seed=0,
    )
    assert fixed["moment_derived_total_variance"] == 0
    assert fixed["relative_closure_error"] == 0

    for iterations in (99, 10_000_001):
        with pytest.raises(ModelError, match="iterations"):
            decompose_independent_product(left, right, iterations=iterations, seed=1)
    for seed in (-1, True, 1.5):
        with pytest.raises(ModelError, match="seed"):
            decompose_independent_product(left, right, iterations=100, seed=seed)  # type: ignore[arg-type]

    monkeypatch.setattr(uncertainty_module, "_sample_variance", lambda _values, _mean: float("nan"))
    with pytest.raises(ModelError, match="invalid variance"):
        decompose_independent_product(left, right, iterations=100, seed=1)


def test_runtime_asset_verifier_accepts_projection_and_reports_tampering(tmp_path: Path) -> None:
    assert verify_runtime_assets(tmp_path / "missing")

    root = tmp_path / "assets"
    root.mkdir()
    assert verify_runtime_assets(root) == ["runtime-assets.json is missing or unsafe"]

    manifest = root / "runtime-assets.json"
    manifest.write_text("{", encoding="utf-8")
    assert "cannot be read" in verify_runtime_assets(root)[0]
    manifest.write_text("[]", encoding="utf-8")
    assert verify_runtime_assets(root) == ["runtime asset manifest is malformed"]

    payload = root / "payload.txt"
    payload.write_text("trusted", encoding="utf-8")
    digest, size = _digest(payload)
    document = {
        "file_count": 1,
        "files": [{"path": "payload.txt", "sha256": digest, "size_bytes": size}],
    }
    manifest.write_text(json.dumps(document), encoding="utf-8")
    assert not verify_runtime_assets(root)

    malformed = deepcopy(document)
    malformed["file_count"] = 9
    malformed["files"].extend(
        [
            None,
            {},
            {"path": "../escape", "sha256": "0", "size_bytes": 0},
            {"path": "payload.txt", "sha256": "0", "size_bytes": 0},
            {"path": "missing.txt", "sha256": "0", "size_bytes": 0},
        ]
    )
    extra = root / "extra.txt"
    extra.write_text("extra", encoding="utf-8")
    manifest.write_text(json.dumps(malformed), encoding="utf-8")
    failures = verify_runtime_assets(root)
    assert any("malformed" in item for item in failures)
    assert any("lacks path" in item for item in failures)
    assert any("unsafe runtime asset path" in item for item in failures)
    assert any("duplicate runtime asset path" in item for item in failures)
    assert any("checksum mismatch" in item for item in failures)
    assert any("size mismatch" in item for item in failures)
    assert any("missing or unsafe" in item for item in failures)
    assert any("unexpected runtime asset" in item for item in failures)
    assert any("file_count differs" in item for item in failures)


def _run(output: Path, *, run_id: str = "run-1") -> dict[str, object]:
    digest, size = _digest(output)
    return {
        "transformation_run_id": run_id,
        "inputs": [{"path": "input.txt", "role": "configuration"}],
        "outputs": [{"path": output.name, "sha256": digest, "size_bytes": size}],
    }


def test_lineage_audit_closes_valid_outputs_and_reports_invalid_graphs(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    output.write_text("{}", encoding="utf-8")
    run = _run(output)
    audit = build_lineage_audit(
        root=tmp_path,
        release_id="release-1",
        transformation_runs=[run],
        expected_outputs=["result.json"],
        created_at="2026-07-27T00:00:00Z",
        exempt_outputs=["release-manifest.json"],
    )
    assert audit["status"] == "passed"
    require_lineage_audit_pass(audit)

    with pytest.raises(LineageAuditError, match="cannot also"):
        build_lineage_audit(
            root=tmp_path,
            release_id="release-1",
            transformation_runs=[run],
            expected_outputs=["result.json"],
            exempt_outputs=["result.json"],
            created_at="2026-07-27T00:00:00Z",
        )

    invalid_runs = [
        {},
        {"transformation_run_id": "bad-outputs", "inputs": [], "outputs": "invalid"},
        {
            "transformation_run_id": "bad-output",
            "inputs": [None],
            "outputs": [None],
        },
        run,
        _run(output, run_id="run-2"),
        {
            "transformation_run_id": "source",
            "inputs": [{"path": "raw.csv", "role": "source_data"}],
            "outputs": [],
        },
    ]
    failed = build_lineage_audit(
        root=tmp_path,
        release_id="release-1",
        transformation_runs=invalid_runs,
        expected_outputs=["../unsafe", "untraced.json", "result.json"],
        created_at="2026-07-27T00:00:00Z",
    )
    assert failed["status"] == "failed"
    assert failed["summary"]["failure_count"] >= 8
    with pytest.raises(LineageAuditError, match="Lineage audit failed"):
        require_lineage_audit_pass(failed)
    with pytest.raises(LineageAuditError, match="unknown lineage failure"):
        require_lineage_audit_pass({"status": "failed"})


def _gather_evidence(status: str = "planned") -> dict[int, dict[str, object]]:
    return {
        number: {
            "status": status,
            "evidence": ["evidence.txt"] if status == "satisfied" else [],
            **({} if status == "satisfied" else {"rationale": "Pending external evidence."}),
        }
        for number, _section, _topic in GATHER_ITEMS
    }


def test_reporting_checklist_builds_and_verifies_complete_evidence(tmp_path: Path) -> None:
    (tmp_path / "evidence.txt").write_text("evidence", encoding="utf-8")
    checklist = build_gather_checklist(
        report_id="report-1",
        title="Fixture",
        created_at="2026-07-27T00:00:00Z",
        evidence=_gather_evidence("satisfied"),
        scope_statement="Synthetic assurance only.",
    )
    assert not verify_gather_checklist(checklist, root=tmp_path)
    require_no_unresolved_reporting_items(checklist)

    planned = build_gather_checklist(
        report_id="report-2",
        title="Fixture",
        created_at="2026-07-27T00:00:00Z",
        evidence=_gather_evidence(),
        scope_statement="Synthetic assurance only.",
    )
    with pytest.raises(ReportingChecklistError, match="Unresolved reporting items"):
        require_no_unresolved_reporting_items(planned)
    with pytest.raises(ReportingChecklistError, match="unavailable"):
        require_no_unresolved_reporting_items({})


def test_reporting_checklist_rejects_builder_and_verifier_edge_cases(tmp_path: Path) -> None:
    evidence = _gather_evidence()
    evidence.pop(18)
    with pytest.raises(ReportingChecklistError, match="item mismatch"):
        build_gather_checklist(
            report_id="report",
            title="Fixture",
            created_at="2026-07-27T00:00:00Z",
            evidence=evidence,
            scope_statement="Synthetic.",
        )

    for supplied, message in [
        ({"status": "invalid", "evidence": [], "rationale": "x"}, "invalid status"),
        ({"status": "satisfied", "evidence": "bad"}, "evidence must be a list"),
        ({"status": "planned", "evidence": []}, "requires a rationale"),
        ({"status": "satisfied", "evidence": []}, "without evidence"),
    ]:
        evidence = _gather_evidence()
        evidence[1] = supplied
        with pytest.raises(ReportingChecklistError, match=message):
            build_gather_checklist(
                report_id="report",
                title="Fixture",
                created_at="2026-07-27T00:00:00Z",
                evidence=evidence,
                scope_statement="Synthetic.",
            )

    assert verify_gather_checklist({}) == ["GATHER checklist items are unavailable"]
    checklist = build_gather_checklist(
        report_id="report",
        title="Fixture",
        created_at="2026-07-27T00:00:00Z",
        evidence=_gather_evidence(),
        scope_statement="Synthetic.",
    )
    broken = deepcopy(checklist)
    broken["standard"] = "other"
    broken["source"] = "https://example.invalid"
    broken["summary"] = {}
    broken["items"] = [
        None,
        {"number": 999},
        {
            **deepcopy(checklist["items"][0]),
            "item_id": "wrong",
            "section": "wrong",
            "topic": "wrong",
            "status": "invalid",
            "evidence": ["../unsafe", "../unsafe"],
        },
        deepcopy(checklist["items"][0]),
    ]
    failures = verify_gather_checklist(broken, root=tmp_path)
    assert any("not an object" in item for item in failures)
    assert any("invalid number" in item for item in failures)
    assert any("duplicated" in item for item in failures)
    assert any("unsafe evidence path" in item for item in failures)
    assert any("missing items" in item for item in failures)
    assert any("summary differs" in item for item in failures)
    assert any("content identity" in item for item in failures)
    assert "reporting checklist does not declare GATHER" in failures
    assert checklist["source"] == GATHER_SOURCE


def test_reference_release_passes_the_in_process_independent_verifier(tmp_path: Path) -> None:
    repository_root = Path(__file__).resolve().parents[1]
    result = run_public_foundation_reference(
        root=repository_root,
        output_directory=tmp_path / "reference",
        created_at="2026-07-27T00:00:00Z",
    )
    report = verify_reference_release(
        result.output_directory,
        verified_at="2026-07-27T01:00:00Z",
    )
    assert report["status"] == "passed"
    assert report["summary"]["check_count"] == 7
    assert report["summary"]["passed_count"] == 7
    assert report["summary"]["failed_count"] == 0
    assert report["summary"]["failure_count"] == 0


def test_quality_contracts_cover_decisions_and_closure_failures() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence_schema = load_mapping(root / "schemas/evidence-assessment.schema.json")
    transport_schema = load_mapping(root / "schemas/transportability-assessment.schema.json")
    disposition_schema = load_mapping(root / "schemas/quality-disposition.schema.json")
    population = build_evidence_assessment(
        load_mapping(root / "examples/quality/population-parameter-assessment.yml")
    )
    fraction = build_evidence_assessment(
        load_mapping(root / "examples/quality/fraction-parameter-assessment.yml")
    )
    transport = build_transportability_assessment(
        load_mapping(root / "examples/quality/fraction-transportability-assessment.yml")
    )
    assert validate_evidence_assessment(population, evidence_schema) == population
    assert validate_transportability_assessment(transport, transport_schema) == transport

    summary = release_eligibility(
        evidence_assessments=[population, fraction],
        transportability_assessments=[transport],
    )
    assert not summary["eligible_for_primary_analysis"]
    disposition = build_quality_disposition(
        analysis_id="analysis-1",
        created_at="2026-07-27T00:00:00Z",
        intended_use="synthetic_assurance",
        evidence_assessments=[population, fraction],
        transportability_assessments=[transport],
    )
    assert (
        validate_quality_disposition(
            disposition,
            disposition_schema,
            evidence_assessments=[population, fraction],
            transportability_assessments=[transport],
        )
        == disposition
    )
    with pytest.raises(QualityAssessmentError, match="Unsupported intended_use"):
        build_quality_disposition(
            analysis_id="analysis",
            created_at="now",
            intended_use="unsupported",
            evidence_assessments=[],
            transportability_assessments=[],
        )

    parameters = [
        {
            "parameter_id": "p1",
            "evidence_assessment_ids": ["missing", population["assessment_id"]],
            "transportability_assessment_ids": ["missing-transport", transport["assessment_id"]],
        },
        {"parameter_id": "p2"},
    ]
    wrong_population = {
        **population,
        "subject": {"subject_type": "parameter", "subject_id": "other"},
    }
    wrong_transport = {**transport, "parameter_id": "other"}
    failures = verify_parameter_assessment_closure(
        parameters=parameters,
        parameter_ids=["missing-parameter", "p1", "p2"],
        evidence_assessments=[wrong_population],
        transportability_assessments=[wrong_transport],
        disposition={
            "evidence_assessment_ids": ["declared-only"],
            "transportability_assessment_ids": ["declared-only"],
        },
    )
    assert any("unknown parameter" in item for item in failures)
    assert any("lacks an evidence assessment" in item for item in failures)
    assert any("missing evidence assessment" in item for item in failures)
    assert any("assesses" in item for item in failures)
    assert any("missing transportability" in item for item in failures)
    assert any("concerns" in item for item in failures)
    assert any("set differs" in item for item in failures)


def test_quality_validators_reject_contradictory_decisions() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence_schema = load_mapping(root / "schemas/evidence-assessment.schema.json")
    transport_schema = load_mapping(root / "schemas/transportability-assessment.schema.json")
    disposition_schema = load_mapping(root / "schemas/quality-disposition.schema.json")

    evidence_core = load_mapping(root / "examples/quality/population-parameter-assessment.yml")
    duplicate = deepcopy(evidence_core)
    duplicate["domains"].append(deepcopy(duplicate["domains"][0]))
    with pytest.raises(QualityAssessmentError, match="duplicate domains"):
        validate_evidence_assessment(build_evidence_assessment(duplicate), evidence_schema)

    high_risk = deepcopy(evidence_core)
    high_risk["domains"][0]["judgement"] = "high_concern"
    high_risk["overall_judgement"]["decision"] = "direct_use"
    with pytest.raises(QualityAssessmentError, match="direct_use"):
        validate_evidence_assessment(build_evidence_assessment(high_risk), evidence_schema)

    unsuitable = deepcopy(evidence_core)
    unsuitable["overall_judgement"]["decision"] = "unsuitable"
    with pytest.raises(QualityAssessmentError, match="unsuitable requires"):
        validate_evidence_assessment(build_evidence_assessment(unsuitable), evidence_schema)

    transport_core = load_mapping(
        root / "examples/quality/fraction-transportability-assessment.yml"
    )
    cases = [
        ("direct", "direct_transfer", "moderate", 1.0, "direct transfer"),
        ("adjusted", "no_transfer", "low", 1.5, "no_transfer strategy"),
        ("not_transportable", "calibration", "low", 1.5, "requires no_transfer"),
        ("adjusted", "calibration", "low", 1.0, "requires uncertainty_multiplier"),
        ("direct", "calibration", "low", 1.0, "requires direct_transfer"),
    ]
    for use, strategy, materiality, multiplier, message in cases:
        candidate = deepcopy(transport_core)
        candidate["differences"][0]["materiality"] = materiality
        candidate["method"]["strategy"] = strategy
        candidate["judgement"]["use"] = use
        candidate["judgement"]["uncertainty_multiplier"] = multiplier
        with pytest.raises(QualityAssessmentError, match=message):
            validate_transportability_assessment(
                build_transportability_assessment(candidate), transport_schema
            )

    disposition = build_quality_disposition(
        analysis_id="analysis",
        created_at="2026-07-27T00:00:00Z",
        intended_use="exploratory",
        evidence_assessments=[],
        transportability_assessments=[],
    )
    mismatched = deepcopy(disposition)
    mismatched["disposition_id"] = "qdp-wrong"
    with pytest.raises(QualityAssessmentError, match="does not match"):
        validate_quality_disposition(mismatched, disposition_schema)


def test_reproducibility_assessment_gates_and_evidence_paths(tmp_path: Path) -> None:
    criteria = reference_assessment_criteria()
    assessment = build_reproducibility_assessment(
        release_id="release-1",
        workflow_run_id="workflow-1",
        created_at="2026-07-27T00:00:00Z",
        criteria=criteria,
        claimed_level="R2_auditable",
        limitations=["Synthetic only."],
    )
    assert not verify_reproducibility_assessment(assessment)
    failures = verify_reproducibility_assessment(
        {**assessment, "external_approval_claimed": True},
        expected_release_id="other",
        expected_workflow_run_id="other",
    )
    assert any("wrong release" in item for item in failures)
    assert any("wrong workflow" in item for item in failures)
    assert any("external approval" in item for item in failures)

    for claimed_level in ("invalid",):
        with pytest.raises(ReproducibilityAssessmentError, match="Unsupported"):
            build_reproducibility_assessment(
                release_id="release",
                workflow_run_id="workflow",
                created_at="now",
                criteria=criteria,
                claimed_level=claimed_level,
                limitations=[],
            )
    with pytest.raises(ReproducibilityAssessmentError, match="unique"):
        build_reproducibility_assessment(
            release_id="release",
            workflow_run_id="workflow",
            created_at="now",
            criteria=[criteria[0], criteria[0]],
            claimed_level="R0_conceptual",
            limitations=[],
        )
    with pytest.raises(ReproducibilityAssessmentError, match="At least one"):
        build_reproducibility_assessment(
            release_id="release",
            workflow_run_id="workflow",
            created_at="now",
            criteria=[],
            claimed_level="R0_conceptual",
            limitations=[],
        )
    with pytest.raises(ReproducibilityAssessmentError, match="requires met criterion"):
        build_reproducibility_assessment(
            release_id="release",
            workflow_run_id="workflow",
            created_at="now",
            criteria=criteria[:1],
            claimed_level="R1_rerunnable",
            limitations=[],
        )

    evidence_file = tmp_path / "evidence.txt"
    evidence_file.write_text("evidence", encoding="utf-8")
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    (evidence_dir / "item.txt").write_text("evidence", encoding="utf-8")
    simple = build_reproducibility_assessment(
        release_id="release",
        workflow_run_id="workflow",
        created_at="now",
        criteria=[
            {
                "criterion_id": "fixture",
                "title": "Fixture",
                "status": "met",
                "evidence": [
                    "evidence.txt",
                    "evidence/",
                    "../unsafe",
                    "http://example.org/not-https",
                    "https://example.org/evidence",
                    "missing.txt",
                ],
                "rationale": "Fixture.",
            }
        ],
        claimed_level="R0_conceptual",
        limitations=[],
    )
    failures = verify_reproducibility_assessment(simple, root=tmp_path)
    assert any("Unsafe reproducibility evidence path" in item for item in failures)
    assert any("unsupported external evidence" in item for item in failures)
    assert any("missing or unsafe" in item for item in failures)
    assert verify_reproducibility_assessment({"criteria": "invalid"})


def _artifact(path: str, digest: str = "1" * 64, size: int = 1) -> TransformationArtifact:
    return TransformationArtifact(
        path=path,
        sha256=digest,
        size_bytes=size,
        media_type="application/json",
        role="fixture",
    )


def _transformation(**overrides: object) -> dict[str, object]:
    arguments: dict[str, object] = {
        "activity_id": "activity-1",
        "title": "Fixture transformation",
        "prospective_plan": {"plan_id": "plan-1"},
        "started_at": "2026-07-27T00:00:00Z",
        "ended_at": "2026-07-27T00:00:01Z",
        "inputs": [_artifact("input.json")],
        "outputs": [_artifact("output.json")],
        "parameters": {"threshold": 1},
        "command": ["rareburden", "fixture"],
        "environment": {"python": "fixture"},
    }
    arguments.update(overrides)
    return build_transformation_run(**arguments)  # type: ignore[arg-type]


def test_transformation_builder_environment_and_artifacts_fail_closed(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    source.write_text("{}", encoding="utf-8")
    artifact = artifact_from_file(
        source,
        logical_path="input.json",
        role="source_data",
        source_release_id="src-1",
        acquisition_manifest_id="acq-1",
        licence_state="verified",
    )
    assert artifact.as_dict()["source_release_id"] == "src-1"
    with pytest.raises(TransformationRecordError, match="not a file"):
        artifact_from_file(tmp_path / "missing", logical_path="missing", role="input")
    link = tmp_path / "link"
    link.symlink_to(source)
    with pytest.raises(TransformationRecordError, match="Symlink"):
        artifact_from_file(link, logical_path="link", role="input")
    for logical in ("", "/absolute", "../escape", "./relative", "bad\\path", "bad\npath", "."):
        with pytest.raises(TransformationRecordError):
            artifact_from_file(source, logical_path=logical, role="input")

    lock = tmp_path / "uv.lock"
    lock.write_text("version = 1", encoding="utf-8")
    environment = capture_environment(
        repository_root=tmp_path,
        lockfile_path=lock,
        container_image_digest="sha256:" + "a" * 64,
    )
    assert environment["lockfile"]["path"] == "uv.lock"
    with pytest.raises(TransformationRecordError, match="Lockfile"):
        capture_environment(lockfile_path=tmp_path / "missing")
    with pytest.raises(TransformationRecordError, match="sha256"):
        capture_environment(container_image_digest="latest")

    invalid_cases = [
        ({"started_at": "not-a-date"}, "RFC 3339"),
        ({"started_at": "2026-07-27T00:00:00"}, "timezone"),
        ({"ended_at": "2026-07-26T00:00:00Z"}, "precedes"),
        ({"inputs": []}, "at least one input"),
        ({"outputs": []}, "at least one output"),
        ({"status": "unknown"}, "Unsupported"),
        ({"inputs": [_artifact("same"), _artifact("same")]}, "Duplicate input"),
        ({"outputs": [_artifact("same"), _artifact("same")]}, "Duplicate output"),
        (
            {"inputs": [_artifact("same")], "outputs": [_artifact("same")]},
            "both an input and an output",
        ),
        ({"command": []}, "non-empty argv"),
        ({"prospective_plan": {}}, "plan_id"),
        ({"parameters": {"api_token": "secret"}}, "Secret-like key"),
        ({"command": ["tool", "--password=hunter2"]}, "Secret-like value"),
        ({"parameters": {"value": float("nan")}}, "finite canonical JSON"),
    ]
    for overrides, message in invalid_cases:
        with pytest.raises(TransformationRecordError, match=message):
            _transformation(**overrides)


def test_transformation_verifier_reports_artefact_failures(tmp_path: Path) -> None:
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.json"
    input_path.write_text("input", encoding="utf-8")
    output_path.write_text("output", encoding="utf-8")
    input_digest, input_size = _digest(input_path)
    output_digest, output_size = _digest(output_path)
    record = _transformation(
        inputs=[_artifact("input.json", input_digest, input_size)],
        outputs=[_artifact("output.json", output_digest, output_size)],
    )
    assert not verify_transformation_run(record, artefact_roots=[tmp_path])

    broken = deepcopy(record)
    broken["transformation_run_id"] = "wrong"
    broken["inputs"] = "invalid"
    broken["outputs"] = [
        None,
        {"path": "../unsafe"},
        {"path": "missing.json", "sha256": "0" * 64, "size_bytes": 0},
        {"path": "output.json", "sha256": "0" * 64, "size_bytes": 999},
    ]
    failures = verify_transformation_run(broken, artefact_roots=[tmp_path])
    assert "transformation run content identifier mismatch" in failures
    assert "inputs is not a list" in failures
    assert "invalid outputs artefact record" in failures
    assert any("Unsafe logical" in item for item in failures)
    assert any("resolved 0 times" in item for item in failures)
    assert "checksum mismatch: output.json" in failures
    assert "size mismatch: output.json" in failures
    second_root = tmp_path / "second"
    second_root.mkdir()
    (second_root / "output.json").write_text("output", encoding="utf-8")
    ambiguous = {**record, "inputs": [], "outputs": [record["outputs"][0]]}
    assert any(
        "resolved 2 times" in item
        for item in verify_transformation_run(ambiguous, artefact_roots=[tmp_path, second_root])
    )


def test_workflow_builder_and_verifier_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(WorkflowProvenanceError, match="at least one"):
        build_workflow_run(
            workflow_id="workflow",
            title="Fixture",
            prospective_plan={},
            transformation_records=[],
            created_at="now",
        )
    record = _transformation()
    reference = TransformationRecordReference(
        record=record, path="run.json", sha256="1" * 64, size_bytes=1
    )
    workflow = build_workflow_run(
        workflow_id="workflow",
        title="Fixture",
        prospective_plan={"plan_id": "plan"},
        transformation_records=[reference],
        created_at="now",
    )
    assert workflow["entry_inputs"]
    assert workflow["final_outputs"]

    for mutation, message in [
        ({**record, "transformation_run_id": ""}, "Duplicate or missing"),
        ({**record, "outputs": "invalid"}, "invalid outputs"),
        ({**record, "outputs": [None]}, "malformed output"),
        ({**record, "inputs": "invalid"}, "invalid inputs"),
        ({**record, "inputs": [None]}, "malformed input"),
        (
            {**record, "inputs": [{"path": "input", "sha256": "bad", "size_bytes": 1}]},
            "Invalid artefact SHA",
        ),
    ]:
        with pytest.raises(WorkflowProvenanceError, match=message):
            build_workflow_run(
                workflow_id="workflow",
                title="Fixture",
                prospective_plan={},
                transformation_records=[
                    TransformationRecordReference(
                        record=mutation, path="run.json", sha256="1" * 64, size_bytes=1
                    )
                ],
                created_at="now",
            )

    assert "workflow runs must be a non-empty list" in verify_workflow_run(tmp_path, {})
    failures = verify_workflow_run(
        tmp_path,
        {
            "workflow_run_id": "wrong",
            "runs": [None, {}, {"record_path": "../unsafe"}, {"record_path": "missing.json"}],
        },
    )
    assert any("content identifier mismatch" in item for item in failures)
    assert any("malformed run index" in item for item in failures)
    assert any("record_path" in item for item in failures)
    assert any("Unsafe workflow path" in item for item in failures)
    assert any("missing or unsafe" in item for item in failures)


def test_independent_verifier_reports_tampered_prov_workflow_and_crate(tmp_path: Path) -> None:
    repository_root = Path(__file__).resolve().parents[1]
    result = run_public_foundation_reference(
        root=repository_root,
        output_directory=tmp_path / "reference",
        created_at="2026-07-27T00:00:00Z",
    )
    release = result.output_directory

    prov_path = release / "provenance/prov.jsonld"
    prov = json.loads(prov_path.read_text(encoding="utf-8"))
    prov["rb:canonicalDigest"] = "0" * 64
    prov["@context"] = {}
    prov["@graph"].extend(
        [
            None,
            {"@id": "duplicate", "@type": "prov:Entity"},
            {"@id": "duplicate", "@type": ["prov:Activity"]},
        ]
    )
    prov_path.write_text(json.dumps(prov), encoding="utf-8")

    workflow_path = release / "provenance/workflow-run.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    workflow["workflow_run_id"] = "wrong"
    workflow["runs"][0]["record_sha256"] = "0" * 64
    workflow["runs"][0]["record_size_bytes"] = -1
    workflow["edges"] = []
    workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

    crate_path = release / "ro-crate-metadata.json"
    crate = json.loads(crate_path.read_text(encoding="utf-8"))
    crate["@graph"].extend([None, {"@id": "duplicate"}, {"@id": "duplicate"}])
    crate_path.write_text(json.dumps(crate), encoding="utf-8")

    transformation_runs = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((release / "provenance/runs").glob("*.json"))
    ]
    assert verify_prov_bundle(
        prov,
        workflow=workflow,
        transformation_runs=transformation_runs,
    )
    assert verify_process_run_crate(release, crate)

    report = verify_reference_release(release, verified_at="2026-07-27T01:00:00Z")
    assert report["status"] == "failed"
    assert report["summary"]["failure_count"] > 0
    failed = {item["check_id"] for item in report["checks"] if item["status"] == "failed"}
    assert "scholarly_assurance" in failed


def test_independent_verifier_low_level_boundaries(tmp_path: Path) -> None:
    for value in ("", "/absolute", "../escape", "./relative", "bad\\path", "bad\npath"):
        with pytest.raises(verification_module.ReferenceVerificationError):
            verification_module._safe_relative(value)

    with pytest.raises(verification_module.ReferenceVerificationError, match="missing"):
        verification_module._path(tmp_path, "missing.json")
    link_target = tmp_path / "target.json"
    link_target.write_text("{}", encoding="utf-8")
    link = tmp_path / "link.json"
    link.symlink_to(link_target)
    with pytest.raises(verification_module.ReferenceVerificationError, match="Symlink"):
        verification_module._path(tmp_path, "link.json")

    malformed = tmp_path / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    with pytest.raises(verification_module.ReferenceVerificationError, match="Cannot parse"):
        verification_module._load_json(tmp_path, "malformed.json")
    array = tmp_path / "array.json"
    array.write_text("[]", encoding="utf-8")
    with pytest.raises(verification_module.ReferenceVerificationError, match="not an object"):
        verification_module._load_json(tmp_path, "array.json")
    noncanonical = tmp_path / "noncanonical.json"
    noncanonical.write_text('{ "value": 1 }', encoding="utf-8")
    with pytest.raises(verification_module.ReferenceVerificationError, match="not canonical"):
        verification_module._load_json(tmp_path, "noncanonical.json")
    assert verification_module._load_json(
        tmp_path, "noncanonical.json", require_canonical=False
    ) == {"value": 1}

    captured = verification_module._check(
        "fixture",
        "Fixture",
        lambda: (_ for _ in ()).throw(ValueError("failure")),
    )
    assert captured["status"] == "failed"
    assert captured["failures"] == ["ValueError: failure"]
    assert verification_module._check("ok", "OK", lambda: [])["status"] == "passed"
    with pytest.raises(verification_module.ReferenceVerificationError, match="schema"):
        verification_module._schema(tmp_path, "missing.schema.json")

    declared = tmp_path / "declared.txt"
    declared.write_text("declared", encoding="utf-8")
    extra = tmp_path / "extra.txt"
    extra.write_text("extra", encoding="utf-8")
    manifest = {"artefacts": [{"path": "declared.txt"}, {"path": "missing.txt"}]}
    failures = verification_module._verify_release_closure(tmp_path, manifest)
    assert any("undeclared release file" in item for item in failures)
    assert any("declared release file is missing" in item for item in failures)


def _decision(*, timing: str = "prospective") -> dict[str, object]:
    return {
        "decision_id": "decision-1",
        "decision_type": "model",
        "timing": timing,
        "description": "Use the prespecified model.",
        "rationale": "It matches the estimand.",
        "consequence": "The result is directly interpretable.",
        "recorded_at": "2026-07-27T00:00:00Z",
        "evidence": ["analysis.md"] if timing == "post_hoc" else [],
    }


def _deviation() -> dict[str, object]:
    return {
        "deviation_id": "deviation-1",
        "classification": "minor",
        "planned": "Use the complete synthetic fixture.",
        "actual": "Exclude one malformed synthetic row.",
        "rationale": "The row cannot be parsed.",
        "impact": "No substantive effect.",
        "recorded_at": "2026-07-27T01:00:00Z",
        "resolution": "Documented and sensitivity checked.",
    }


def test_transparency_records_build_and_verify_without_overstatement(tmp_path: Path) -> None:
    protocol_path = tmp_path / "protocol.md"
    protocol_path.write_text("# Protocol\n", encoding="utf-8")
    registration = build_protocol_registration(
        protocol_id="protocol-1",
        title="Synthetic protocol",
        version="1.0",
        protocol_path=protocol_path,
        logical_path="protocol.md",
        status="externally_preregistered",
        created_at="2026-07-27T00:00:00Z",
        frozen_at="2026-07-27T00:00:00+00:00",
        registration_url="https://example.org/registrations/1",
        registration_service="Fixture registry",
        research_questions=[" Question B ", "Question A", "Question A"],
        estimands=["Synthetic estimand"],
        planned_analyses=["Synthetic analysis"],
        exclusions=[],
        amendments=[
            {
                "amendment_id": "amendment-1",
                "recorded_at": "2026-07-27T01:00:00Z",
                "description": "Clarify wording.",
                "rationale": "Remove ambiguity.",
                "impact": "No analytic change.",
                "prospective": True,
            }
        ],
    )
    assert registration["research_questions"] == ["Question A", "Question B"]
    assert not verify_protocol_registration(registration, root=tmp_path)

    decision_log = build_analysis_decision_log(
        analysis_id="analysis-1",
        protocol_registration_id=str(registration["protocol_registration_id"]),
        created_at="2026-07-27T00:00:00Z",
        decisions=[_decision(timing="post_hoc")],
        deviations=[_deviation()],
    )
    assert decision_log["deviation_status"] == "recorded"
    assert not verify_analysis_decision_log(
        decision_log,
        expected_protocol_registration_id=str(registration["protocol_registration_id"]),
    )

    tampered_registration = deepcopy(registration)
    tampered_registration["protocol_registration_id"] = "wrong"
    tampered_registration["registration"] = {"service": None, "url": None}
    tampered_registration["protocol_snapshot"] = {
        "path": "protocol.md",
        "sha256": "0" * 64,
        "size_bytes": 0,
    }
    failures = verify_protocol_registration(tampered_registration, root=tmp_path)
    assert any("identifier mismatch" in item for item in failures)
    assert any("lacks service or URL" in item for item in failures)
    assert any("checksum mismatch" in item for item in failures)
    assert any("size mismatch" in item for item in failures)

    tampered_log = deepcopy(decision_log)
    tampered_log["analysis_decision_log_id"] = "wrong"
    tampered_log["protocol_registration_id"] = "wrong"
    tampered_log["deviation_status"] = "none_recorded"
    tampered_log["decisions"][0]["evidence"] = []
    failures = verify_analysis_decision_log(
        tampered_log,
        expected_protocol_registration_id=str(registration["protocol_registration_id"]),
    )
    assert any("identifier mismatch" in item for item in failures)
    assert any("wrong protocol" in item for item in failures)
    assert any("deviations are present" in item for item in failures)
    assert any("lacks evidence" in item for item in failures)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"status": "unknown"}, "Unsupported protocol status"),
        ({"created_at": "not-a-time"}, "RFC 3339"),
        ({"created_at": "2026-07-27T00:00:00"}, "timezone"),
        (
            {
                "status": "externally_preregistered",
                "registration_url": None,
                "registration_service": None,
            },
            "require a service",
        ),
        (
            {"registration_url": "https://user:secret@example.org/record"},
            "credential-free",
        ),
        ({"research_questions": []}, "substantive item"),
        (
            {
                "amendments": [
                    {
                        "amendment_id": "",
                        "recorded_at": "2026-07-27T00:00:00Z",
                        "description": "",
                        "rationale": "",
                        "impact": "",
                    }
                ]
            },
            "amendments require",
        ),
    ],
)
def test_protocol_registration_rejects_misleading_records(
    tmp_path: Path, mutation: dict[str, object], message: str
) -> None:
    protocol_path = tmp_path / "protocol.md"
    protocol_path.write_text("# Protocol\n", encoding="utf-8")
    arguments: dict[str, object] = {
        "protocol_id": "protocol-1",
        "title": "Synthetic protocol",
        "version": "1.0",
        "protocol_path": protocol_path,
        "logical_path": "protocol.md",
        "status": "draft",
        "created_at": "2026-07-27T00:00:00Z",
        "frozen_at": None,
        "registration_url": None,
        "registration_service": None,
        "research_questions": ["Question"],
        "estimands": ["Estimand"],
        "planned_analyses": ["Analysis"],
        "exclusions": [],
    }
    arguments.update(mutation)
    with pytest.raises(TransparencyRecordError, match=message):
        build_protocol_registration(**arguments)  # type: ignore[arg-type]


def test_decision_log_and_transparency_verifiers_reject_invalid_states(tmp_path: Path) -> None:
    base = {
        "analysis_id": "analysis-1",
        "protocol_registration_id": "protocol-1",
        "created_at": "2026-07-27T00:00:00Z",
        "decisions": [_decision()],
        "deviations": [],
    }
    mutations = [
        ({"decisions": []}, "At least one"),
        ({"decisions": [{**_decision(), "decision_type": "unknown"}]}, "decision type"),
        ({"decisions": [{**_decision(), "timing": "unknown"}]}, "decision timing"),
        ({"decisions": [{**_decision(), "description": ""}]}, "requires description"),
        (
            {"decisions": [{**_decision(timing="post_hoc"), "evidence": []}]},
            "requires evidence",
        ),
        ({"deviations": [{**_deviation(), "classification": "unknown"}]}, "classification"),
        ({"deviations": [{**_deviation(), "impact": ""}]}, "requires planned"),
    ]
    for mutation, message in mutations:
        arguments = {**base, **mutation}
        with pytest.raises(TransparencyRecordError, match=message):
            build_analysis_decision_log(**arguments)

    assert any(
        "snapshot record is malformed" in item
        for item in verify_protocol_registration({"protocol_snapshot": None}, root=tmp_path)
    )
    unsafe = verify_protocol_registration(
        {
            "status": "draft",
            "registration": {"service": "unexpected", "url": "https://example.org"},
            "protocol_snapshot": {"path": "../escape"},
        },
        root=tmp_path,
    )
    assert any("external registration" in item for item in unsafe)
    assert any("Unsafe transparency evidence path" in item for item in unsafe)

    missing = verify_protocol_registration(
        {
            "status": "draft",
            "registration": {"service": None, "url": None},
            "protocol_snapshot": {"path": "missing.md"},
        },
        root=tmp_path,
    )
    assert any("missing or unsafe" in item for item in missing)

    assert any(
        "recorded but no deviations" in item
        for item in verify_analysis_decision_log(
            {"deviation_status": "recorded", "deviations": [], "decisions": []}
        )
    )
