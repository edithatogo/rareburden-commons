#!/usr/bin/env python3
"""Validate the bounded RBC-P002 registration without activating data use."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml


class Track003RegistrationError(ValueError):
    """Raised when the bounded Track 003 registration drifts."""


SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
FALSE_CLAIMS = {
    "empirical_activation",
    "controlled_data_activation",
    "public_aggregate_execution",
    "clinical_entity_freeze",
    "gene_or_phenotype_freeze",
    "independent_review",
    "patient_community_approval",
    "community_representation",
    "publication_authority",
    "production_release_authority",
}
EXPECTED_BINDINGS = {
    "semantic_scope": "examples/semantics/rare-within-common-synthetic.yml",
    "ledger_profile": "examples/demonstrators/003-ledger-profile.yml",
    "burden_engine": "manifests/burden/track-010-post-dependency-candidate-2026-08-27.json",
    "estimand_denominator_contract": "docs/track-003-estimand-denominator-contract-v0.1.0.yml",
    "population_state_contract": "docs/track-003-population-state-contract-v0.1.0.yml",
    "framing_guard": "docs/track-003-framing-interpretation-guard-v0.1.0.yml",
}


def _load(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise Track003RegistrationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track003RegistrationError(f"{path} must contain a mapping")
    return value


def _path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise Track003RegistrationError("binding path is missing")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise Track003RegistrationError("binding path escapes repository") from exc
    return candidate


def _tree(root: Path, commit: str) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", f"{commit}^{{tree}}"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Track003RegistrationError("cannot resolve upstream candidate") from exc


def validate(path: Path, root: Path) -> None:
    document = _load(path)
    if (
        document.get("schema_version") != "1.0.0"
        or document.get("track") != "003-monogenic-diabetes-demonstrator"
        or document.get("protocol_id") != "RBC-P002"
        or document.get("protocol_version") != "0.2.0-bounded"
        or document.get("status") != "internally_registered_bounded_synthetic_interface"
        or document.get("registered_by") != "edithatogo"
    ):
        raise Track003RegistrationError("registration identity or bounded status drift")
    upstream = document.get("upstream_candidate", {})
    commit, tree = str(upstream.get("commit", "")), str(upstream.get("tree", ""))
    if not COMMIT.fullmatch(commit) or not COMMIT.fullmatch(tree) or _tree(root, commit) != tree:
        raise Track003RegistrationError("upstream candidate identity drift")
    bindings = document.get("bindings", {})
    for name, expected_path in EXPECTED_BINDINGS.items():
        binding = bindings.get(name, {})
        digest = str(binding.get("sha256", ""))
        target = _path(root, binding.get("path"))
        if (
            binding.get("path") != expected_path
            or not SHA256.fullmatch(digest)
            or hashlib.sha256(target.read_bytes()).hexdigest() != digest
        ):
            raise Track003RegistrationError(f"binding drift: {name}")
    estimands = document.get("registered_estimands", {})
    if (
        estimands.get("primary", {}).get("estimand_id") != "E-RBC-P002-AETIOLOGIC-PROPORTION"
        or estimands.get("primary", {}).get("denominator_id") != "D-RBC-P002-PRIMARY-DIABETES"
        or estimands.get("derived", {}).get("estimand_id") != "E-RBC-P002-EXPECTED-CASES"
        or estimands.get("derived", {}).get("interpretation")
        != "modelled_expected_population_not_observed_case_count"
        or "E-RBC-P002-POPULATION-PREVALENCE" not in estimands.get("deferred", [])
    ):
        raise Track003RegistrationError("estimand or denominator scope drift")
    semantic = document.get("synthetic_entity_scope", {})
    if (
        semantic.get("hierarchy_id") != "rare-within-common-synthetic"
        or semantic.get("hierarchy_version") != "0.1.0"
        or semantic.get("gene_scope") != "not_registered_synthetic_grouping_only"
        or semantic.get("phenotype_scope") != "not_registered_synthetic_grouping_only"
    ):
        raise Track003RegistrationError("synthetic semantic scope drift")
    execution = document.get("execution", {})
    if (
        execution.get("compatible_synthetic_fixture") is not None
        or execution.get("public_aggregate_parameter_set") is not None
        or execution.get("supported_cli") != "run-analysis"
        or execution.get("detached_estimation") != "disabled"
    ):
        raise Track003RegistrationError("execution boundary drift")
    claims = document.get("claims", {})
    if set(claims) != FALSE_CLAIMS or any(claims[name] is not False for name in FALSE_CLAIMS):
        raise Track003RegistrationError("prohibited activation or authority claim")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("registration", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.registration.resolve(), args.root.resolve())
    except (OSError, Track003RegistrationError) as exc:
        print(f"Track 003 bounded registration failed: {exc}")
        return 1
    print("Track 003 bounded registration passed; empirical and authority claims remain false.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
