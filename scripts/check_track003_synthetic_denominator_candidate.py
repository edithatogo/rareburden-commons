#!/usr/bin/env python3
"""Validate the RBC-P002 synthetic denominator candidate without executing it."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import yaml

from rareburden.burden_assurance import run_bounded_synthetic_analysis
from rareburden.ledger import load_ledger
from rareburden.quality import (
    validate_evidence_assessment,
    validate_quality_disposition,
    validate_transportability_assessment,
    verify_parameter_assessment_closure,
)
from rareburden.schema import load_mapping, validate_instance


class Track003SyntheticCandidateError(ValueError):
    """Raised when the bounded synthetic candidate drifts or broadens."""


EXPECTED_BINDINGS = {
    "registration": "docs/track-003-rbc-p002-bounded-registration-2026-08-29.yml",
    "estimand_contract": "docs/track-003-estimand-denominator-contract-v0.1.0.yml",
    "synthetic_ledger_profile": (
        "examples/demonstrators/003-rbc-p002-synthetic-ledger-profile-v0.2.0.yml"
    ),
    "ledger": "examples/ledger/track-003-rbc-p002-synthetic.yml",
    "analysis": "examples/analyses/track-003-rbc-p002-synthetic.yml",
    "denominator_assessment": (
        "examples/quality/track-003-rbc-p002-synthetic-denominator-assessment.yml"
    ),
    "fraction_assessment": (
        "examples/quality/track-003-rbc-p002-synthetic-fraction-assessment.yml"
    ),
    "transportability_assessment": (
        "examples/quality/track-003-rbc-p002-synthetic-transportability-assessment.yml"
    ),
    "quality_disposition": ("docs/track-003-rbc-p002-synthetic-quality-disposition-2026-08-29.yml"),
    "source_release_bindings": (
        "manifests/ledger/track-009-source-release-bindings-2026-08-16.json"
    ),
    "execution_plan": "docs/track-003-rbc-p002-synthetic-execution-plan-2026-08-29.yml",
}
FALSE_CLAIMS = {
    "empirical_parameter_activation",
    "controlled_data_activation",
    "public_aggregate_execution",
    "clinical_validity",
    "independent_review",
    "patient_community_approval",
    "community_representation",
    "publication_authority",
    "production_release_authority",
}


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Track003SyntheticCandidateError(f"{path} must contain a mapping")
    return value


def _bound_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise Track003SyntheticCandidateError("binding path is missing")
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise Track003SyntheticCandidateError("binding path escapes repository") from exc
    return path


def validate_required_alignment(denominator: dict[str, Any], fraction: dict[str, Any]) -> None:
    """Validate every RBC-P002 primary-denominator alignment dimension."""
    expected_population = {
        "population_id": "rbc-p002-primary-diabetes-synthetic",
        "geography_id": "synthetic-rbc-p002",
        "sex": "all",
        "age_min": 0,
        "age_max": 100,
    }
    expected_period = {"start": "2025-01-01", "end": "2025-12-31"}
    if any(
        parameter.get("population") != expected_population for parameter in (denominator, fraction)
    ):
        raise Track003SyntheticCandidateError("population alignment drift")
    if any(parameter.get("period") != expected_period for parameter in (denominator, fraction)):
        raise Track003SyntheticCandidateError("period alignment drift")
    expected_definition = {
        "diabetes_case_definition": "synthetic-primary-diabetes-case-definition-v1",
        "ascertainment_target": "all-people-meeting-synthetic-primary-diabetes-definition",
    }
    for parameter in (denominator, fraction):
        definition = parameter.get("disease_definition", {})
        if any(definition.get(key) != value for key, value in expected_definition.items()):
            raise Track003SyntheticCandidateError("required alignment drift")


def validate(candidate_path: Path, root: Path) -> None:
    candidate = _load(candidate_path)
    if {
        "schema_version": candidate.get("schema_version"),
        "candidate_id": candidate.get("candidate_id"),
        "track": candidate.get("track"),
        "protocol_id": candidate.get("protocol_id"),
        "status": candidate.get("status"),
        "intended_use": candidate.get("intended_use"),
        "created_on": candidate.get("created_on"),
    } != {
        "schema_version": "1.0.0",
        "candidate_id": "RBC-P002-SYNTHETIC-DENOMINATOR-2026-08-29",
        "track": "003-monogenic-diabetes-demonstrator",
        "protocol_id": "RBC-P002",
        "status": "candidate_pending_exact_review",
        "intended_use": "synthetic_assurance",
        "created_on": "2026-08-29",
    }:
        raise Track003SyntheticCandidateError("candidate identity or status drift")

    bindings = candidate.get("bindings", {})
    if set(bindings) != set(EXPECTED_BINDINGS):
        raise Track003SyntheticCandidateError("binding set drift")
    for name, expected in EXPECTED_BINDINGS.items():
        binding = bindings[name]
        path = _bound_path(root, binding.get("path"))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if binding.get("path") != expected or binding.get("sha256") != digest:
            raise Track003SyntheticCandidateError(f"binding drift: {name}")

    ledger_path = root / EXPECTED_BINDINGS["ledger"]
    ledger = load_ledger(ledger_path, root / "schemas/parameter-ledger.schema.json")
    parameter_ids = [
        "rbc-p002-diabetes-denominator-synthetic",
        "rbc-p002-aetiologic-fraction-synthetic",
    ]
    if sorted(ledger.records) != sorted(parameter_ids):
        raise Track003SyntheticCandidateError("synthetic parameter set drift")
    denominator, fraction = (ledger.get(item) for item in parameter_ids)
    if (
        denominator.get("quantity_type") != "case_count"
        or denominator.get("unit") != "people"
        or denominator.get("metric") != "count"
        or denominator.get("disease_definition", {}).get("denominator_id")
        != "D-RBC-P002-PRIMARY-DIABETES"
        or fraction.get("quantity_type") != "fraction"
        or fraction.get("unit") != "proportion"
        or fraction.get("disease_definition", {}).get("estimand_id")
        != "E-RBC-P002-AETIOLOGIC-PROPORTION"
    ):
        raise Track003SyntheticCandidateError("parameter compatibility drift")

    validate_required_alignment(denominator, fraction)

    profile = load_mapping(root / EXPECTED_BINDINGS["synthetic_ledger_profile"])
    if profile.get("requirements") != [
        {
            "role": "denominator",
            "acceptable_quantity_types": ["case_count"],
            "acceptable_metrics": ["count"],
            "parameter_id": parameter_ids[0],
        },
        {
            "role": "aetiologic_fraction",
            "acceptable_quantity_types": ["fraction"],
            "acceptable_metrics": ["case_fraction"],
            "parameter_id": parameter_ids[1],
        },
    ] or profile.get("required_alignment") != [
        "geography",
        "period",
        "age_band",
        "diabetes_case_definition",
        "ascertainment_target",
    ]:
        raise Track003SyntheticCandidateError("synthetic ledger profile drift")

    analysis = load_mapping(root / EXPECTED_BINDINGS["analysis"])
    validate_instance(
        analysis,
        load_mapping(root / "schemas/analysis-specification.schema.json"),
        label="track003_analysis",
    )
    if analysis != {
        "schema_version": "1.0.0",
        "analysis_id": "track-003-rbc-p002-synthetic",
        "title": "RBC-P002 protocol-compatible synthetic denominator assurance analysis",
        "estimand": "rare_aetiology_cases",
        "left_parameter_id": parameter_ids[0],
        "right_parameter_id": parameter_ids[1],
        "output_unit": "people",
        "iterations": 10000,
        "seed": 20260829,
        "interval_probability": 0.95,
        "dependence": "independent",
        "dependence_rationale": (
            "Independence is an explicit synthetic assurance assumption and is not "
            "asserted for any empirical population."
        ),
        "intended_use": "synthetic_assurance",
        "limitations": [
            "Synthetic protocol compatibility only; no empirical, clinical, policy or "
            "patient-facing interpretation is permitted.",
            "The denominator and aetiologic fraction are transparent assumptions rather "
            "than observed quantities.",
            "Gene, phenotype, ascertainment, penetrance and clinical entity scope remain unfrozen.",
        ],
    }:
        raise Track003SyntheticCandidateError("analysis specification drift")

    evidence_schema = load_mapping(root / "schemas/evidence-assessment.schema.json")
    evidence = [
        validate_evidence_assessment(load_mapping(root / EXPECTED_BINDINGS[name]), evidence_schema)
        for name in ("denominator_assessment", "fraction_assessment")
    ]
    transport = [
        validate_transportability_assessment(
            load_mapping(root / EXPECTED_BINDINGS["transportability_assessment"]),
            load_mapping(root / "schemas/transportability-assessment.schema.json"),
        )
    ]
    disposition = validate_quality_disposition(
        load_mapping(root / EXPECTED_BINDINGS["quality_disposition"]),
        load_mapping(root / "schemas/quality-disposition.schema.json"),
        evidence_assessments=evidence,
        transportability_assessments=transport,
    )
    failures = verify_parameter_assessment_closure(
        parameters=list(ledger.records.values()),
        parameter_ids=parameter_ids,
        evidence_assessments=evidence,
        transportability_assessments=transport,
        disposition=disposition,
    )
    if failures:
        raise Track003SyntheticCandidateError("quality graph drift: " + "; ".join(failures))

    execution_plan = load_mapping(root / EXPECTED_BINDINGS["execution_plan"])
    expected_plan = {
        "command": "run-analysis",
        "ledger": EXPECTED_BINDINGS["ledger"],
        "analysis": EXPECTED_BINDINGS["analysis"],
        "quality_disposition": EXPECTED_BINDINGS["quality_disposition"],
        "source_release_bindings": EXPECTED_BINDINGS["source_release_bindings"],
        "created_at": "2026-08-29T00:00:00Z",
        "intended_output": (
            "manifests/demonstrators/track-003-rbc-p002-synthetic-execution-2026-08-29.json"
        ),
    }
    if any(execution_plan.get(key) != value for key, value in expected_plan.items()):
        raise Track003SyntheticCandidateError("execution plan drift")
    result = run_bounded_synthetic_analysis(
        analysis,
        ledger,
        load_mapping(root / EXPECTED_BINDINGS["source_release_bindings"]),
        disposition,
        created_at=expected_plan["created_at"],
    )
    repeated_result = run_bounded_synthetic_analysis(
        analysis,
        ledger,
        load_mapping(root / EXPECTED_BINDINGS["source_release_bindings"]),
        disposition,
        created_at=expected_plan["created_at"],
    )
    if result != repeated_result:
        raise Track003SyntheticCandidateError("deterministic dry-run drift")
    validate_instance(
        result,
        load_mapping(root / "schemas/analysis-result.schema.json"),
        label="track003_dry_run_result",
    )

    expected_scope = {
        "estimand_id": "E-RBC-P002-EXPECTED-CASES",
        "denominator_id": "D-RBC-P002-PRIMARY-DIABETES",
        "denominator_parameter_id": parameter_ids[0],
        "aetiologic_fraction_parameter_id": parameter_ids[1],
        "output_unit": "people",
    }
    if candidate.get("registered_scope") != expected_scope:
        raise Track003SyntheticCandidateError("registered scope drift")
    expected_qualification = {
        "schema_valid": True,
        "compatible_population_context": True,
        "compatible_period_context": True,
        "compatible_age_band": True,
        "compatible_diabetes_case_definition": True,
        "compatible_ascertainment_target": True,
        "compatible_case_count_times_fraction_units": True,
        "quality_graph_closed": True,
        "exact_candidate_review_complete": False,
        "owner_disposition_complete": False,
        "executable": False,
    }
    if candidate.get("qualification") != expected_qualification:
        raise Track003SyntheticCandidateError("qualification state drift")
    claims = candidate.get("claims", {})
    if set(claims) != FALSE_CLAIMS or any(claims[name] is not False for name in FALSE_CLAIMS):
        raise Track003SyntheticCandidateError("activation or authority claim drift")
    if candidate.get("next_gate") != (
        "Bind role-separated agent review and repository-owner disposition to the exact "
        "candidate commit before one provenance-bound synthetic assurance execution."
    ):
        raise Track003SyntheticCandidateError("next gate drift")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.candidate.resolve(), args.root.resolve())
    except (OSError, Track003SyntheticCandidateError, ValueError) as exc:
        print(f"Track 003 synthetic denominator candidate failed: {exc}")
        return 1
    print("Track 003 synthetic denominator candidate passed; execution remains disabled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
