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
EXPECTED_UPSTREAM_COMMIT = "0b8e57a95ff634505af613c4c17e3fc260a37a53"
EXPECTED_UPSTREAM_TREE = "44d57c5051874040b816a4fe567b46c60896a9c5"
EXPECTED_SCOPE = (
    "Synthetic protocol and interface assurance only. Exactly-receipted public "
    "aggregates may be prepared for later qualification, but no public aggregate "
    "is executed or interpreted by this registration."
)
EXPECTED_NEXT_GATE = (
    "Register an exact rights-receipted public-aggregate parameter set under issue "
    "261, or build a protocol-compatible synthetic diabetes denominator, before "
    "running RBC-P002."
)
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
    "framing_overlay": "docs/track-003-bounded-framing-overlay-2026-08-29.yml",
}

EXPECTED_ESTIMANDS = {
    "primary": {
        "estimand_id": "E-RBC-P002-AETIOLOGIC-PROPORTION",
        "denominator_id": "D-RBC-P002-PRIMARY-DIABETES",
        "unit": "proportion",
    },
    "derived": {
        "estimand_id": "E-RBC-P002-EXPECTED-CASES",
        "denominator_id": "D-RBC-P002-PRIMARY-DIABETES",
        "unit": "people",
        "interpretation": "modelled_expected_population_not_observed_case_count",
    },
    "sensitivities": [
        "E-RBC-P002-DIAGNOSED-AETIOLOGIC-PROPORTION",
        "E-RBC-P002-REFERRAL-COHORT-PROPORTION",
    ],
    "deferred": ["E-RBC-P002-POPULATION-PREVALENCE"],
}
EXPECTED_ENTITY_IDS = [
    "monogenic-diabetes",
    "mody",
    "neonatal-diabetes",
    "other-monogenic-diabetes",
]
EXPECTED_POPULATION_STATES = {
    "contract": "RBC-P002-POPULATION-STATES-v0.1.0",
    "required_dimensions": [
        "diabetes_denominator_eligibility",
        "monogenic_aetiology_observation",
        "monogenic_aetiology_latent",
        "referral_and_testing_selection",
    ],
    "required_quantities": [
        "Q-RBC-P002-DIAGNOSED-CONFIRMED",
        "Q-RBC-P002-MODELLED-TOTAL",
        "Q-RBC-P002-MODELLED-UNDIAGNOSED",
        "Q-RBC-P002-UNCLASSIFIED-OR-UNKNOWN",
    ],
}
EXPECTED_FRAMING_OVERLAY = {
    "schema_version": "1.0.0",
    "overlay_id": "RBC-P002-BOUNDED-FRAMING-OVERLAY-2026-08-29",
    "track": "003-monogenic-diabetes-demonstrator",
    "protocol_id": "RBC-P002",
    "status": "active_bounded_synthetic_interface",
    "historical_guard": {
        "path": "docs/track-003-framing-interpretation-guard-v0.1.0.yml",
        "sha256": "70c491ea91ecbcef96745a49bb9cb12b7719835a2ee4ac1f8a91751ac32e9614",
    },
    "dependency_disposition": {
        "track_008": "complete_bounded_semantic_scope_only",
        "track_009": (
            "complete_bounded_synthetic_and_exactly_receipted_public_aggregate_scope_only"
        ),
        "track_010": "complete_bounded_interface_only",
    },
    "review_disposition": {
        "scientific_methods_agent_challenge": "pending_exact_candidate_review",
        "engineering_agent_challenge": "pending_exact_candidate_review",
        "simulated_patient_community_harm_agent_challenge": ("pending_exact_candidate_review"),
        "repository_owner_disposition": "pending",
    },
    "authority_boundaries": {
        "agent_review_is_advisory_repository_evidence": True,
        "independent_review": False,
        "patient_community_approval": False,
        "community_representation": False,
        "empirical_activation": False,
        "controlled_data_activation": False,
        "public_aggregate_execution": False,
        "publication_authority": False,
        "production_release_authority": False,
    },
    "acceptable_scope": [
        "synthetic interface assurance",
        "preparation of exactly-receipted public aggregates for later qualification",
    ],
    "prohibited_scope": [
        "empirical execution",
        "controlled-data execution",
        "clinical decision support",
        "patient or community endorsement claims",
        "independent or external review claims",
    ],
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
        or document.get("registered_on") != "2026-08-29"
        or document.get("registered_by") != "edithatogo"
        or document.get("scope") != EXPECTED_SCOPE
        or document.get("next_gate") != EXPECTED_NEXT_GATE
    ):
        raise Track003RegistrationError("registration identity or bounded status drift")
    upstream = document.get("upstream_candidate", {})
    commit, tree = str(upstream.get("commit", "")), str(upstream.get("tree", ""))
    if (
        not COMMIT.fullmatch(commit)
        or not COMMIT.fullmatch(tree)
        or commit != EXPECTED_UPSTREAM_COMMIT
        or tree != EXPECTED_UPSTREAM_TREE
        or _tree(root, commit) != tree
    ):
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
    if estimands != EXPECTED_ESTIMANDS:
        raise Track003RegistrationError("estimand or denominator scope drift")
    estimand_contract = _load(root / EXPECTED_BINDINGS["estimand_denominator_contract"])
    contract_estimands = {
        item.get("estimand_id"): item for item in estimand_contract.get("estimands", [])
    }
    denominator_options = {
        item.get("denominator_id"): item
        for item in estimand_contract.get("denominator_options", [])
    }
    registered_ids = [
        estimands["primary"]["estimand_id"],
        estimands["derived"]["estimand_id"],
        *estimands["sensitivities"],
        *estimands["deferred"],
    ]
    if any(estimand_id not in contract_estimands for estimand_id in registered_ids):
        raise Track003RegistrationError("estimand reference is absent from bound contract")
    for role in ("primary", "derived"):
        registered = estimands[role]
        contract_estimand = contract_estimands[registered["estimand_id"]]
        denominator = denominator_options.get(registered["denominator_id"], {})
        if contract_estimand.get("unit") != registered["unit"] or registered[
            "estimand_id"
        ] not in denominator.get("permitted_estimands", []):
            raise Track003RegistrationError("estimand unit or denominator reference drift")
    semantic = document.get("synthetic_entity_scope", {})
    if (
        semantic.get("hierarchy_id") != "rare-within-common-synthetic"
        or semantic.get("hierarchy_version") != "0.1.0"
        or semantic.get("included_entity_ids") != EXPECTED_ENTITY_IDS
        or semantic.get("gene_scope") != "not_registered_synthetic_grouping_only"
        or semantic.get("phenotype_scope") != "not_registered_synthetic_grouping_only"
    ):
        raise Track003RegistrationError("synthetic semantic scope drift")
    semantic_contract = _load(root / EXPECTED_BINDINGS["semantic_scope"])
    contract_entity_ids = {
        entity.get("entity_id") for entity in semantic_contract.get("entities", [])
    }
    if any(entity_id not in contract_entity_ids for entity_id in EXPECTED_ENTITY_IDS):
        raise Track003RegistrationError("entity reference is absent from bound semantic scope")
    population_states = document.get("population_states", {})
    if population_states != EXPECTED_POPULATION_STATES:
        raise Track003RegistrationError("population-state scope drift")
    population_contract = _load(root / EXPECTED_BINDINGS["population_state_contract"])
    dimension_ids = {
        item.get("dimension_id") for item in population_contract.get("state_dimensions", [])
    }
    quantity_ids = {
        item.get("quantity_id") for item in population_contract.get("derived_quantities", [])
    }
    if (
        population_contract.get("contract_id") != population_states["contract"]
        or any(item not in dimension_ids for item in population_states["required_dimensions"])
        or any(item not in quantity_ids for item in population_states["required_quantities"])
    ):
        raise Track003RegistrationError("population-state reference is absent from bound contract")
    overlay = _load(root / EXPECTED_BINDINGS["framing_overlay"])
    if overlay != EXPECTED_FRAMING_OVERLAY:
        raise Track003RegistrationError("bounded framing overlay drift")
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
