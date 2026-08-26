"""Bounded missingness and structural-scenario assurance for Track 010."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from rareburden.ledger import LedgerError, ParameterLedger
from rareburden.model import ModelError, run_analysis_spec
from rareburden.provenance import content_id


def assess_analysis_estimability(
    specification: Mapping[str, Any], ledger: ParameterLedger
) -> dict[str, Any]:
    """Return explicit missing-input reasons without silently imputing values."""
    missing: list[str] = []
    reasons: list[str] = []
    for field in ("left_parameter_id", "right_parameter_id"):
        value = specification.get(field)
        if not isinstance(value, str) or not value:
            reasons.append(f"analysis specification lacks {field}")
            continue
        try:
            ledger.get(value)
        except LedgerError:
            missing.append(value)
            reasons.append(f"parameter is unavailable: {value}")
    return {
        "schema_version": "0.1.0",
        "analysis_id": str(specification.get("analysis_id", "")),
        "estimable": not reasons,
        "missing_parameter_ids": sorted(set(missing)),
        "reasons": reasons,
        "imputation_performed": False,
    }


def run_bounded_synthetic_analysis(
    specification: dict[str, Any],
    ledger: ParameterLedger,
    source_release_bindings: Mapping[str, Any],
    quality_disposition: dict[str, Any],
    *,
    created_at: str,
) -> dict[str, Any]:
    """Run only a synthetic analysis after validating Track 009 release links."""
    if specification.get("intended_use") != "synthetic_assurance":
        raise ModelError("bounded reconciliation permits synthetic_assurance only")
    claims = source_release_bindings.get("claims")
    if (
        not isinstance(claims, Mapping)
        or claims.get("empirical_parameter_activation") is not False
        or claims.get("v0_4_contract_frozen") is not False
    ):
        raise ModelError("empirical source activation must remain explicitly false")
    records = source_release_bindings.get("source_releases")
    if not isinstance(records, list):
        raise ModelError("source-release binding document is incomplete")
    releases = {
        str(record.get("source_release_id")): record
        for record in records
        if isinstance(record, Mapping)
    }
    ledger.validate_source_release_links(releases)
    result = run_analysis_spec(
        specification,
        ledger,
        created_at=created_at,
        quality_disposition=quality_disposition,
    )
    result["summary"] = {
        key: round(value, 6) if isinstance(value, float) else value
        for key, value in result["summary"].items()
    }
    binding_bytes = json.dumps(
        source_release_bindings, sort_keys=True, separators=(",", ":")
    ).encode()
    return {
        **result,
        "source_release_binding_sha256": hashlib.sha256(binding_bytes).hexdigest(),
        "activation_state": "synthetic_only",
        "contract_frozen": False,
        "empirical_parameter_activation": False,
        "interpretation": "repository-owned synthetic assurance; not an empirical burden estimate",
        "summary_precision_decimal_places": 6,
    }


def run_structural_scenarios(
    scenarios: Mapping[str, dict[str, Any]],
    ledger: ParameterLedger,
    *,
    created_at: str,
) -> dict[str, Any]:
    """Run bounded synthetic scenarios and retain every input lineage identity."""
    if "baseline" not in scenarios:
        raise ModelError("structural scenarios require a baseline")
    if not 2 <= len(scenarios) <= 20:
        raise ModelError("structural scenarios require between 2 and 20 alternatives")
    if any(not isinstance(name, str) or not name.strip() for name in scenarios):
        raise ModelError("scenario names must be non-empty strings")

    baseline = scenarios["baseline"]
    invariant_fields = ("analysis_id", "estimand", "output_unit", "intended_use")
    outputs: dict[str, dict[str, Any]] = {}
    for name in sorted(scenarios):
        specification = scenarios[name]
        for field in invariant_fields:
            if specification.get(field) != baseline.get(field):
                raise ModelError(f"scenario {name!r} changes invariant field {field}")
        estimability = assess_analysis_estimability(specification, ledger)
        if not estimability["estimable"]:
            raise ModelError(f"scenario {name!r} is non-estimable: {estimability['reasons']}")
        outputs[name] = run_analysis_spec(specification, ledger, created_at=created_at)

    baseline_mean = float(outputs["baseline"]["summary"]["mean"])
    records = [
        {
            "scenario": name,
            "analysis_result_id": result["analysis_result_id"],
            "left_parameter_id": result["left_parameter_id"],
            "left_parameter_fingerprint": result["left_parameter_fingerprint"],
            "right_parameter_id": result["right_parameter_id"],
            "right_parameter_fingerprint": result["right_parameter_fingerprint"],
            "mean": result["summary"]["mean"],
            "lower": result["summary"]["lower"],
            "upper": result["summary"]["upper"],
            "interval_probability": result["summary"]["interval_probability"],
            "absolute_change_from_baseline": float(result["summary"]["mean"]) - baseline_mean,
            "intended_use": result["intended_use"],
            "activation_state": result["activation_state"],
            "interpretation": result["interpretation"],
            "limitations": result["limitations"],
        }
        for name, result in sorted(outputs.items())
    ]
    core = {
        "analysis_id": baseline["analysis_id"],
        "ledger_id": ledger.document["ledger_id"],
        "created_at": created_at,
        "scenarios": records,
    }
    return {
        "schema_version": "0.1.0",
        "scenario_result_id": content_id("scn", core),
        **core,
    }


__all__ = [
    "assess_analysis_estimability",
    "run_bounded_synthetic_analysis",
    "run_structural_scenarios",
]
