#!/usr/bin/env python3
"""Validate and reconstruct the single authorized Track 003 synthetic output."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

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


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(closeout_path: Path, root: Path) -> None:
    closeout = load_mapping(closeout_path)
    if closeout.get("status") != "synthetic_assurance_executed":
        raise Track003SyntheticExecutionError("closeout status drift")
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
    if reconstructed != repeated or reconstructed != retained:
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
