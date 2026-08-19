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


def reconcile_paediatric_synthetic_linkage(
    fixture: Mapping[str, Any],
    dependency_bindings: Mapping[str, Any],
    *,
    disclosure_threshold: int,
    created_at: str,
) -> dict[str, Any]:
    """Summarise invented linked tables without emitting row-level identifiers."""
    if fixture.get("status") != "synthetic_only":
        raise DemonstratorError("Track 012 reconciliation permits synthetic_only fixtures only")
    if isinstance(disclosure_threshold, bool) or disclosure_threshold < 2:
        raise DemonstratorError("disclosure threshold must be an integer of at least two")
    claims = dependency_bindings.get("claims")
    blocked = (
        "controlled_data_activation",
        "clinical_interpretation",
        "policy_interpretation",
        "contract_frozen",
    )
    if not isinstance(claims, Mapping) or any(claims.get(key) is not False for key in blocked):
        raise DemonstratorError(
            "controlled-data, clinical, policy and contract activation must remain false"
        )
    dependencies = dependency_bindings.get("dependencies")
    expected = {"004", "005", "008", "009", "010", "011"}
    if (
        not isinstance(dependencies, list)
        or {item.get("track_id") for item in dependencies if isinstance(item, Mapping)} != expected
    ):
        raise DemonstratorError("exact Track 004, 005 and 008-011 bindings are required")

    tables = fixture.get("tables")
    if not isinstance(tables, Mapping):
        raise DemonstratorError("synthetic linked tables are required")
    people = _unique_rows(tables.get("person"), "person", "person_id")
    person_ids = set(people)
    diagnoses = _rows_with_known_people(tables.get("diagnosis"), "diagnosis", person_ids)
    admissions = _rows_with_known_people(tables.get("admission"), "admission", person_ids)
    deaths = _rows_with_known_people(tables.get("death"), "death", person_ids)
    costs = _rows_with_known_people(tables.get("cost"), "cost", person_ids)
    admission_ids = [row.get("admission_id") for row in admissions]
    if len(admission_ids) != len(set(admission_ids)) or any(not value for value in admission_ids):
        raise DemonstratorError("admission identifiers must be present and unique locally")

    diagnoses_by_person: dict[str, set[str]] = {person_id: set() for person_id in person_ids}
    for row in diagnoses:
        diagnoses_by_person[str(row["person_id"])].add(str(row.get("code", "")))
    jurisdictions: dict[str, int] = {}
    for row in people.values():
        jurisdiction = str(row.get("jurisdiction", ""))
        if not jurisdiction:
            raise DemonstratorError("every synthetic person requires a jurisdiction")
        jurisdictions[jurisdiction] = jurisdictions.get(jurisdiction, 0) + 1
    equity_rows = [
        {
            "jurisdiction": jurisdiction,
            "count": count if count >= disclosure_threshold else None,
            "suppressed": count < disclosure_threshold,
        }
        for jurisdiction, count in sorted(jurisdictions.items())
    ]
    known_deaths = sum(row.get("year") is not None for row in deaths)
    cost_people = {str(row["person_id"]) for row in costs}
    core = {
        "analysis_id": "rbc-p004-bounded-synthetic-linkage",
        "created_at": created_at,
        "population": {
            "deduplicated_people": len(person_ids),
            "people_with_diagnosis": sum(bool(values) for values in diagnoses_by_person.values()),
            "people_with_multiple_diagnoses": sum(
                len(values) > 1 for values in diagnoses_by_person.values()
            ),
        },
        "utilisation": {
            "admissions": len(admissions),
            "people_with_admission": len({str(row["person_id"]) for row in admissions}),
        },
        "mortality": {
            "known_deaths": known_deaths,
            "unknown_death_status": len(person_ids) - known_deaths,
        },
        "cost": {
            "observed_people": len(cost_people),
            "missing_people": len(person_ids - cost_people),
            "currency": "SYN",
            "total": sum(_finite_nonnegative(row.get("amount"), "cost amount") for row in costs),
        },
        "equity_breakdown": equity_rows,
        "disclosure_threshold": disclosure_threshold,
        "uncertainty": {
            "death_status_missing_people": len(person_ids) - known_deaths,
            "cost_missing_people": len(person_ids - cost_people),
            "modelled_values": 0,
            "imputation_performed": False,
        },
        "dependency_bindings": [dict(item) for item in dependencies],
        "activation_state": "synthetic_only",
        "controlled_data_activation": False,
        "clinical_interpretation": False,
        "policy_interpretation": False,
        "contract_frozen": False,
        "limitations": list(fixture.get("limitations", [])),
    }
    return {"schema_version": "0.1.0", "receipt_id": content_id("demo", core), **core}


def _unique_rows(value: Any, label: str, identifier: str) -> dict[str, Mapping[str, Any]]:
    if not isinstance(value, list):
        raise DemonstratorError(f"{label} table must be a list")
    rows: dict[str, Mapping[str, Any]] = {}
    for row in value:
        if not isinstance(row, Mapping) or not row.get(identifier):
            raise DemonstratorError(f"{label} rows require {identifier}")
        key = str(row[identifier])
        if key in rows:
            raise DemonstratorError(f"duplicate {label} {identifier}: {key}")
        rows[key] = row
    return rows


def _rows_with_known_people(
    value: Any, label: str, person_ids: set[str]
) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        raise DemonstratorError(f"{label} table must be a list")
    rows: list[Mapping[str, Any]] = []
    for row in value:
        if not isinstance(row, Mapping) or str(row.get("person_id", "")) not in person_ids:
            raise DemonstratorError(f"{label} row references an unknown person")
        rows.append(row)
    return rows


__all__.extend(["reconcile_paediatric_synthetic_linkage"])
