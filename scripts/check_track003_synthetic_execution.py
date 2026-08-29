#!/usr/bin/env python3
"""Validate and reconstruct the single authorized Track 003 synthetic output."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from rareburden.burden_assurance import run_bounded_synthetic_analysis
from rareburden.ledger import load_ledger
from rareburden.quality import validate_quality_disposition
from rareburden.schema import load_mapping, validate_instance


class Track003SyntheticExecutionError(ValueError):
    """Raised when the authorized synthetic execution evidence drifts."""


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
EXPECTED_CANDIDATE = {
    "commit": "fc6f8d755581ce87d38fc8953f8e20f2c89b56ba",
    "tree": "94da74dfee88790fbc6a7da7abfe367b8ca922b8",
    "candidate_sha256": "95beebc8a371633a4b2a0d06a214fafc92dab8f212de9e4f857be0faab429f9c",
}
EXPECTED_REVIEWS = {
    "scientific_methods": (
        "docs/reviews/track-003-synthetic-denominator-scientific-agent-2026-08-29.yml",
        "scientific_methods_agent",
    ),
    "engineering_reproducibility_security": (
        "docs/reviews/track-003-synthetic-denominator-engineering-agent-2026-08-29.yml",
        "engineering_reproducibility_security_agent",
    ),
    "simulated_patient_community_harm": (
        "docs/reviews/track-003-synthetic-denominator-simulated-community-harm-agent-2026-08-29.yml",
        "simulated_patient_community_harm_interpretation_agent",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scientific_projection(result: dict[str, Any]) -> dict[str, Any]:
    """Remove runtime identity while retaining every scientific and boundary field."""
    return {
        key: value for key, value in result.items() if key not in {"analysis_result_id", "runtime"}
    }


def validate_review_receipt(receipt: dict[str, Any], perspective: str) -> None:
    """Require an advisory PASS against the exact reviewed candidate."""
    if (
        receipt.get("reviewed_candidate") != EXPECTED_CANDIDATE
        or receipt.get("perspective") != perspective
        or receipt.get("disposition") != "pass_synthetic_denominator_qualification"
        or receipt.get("unresolved_blocking_findings") != []
        or receipt.get("simulation_status") != "simulated_role_separated_advisory_panel"
        or any(value is not False for value in receipt.get("authority", {}).values())
    ):
        raise Track003SyntheticExecutionError("review receipt semantics drift")


def validate_authorization(authorization: dict[str, Any]) -> None:
    """Require the exact owner decision and retain all external claims as false."""
    decision = authorization.get("decision", {})
    claims = authorization.get("claims", {})
    if (
        authorization.get("candidate", {}).get("commit") != EXPECTED_CANDIDATE["commit"]
        or authorization.get("candidate", {}).get("tree") != EXPECTED_CANDIDATE["tree"]
        or authorization.get("candidate", {}).get("candidate_sha256")
        != EXPECTED_CANDIDATE["candidate_sha256"]
        or decision.get("synthetic_denominator_qualified") is not True
        or decision.get("synthetic_execution_authorized") is not True
        or decision.get("persisted_output_limit") != 1
        or decision.get("empirical_activation") is not False
        or decision.get("controlled_data_activation") is not False
        or decision.get("public_aggregate_execution") is not False
        or claims.get("agent_panel_review_complete") is not True
        or any(
            value is not False
            for key, value in claims.items()
            if key != "agent_panel_review_complete"
        )
    ):
        raise Track003SyntheticExecutionError("owner authorization semantics drift")


def validate_bound_execution_plan(plan: dict[str, Any]) -> None:
    """Require the exact plan that was reviewed and authorized."""
    expected = {
        "schema_version": "1.0.0",
        "execution_plan_id": "RBC-P002-SYNTHETIC-EXECUTION-2026-08-29",
        "status": "blocked_pending_exact_review_and_owner_disposition",
        "command": "run-analysis",
        "ledger": "examples/ledger/track-003-rbc-p002-synthetic.yml",
        "analysis": "examples/analyses/track-003-rbc-p002-synthetic.yml",
        "quality_disposition": (
            "docs/track-003-rbc-p002-synthetic-quality-disposition-2026-08-29.yml"
        ),
        "source_release_bindings": (
            "manifests/ledger/track-009-source-release-bindings-2026-08-16.json"
        ),
        "created_at": "2026-08-29T00:00:00Z",
        "intended_output": (
            "manifests/demonstrators/track-003-rbc-p002-synthetic-execution-2026-08-29.json"
        ),
        "execution_limit": "one_persisted_provenance_bound_synthetic_assurance_output",
        "claims": dict.fromkeys(FALSE_CLAIMS, False),
    }
    if plan != expected:
        raise Track003SyntheticExecutionError("execution plan semantics drift")


def validate(closeout_path: Path, root: Path) -> None:
    closeout = load_mapping(closeout_path)
    if closeout.get("status") != "synthetic_assurance_executed":
        raise Track003SyntheticExecutionError("closeout status drift")
    if closeout.get("reviewed_candidate") != EXPECTED_CANDIDATE:
        raise Track003SyntheticExecutionError("reviewed candidate drift")
    if (
        closeout.get("authorization", {}).get("path")
        != "docs/decisions/2026-08-29-track-003-synthetic-denominator-disposition.yml"
        or closeout.get("execution_plan", {}).get("path")
        != "docs/track-003-rbc-p002-synthetic-execution-plan-2026-08-29.yml"
        or closeout.get("persisted_output", {}).get("path")
        != "manifests/demonstrators/track-003-rbc-p002-synthetic-execution-2026-08-29.json"
    ):
        raise Track003SyntheticExecutionError("provenance path drift")
    if {
        role: binding.get("path") for role, binding in closeout.get("review_receipts", {}).items()
    } != {role: expected[0] for role, expected in EXPECTED_REVIEWS.items()}:
        raise Track003SyntheticExecutionError("review receipt path drift")
    for binding in [
        closeout["authorization"],
        closeout["execution_plan"],
        closeout["persisted_output"],
        *closeout["review_receipts"].values(),
    ]:
        path = (root / binding["path"]).resolve()
        path.relative_to(root.resolve())
        if binding["sha256"] != _sha(path):
            raise Track003SyntheticExecutionError(f"binding drift: {binding['path']}")
    authorization = load_mapping(root / closeout["authorization"]["path"])
    validate_authorization(authorization)
    for role, (path, perspective) in EXPECTED_REVIEWS.items():
        validate_review_receipt(load_mapping(root / path), perspective)
        if authorization["agent_review_receipts"][role] != path:
            raise Track003SyntheticExecutionError("authorization review path drift")
    validate_bound_execution_plan(load_mapping(root / closeout["execution_plan"]["path"]))
    output_path = root / closeout["persisted_output"]["path"]
    retained = load_mapping(output_path)
    validate_instance(
        retained,
        load_mapping(root / "schemas/analysis-result.schema.json"),
        label="track003_synthetic_execution",
    )
    if (
        closeout["persisted_output"]["persisted_output_count"] != 1
        or retained.get("activation_state") != "not_activated"
        or retained.get("intended_use") != "synthetic_assurance"
    ):
        raise Track003SyntheticExecutionError("persisted output boundary drift")
    claims = closeout.get("claims", {})
    if set(claims) != FALSE_CLAIMS or any(claims[name] is not False for name in FALSE_CLAIMS):
        raise Track003SyntheticExecutionError("activation or authority claim drift")

    ledger = load_ledger(
        root / "examples/ledger/track-003-rbc-p002-synthetic.yml",
        root / "schemas/parameter-ledger.schema.json",
    )
    analysis = load_mapping(root / "examples/analyses/track-003-rbc-p002-synthetic.yml")
    disposition = validate_quality_disposition(
        load_mapping(root / "docs/track-003-rbc-p002-synthetic-quality-disposition-2026-08-29.yml"),
        load_mapping(root / "schemas/quality-disposition.schema.json"),
    )
    bindings = load_mapping(
        root / "manifests/ledger/track-009-source-release-bindings-2026-08-16.json"
    )
    reconstructed = run_bounded_synthetic_analysis(
        analysis,
        ledger,
        bindings,
        disposition,
        created_at="2026-08-29T00:00:00Z",
    )
    repeated = run_bounded_synthetic_analysis(
        analysis,
        ledger,
        bindings,
        disposition,
        created_at="2026-08-29T00:00:00Z",
    )
    if reconstructed != repeated or _scientific_projection(reconstructed) != _scientific_projection(
        retained
    ):
        raise Track003SyntheticExecutionError("deterministic reconstruction drift")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("closeout", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.closeout.resolve(), args.root.resolve())
    except (KeyError, OSError, ValueError) as exc:
        print(f"Track 003 synthetic execution failed: {exc}")
        return 1
    print("Track 003 synthetic execution passed; empirical and authority gates remain false.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
