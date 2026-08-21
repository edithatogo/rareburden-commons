#!/usr/bin/env python3
"""Validate the prospective Track 008A/008B split without activating it."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml


class Track008SplitError(ValueError):
    """Raised when the split candidate weakens a fail-closed boundary."""


BASELINE_FILES = {
    "track_008_spec_sha256": "conductor/tracks/008-semantic-backbone/spec.md",
    "track_008_plan_sha256": "conductor/tracks/008-semantic-backbone/plan.md",
    "track_008_metadata_sha256": "conductor/tracks/008-semantic-backbone/metadata.json",
    "track_008_readiness_sha256": "docs/track-008-freeze-readiness-2026-08-21.yml",
    "track_008_final_disposition_sha256": (
        "docs/decisions/2026-08-21-track-008-v0.4-final-disposition.yml"
    ),
    "track_009_metadata_sha256": "conductor/tracks/009-evidence-parameter-ledger/metadata.json",
    "track_009_readiness_sha256": "docs/track-009-freeze-readiness-2026-08-21.yml",
}
REQUIRED_TRANSFER_IDS = {
    *(f"RO-{index}" for index in range(1, 9)),
    *(f"AC-{index}" for index in range(1, 8)),
    "REV-1",
    "V1-1",
}
REQUIRED_CONSUMERS = {
    "003-monogenic-diabetes-demonstrator",
    "009-evidence-parameter-ledger",
    "011-bronchiectasis-demonstrator",
    "012-paediatric-burden-demonstrator",
    "014-atlas-api-release",
}
EXPECTED_ROUTE_CLASSES = {
    "repository_synthetic_fixtures",
    "exact_unmodified_allowlisted_source_assets",
    "source_derived_mapping_or_extracted_label_artifacts",
    "controlled_mixed_or_unresolved_sources",
}
DERIVED_QUARANTINE_ROUTE = (
    "already_public_in_git_no_additional_repository_owned_publication_export_"
    "rendering_activation_or_promotion_pending_rights_disposition"
)
EXPECTED_DERIVED_ARTIFACTS = {
    "manifests/semantics/track-008-v0.4-orpha-mondo-mappings.json": (
        "ae617b0826ce17915ddeff73be78f5b10f88bb9e89df634a86c0921d51df188e"
    ),
    "manifests/semantics/track-008-v0.4-provisional-naming.json": (
        "a4cb8c3cbb0e7f3dc0ad013252301ff811c0a07711161748ed57196baabee05f"
    ),
}
PROPOSED_CONTAINMENT = (
    "do_not_additionally_publish_export_render_activate_or_promote_pending_exact_"
    "rights_and_scope_disposition; historical_git_availability_persists"
)
FALSE_CLAIMS = {
    "track_008a_complete",
    "track_008_complete",
    "track_008b_complete",
    "track_009_unblocked",
    "scope_change_approved",
    "clinical_validation",
    "patient_community_authority",
    "derivative_publication_rights_complete",
    "independent_review",
}


def _mapping(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise Track008SplitError(f"cannot read split candidate {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track008SplitError("split candidate must be a mapping")
    return value


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise Track008SplitError(f"cannot hash baseline file {path}: {exc}") from exc


def _metadata(root: Path, track: str) -> dict[str, Any]:
    path = root / "conductor" / "tracks" / track / "metadata.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Track008SplitError(f"cannot read track metadata {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Track008SplitError(f"track metadata must be an object: {path}")
    return value


def _git(root: Path, revision: str) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", revision],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Track008SplitError(f"cannot resolve baseline revision {revision}") from exc


def _git_blob_sha256(root: Path, commit: str, relative: str) -> str:
    try:
        value = subprocess.run(
            ["git", "show", f"{commit}:{relative}"],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Track008SplitError(f"cannot read baseline Git blob: {relative}") from exc
    return hashlib.sha256(value).hexdigest()


def validate(candidate_path: Path, root: Path) -> None:
    """Validate exact binding, prospective scope, and unchanged dependency state."""
    candidate = _mapping(candidate_path)
    if candidate.get("schema_version") != "1.1.0":
        raise Track008SplitError("schema_version must be 1.1.0")
    if candidate.get("status") != "prospective_scope_change_candidate_preparation_only":
        raise Track008SplitError("candidate must remain preparation only")

    authorization = candidate.get("owner_authorization")
    if not isinstance(authorization, dict) or authorization.get("authorized_action") != (
        "prepare_scope_change_candidate_and_dependency_analysis"
    ):
        raise Track008SplitError("owner authorization must remain preparation-only")
    prohibited = set(authorization.get("prohibited_effects", []))
    if not {
        "mark_track_008_or_successors_complete",
        "register_or_activate_successor_tracks",
        "unblock_or_activate_track_009",
        "infer_final_owner_disposition",
    }.issubset(prohibited):
        raise Track008SplitError("owner authorization is missing prohibited effects")

    baseline = candidate.get("baseline")
    if not isinstance(baseline, dict):
        raise Track008SplitError("baseline must be a mapping")
    commit = str(baseline.get("repository_commit", ""))
    tree = str(baseline.get("repository_tree", ""))
    if _git(root, f"{commit}^{{tree}}") != tree:
        raise Track008SplitError("baseline commit does not own the declared tree")
    for field, relative in BASELINE_FILES.items():
        expected = baseline.get(field)
        if expected != _sha256(root / relative) or expected != _git_blob_sha256(
            root, commit, relative
        ):
            raise Track008SplitError(f"baseline hash drift: {relative}")

    historical = candidate.get("historical_track")
    if not isinstance(historical, dict) or historical != {
        "canonical_id": "008-semantic-backbone",
        "treatment": "preserved_umbrella_blocked_pending_exact_supersession_decision",
    }:
        raise Track008SplitError("historical Track 008 must remain a blocked umbrella")

    tracks = candidate.get("proposed_tracks")
    if not isinstance(tracks, list) or len(tracks) != 2:
        raise Track008SplitError("exactly two proposed tracks are required")
    by_alias = {row.get("alias"): row for row in tracks if isinstance(row, dict)}
    if set(by_alias) != {"008A", "008B"}:
        raise Track008SplitError("proposed aliases must be 008A and 008B")
    expected_ids = {
        "008A": "019-bounded-semantic-infrastructure",
        "008B": "020-clinical-community-semantic-assurance",
    }
    if any(by_alias[alias].get("canonical_id") != value for alias, value in expected_ids.items()):
        raise Track008SplitError("successors must use distinct canonical identifiers")
    if any(
        row.get("candidate_state") != "proposed_not_registered_or_active"
        for row in by_alias.values()
    ):
        raise Track008SplitError("successors must remain unregistered and inactive")

    transfers = candidate.get("requirement_transfer_matrix")
    if not isinstance(transfers, list):
        raise Track008SplitError("transferred requirement register must be a list")
    transfer_ids = [row.get("id") for row in transfers if isinstance(row, dict)]
    if set(transfer_ids) != REQUIRED_TRANSFER_IDS or len(transfer_ids) != len(
        REQUIRED_TRANSFER_IDS
    ):
        raise Track008SplitError("requirement transfer matrix is incomplete or duplicated")
    if any(not row.get("source") or not row.get("destination") for row in transfers):
        raise Track008SplitError("each requirement transfer needs source and destination")

    route_rows = candidate.get("artifact_routes", [])
    routes = {row.get("class"): row for row in route_rows if isinstance(row, dict)}
    if set(routes) != EXPECTED_ROUTE_CLASSES or len(route_rows) != len(EXPECTED_ROUTE_CLASSES):
        raise Track008SplitError("artifact route classes are incomplete or duplicated")
    synthetic = routes["repository_synthetic_fixtures"]
    if synthetic != {
        "class": "repository_synthetic_fixtures",
        "route": "repository_distributable_with_persistent_synthetic_non_clinical_context",
        "successor_gate": ["019-bounded-semantic-infrastructure"],
    }:
        raise Track008SplitError("synthetic artifact route must preserve context")
    exact_assets = routes["exact_unmodified_allowlisted_source_assets"]
    if exact_assets.get("route") != "source_specific_recorded_route_only" or set(
        exact_assets.get("exact_allowlist", [])
    ) != {
        "orphadata_july_2026_en_product1_xml",
        "mondo_v2026_08_04_three_assets",
        "hpo_v2026_06_23_nine_ontology_core_assets",
    }:
        raise Track008SplitError("exact source allowlist or route has drifted")
    derived = routes.get("source_derived_mapping_or_extracted_label_artifacts", {})
    if derived.get("route") != DERIVED_QUARANTINE_ROUTE or derived.get("successor_gate") != [
        "019-bounded-semantic-infrastructure",
        "020-clinical-community-semantic-assurance",
    ]:
        raise Track008SplitError(
            "source-derived artifacts must remain quarantined and assurance-gated"
        )
    artifacts = derived.get("artifacts", [])
    artifact_map = {
        artifact.get("path"): artifact.get("sha256")
        for artifact in artifacts
        if isinstance(artifact, dict)
    }
    if (
        artifact_map != EXPECTED_DERIVED_ARTIFACTS
        or len(artifacts) != len(EXPECTED_DERIVED_ARTIFACTS)
        or derived.get("public_exposure_observed_at") != "2026-08-21"
        or derived.get("proposed_containment") != PROPOSED_CONTAINMENT
    ):
        raise Track008SplitError("public source-derived exposure record is incomplete")
    for relative, expected in artifact_map.items():
        if expected != _sha256(root / relative):
            raise Track008SplitError("public source-derived artifact hash drift")
    controlled = routes["controlled_mixed_or_unresolved_sources"]
    if controlled.get("route") != "private_or_metadata_only" or controlled.get(
        "successor_gate"
    ) != ["020-clinical-community-semantic-assurance"]:
        raise Track008SplitError("controlled or unresolved source route has drifted")

    dependency = candidate.get("dependency_analysis")
    if not isinstance(dependency, dict):
        raise Track008SplitError("dependency analysis must be a mapping")
    current = dependency.get("current_track_009")
    if not isinstance(current, dict) or current != {
        "status": "blocked",
        "dependencies": ["002-public-source-acquisition", "008-semantic-backbone"],
        "activation": False,
    }:
        raise Track008SplitError("Track 009 current dependency state must remain blocked")
    if dependency.get("preparation_candidate_effect") != "none":
        raise Track008SplitError("preparation candidate cannot change dependencies")
    modes = dependency.get("proposed_modes", {})
    synthetic_mode = modes.get("synthetic_internal_preparation", {})
    if synthetic_mode.get("depends_on") != ["019-bounded-semantic-infrastructure"] or set(
        synthetic_mode.get("prohibited", [])
    ) != {
        "empirical_activation",
        "source_derived_use",
        "clinical_use",
        "patient_facing_use",
        "public_semantic_authority",
    }:
        raise Track008SplitError("synthetic mode boundary has drifted")
    exact_mode = modes.get("exact_unmodified_source_asset_handling", {})
    if (
        exact_mode.get("depends_on") != ["019-bounded-semantic-infrastructure"]
        or exact_mode.get("additional_gate") != "exact_source_specific_rights_route"
    ):
        raise Track008SplitError("exact-asset mode boundary has drifted")
    empirical = modes.get("source_derived_empirical_public_clinical_or_authority_bearing", {})
    if (
        empirical.get("depends_on")
        != [
            "019-bounded-semantic-infrastructure",
            "020-clinical-community-semantic-assurance",
        ]
        or modes.get("default") != "deny_unknown_or_unlabelled_mode"
    ):
        raise Track008SplitError("empirical and unknown modes must fail closed")

    consumers = candidate.get("downstream_consumer_inventory", [])
    consumer_ids = [row.get("track") for row in consumers if isinstance(row, dict)]
    if set(consumer_ids) != REQUIRED_CONSUMERS or len(consumer_ids) != len(REQUIRED_CONSUMERS):
        raise Track008SplitError("downstream consumer inventory is incomplete or duplicated")
    if any(not row.get("proposed_gate") for row in consumers):
        raise Track008SplitError("each downstream consumer requires a proposed gate")

    if _metadata(root, "008-semantic-backbone").get("status") != "blocked":
        raise Track008SplitError("current Track 008 metadata must remain blocked")
    track_009 = _metadata(root, "009-evidence-parameter-ledger")
    if track_009.get("status") != "blocked" or track_009.get("dependencies") != [
        "002-public-source-acquisition",
        "008-semantic-backbone",
    ]:
        raise Track008SplitError("current Track 009 metadata or dependency has changed")

    claims = candidate.get("claims")
    if not isinstance(claims, dict) or any(claims.get(name) is not False for name in FALSE_CLAIMS):
        raise Track008SplitError(
            "all completion, activation and authority claims must remain false"
        )
    next_gate = candidate.get("next_gate")
    if not isinstance(next_gate, dict) or next_gate.get("required") != (
        "new_simulated_panel_packet_and_exact_candidate_owner_disposition"
    ):
        raise Track008SplitError("the next exact panel and owner gate is required")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.candidate.resolve(), args.root.resolve())
    except Track008SplitError as exc:
        print(f"Track 008 split candidate failed: {exc}")
        return 1
    print("Track 008 split candidate passed; both tracks and Track 009 remain blocked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
