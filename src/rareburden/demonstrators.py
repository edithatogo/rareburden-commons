"""Bounded demonstrator reconciliations that cannot activate empirical claims."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from rareburden.provenance import content_id
from rareburden.semantics import DiseaseHierarchy, SemanticValidationError


class DemonstratorError(ValueError):
    """Raised when a bounded demonstrator contract is unsafe or incomplete."""


def reconcile_bronchiectasis_synthetic_profile(
    profile: Mapping[str, Any],
    hierarchy: DiseaseHierarchy,
    dependency_bindings: Mapping[str, Any],
    *,
    created_at: str,
) -> dict[str, Any]:
    """Reconcile an explicit synthetic composition without inferring aetiology.

    The mutually exclusive categories are checked through the Track 008
    hierarchy. Multi-aetiology observations remain a separate structural bucket
    and are never added to an individual aetiology. This is an assurance receipt,
    not an epidemiological estimator.
    """
    if profile.get("intended_use") != "synthetic_assurance":
        raise DemonstratorError("Track 011 reconciliation permits synthetic_assurance only")
    claims = dependency_bindings.get("claims")
    if not isinstance(claims, Mapping) or any(
        claims.get(key) is not False
        for key in ("empirical_activation", "clinical_interpretation", "contract_frozen")
    ):
        raise DemonstratorError("empirical, clinical and contract activation must remain false")
    dependencies = dependency_bindings.get("dependencies")
    if not isinstance(dependencies, list) or {
        item.get("track_id") for item in dependencies if isinstance(item, Mapping)
    } != {"008", "009", "010"}:
        raise DemonstratorError("exact Track 008, 009 and 010 dependency bindings are required")
    if any(
        not isinstance(item.get("sha256"), str) or len(item["sha256"]) != 64
        for item in dependencies
        if isinstance(item, Mapping)
    ):
        raise DemonstratorError("every dependency binding requires an exact SHA-256")

    context = profile.get("context")
    required_context = ("geography", "period", "age_band", "setting", "case_definition")
    if not isinstance(context, Mapping) or any(not context.get(key) for key in required_context):
        raise DemonstratorError(
            "profile requires explicit geography, period, age, setting and case definition"
        )
    denominator = _finite_nonnegative(profile.get("denominator"), "denominator")
    counts = profile.get("mutually_exclusive_counts")
    if not isinstance(counts, Mapping):
        raise DemonstratorError("mutually_exclusive_counts must be a mapping")
    try:
        exclusive = hierarchy.aggregate_counts("bronchiectasis-composition", counts)
    except SemanticValidationError as exc:
        raise DemonstratorError(str(exc)) from exc
    multi = _finite_nonnegative(profile.get("multi_aetiology_count"), "multi_aetiology_count")
    unknown = _finite_nonnegative(profile.get("unknown_count"), "unknown_count")
    accounted = float(exclusive["value"]) + multi + unknown
    if accounted > denominator:
        raise DemonstratorError("explicit composition exceeds the declared denominator")
    unaccounted = denominator - accounted
    core = {
        "analysis_id": profile.get("analysis_id"),
        "created_at": created_at,
        "context": dict(context),
        "denominator": denominator,
        "hierarchy_id": hierarchy.document["hierarchy_id"],
        "hierarchy_version": hierarchy.document["version"],
        "hierarchy_fingerprint": hierarchy.fingerprint,
        "exclusive_composition": exclusive,
        "multi_aetiology_count": multi,
        "unknown_count": unknown,
        "unaccounted_count": unaccounted,
        "dependency_bindings": [dict(item) for item in dependencies],
        "activation_state": "synthetic_only",
        "empirical_activation": False,
        "clinical_interpretation": False,
        "contract_frozen": False,
        "limitations": list(profile.get("limitations", [])),
    }
    return {"schema_version": "0.1.0", "receipt_id": content_id("demo", core), **core}


def _finite_nonnegative(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DemonstratorError(f"{label} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0:
        raise DemonstratorError(f"{label} must be finite and non-negative")
    return numeric


__all__ = ["DemonstratorError", "reconcile_bronchiectasis_synthetic_profile"]
