"""Transparent evidence-quality and transportability assessments.

The module deliberately avoids numeric composite quality scores.  Domain judgements,
rationales, evidence references, and the final use decision remain separately visible so
reviewers can disagree with individual decisions without reverse-engineering a score.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from rareburden.provenance import content_id
from rareburden.schema import SchemaValidationError, validate_instance


class QualityAssessmentError(ValueError):
    """Raised when a quality or transportability record is internally incoherent."""


def triangulate_synthetic_estimates(
    primary: Mapping[str, Any],
    comparators: Sequence[Mapping[str, Any]],
    *,
    tolerance: float,
) -> dict[str, Any]:
    """Compare invented estimates without treating agreement as validation.

    ``primary`` and each comparator require an ``estimate`` and ``source_id``.
    The result reports relative differences and labels all comparisons as
    synthetic assurance; it cannot establish empirical calibration or external
    validity.
    """
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)):
        raise QualityAssessmentError("tolerance must be numeric")
    tolerance_value = float(tolerance)
    if not math.isfinite(tolerance_value) or tolerance_value < 0 or tolerance_value >= 1:
        raise QualityAssessmentError("tolerance must be between zero and one")
    rows: list[dict[str, Any]] = []
    primary_value = _finite_nonnegative_number(primary.get("estimate"), "primary estimate")
    if not primary.get("source_id"):
        raise QualityAssessmentError("primary source_id is required")
    for comparator in comparators:
        if not comparator.get("source_id"):
            raise QualityAssessmentError("comparator source_id is required")
        value = _finite_nonnegative_number(comparator.get("estimate"), "comparator estimate")
        relative_difference = _relative_change(primary_value, value)
        rows.append(
            {
                "source_id": str(comparator["source_id"]),
                "estimate": value,
                "absolute_difference": abs(value - primary_value),
                "relative_difference": relative_difference,
                "within_declared_tolerance": (
                    relative_difference <= tolerance_value
                    if relative_difference is not None
                    else None
                ),
            }
        )
    core = {
        "schema_version": "1.0.0",
        "method": "synthetic-estimate-triangulation",
        "intended_use": "synthetic_assurance",
        "primary": {"source_id": str(primary["source_id"]), "estimate": primary_value},
        "tolerance": tolerance_value,
        "comparisons": rows,
        "interpretation": "agreement is a debugging signal, not empirical validation",
        "limitations": [
            "All inputs are synthetic or reference fixtures.",
            "Comparators are not independent human or external validation.",
            "Tolerance is a declared assurance threshold, not a scientific acceptance limit.",
        ],
    }
    return {"receipt_id": content_id("tri", core), **core}


def assess_synthetic_sensitivity(
    baseline: Mapping[str, Any], scenarios: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Report bounded one-at-a-time synthetic sensitivity without inference.

    Each scenario supplies a non-negative estimate and a changed parameter.
    The receipt exposes absolute and relative deltas and labels decision
    sensitivity as an assurance diagnostic, never as an empirical result.
    """
    baseline_value = _finite_nonnegative_number(baseline.get("estimate"), "baseline estimate")
    if not baseline.get("source_id"):
        raise QualityAssessmentError("baseline source_id is required")
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        parameter = scenario.get("parameter")
        if not isinstance(parameter, str) or not parameter.strip():
            raise QualityAssessmentError("scenario parameter is required")
        value = _finite_nonnegative_number(scenario.get("estimate"), "scenario estimate")
        rows.append(
            {
                "scenario_id": str(scenario.get("scenario_id", parameter)),
                "parameter": parameter,
                "estimate": value,
                "absolute_change": abs(value - baseline_value),
                "relative_change": _relative_change(baseline_value, value),
            }
        )
    core = {
        "schema_version": "1.0.0",
        "method": "synthetic-one-at-a-time-sensitivity",
        "intended_use": "synthetic_assurance",
        "baseline": {"source_id": str(baseline["source_id"]), "estimate": baseline_value},
        "scenarios": rows,
        "interpretation": "parameter sensitivity is a debugging signal, not empirical evidence",
        "limitations": [
            "All inputs are synthetic or reference fixtures.",
            "Scenarios are not calibrated uncertainty intervals or policy analysis.",
            "Decision sensitivity does not establish transportability or validity.",
        ],
    }
    return {"receipt_id": content_id("sens", core), **core}


def _relative_change(baseline: float, value: float) -> float | None:
    """Return null when a relative change is undefined or unrepresentable."""
    if baseline == 0:
        return None
    result = abs(value - baseline) / baseline
    return result if math.isfinite(result) else None


def run_synthetic_model_sensitivity(
    model: Callable[[Mapping[str, float]], float],
    parameters: Mapping[str, float],
    variations: Mapping[str, Sequence[float]],
    *,
    model_id: str,
) -> dict[str, Any]:
    """Execute a declared synthetic model at baseline and one parameter at a time.

    The callable receives a fresh parameter dictionary for every execution.
    Variations are absolute replacement values. Inputs, model identity and
    outputs are retained in the receipt for reproducible scenario inspection.
    """
    if not isinstance(model_id, str) or not model_id.strip():
        raise QualityAssessmentError("model_id is required")
    if not parameters or not variations or set(variations) - set(parameters):
        raise QualityAssessmentError("variations require known baseline parameters")
    baseline = {
        key: _finite_nonnegative_number(value, "parameter") for key, value in parameters.items()
    }
    runs: list[tuple[str, dict[str, float]]] = []
    for parameter, values in variations.items():
        if not values:
            raise QualityAssessmentError("each parameter requires variation values")
        for value in values:
            changed = dict(baseline)
            changed[parameter] = _finite_nonnegative_number(value, "variation")
            runs.append((parameter, changed))
    baseline_output = _finite_nonnegative_number(model(dict(baseline)), "model output")
    scenarios = [
        {
            "scenario_id": f"scenario-{index}",
            "parameter": parameter,
            "estimate": _finite_nonnegative_number(model(dict(values)), "model output"),
        }
        for index, (parameter, values) in enumerate(runs)
    ]
    comparison = assess_synthetic_sensitivity(
        {"source_id": model_id, "estimate": baseline_output}, scenarios
    )
    core = {
        "method": "executed-synthetic-model-sensitivity",
        "intended_use": "synthetic_assurance",
        "model_id": model_id,
        "baseline_parameters": baseline,
        "scenario_parameters": [values for _, values in runs],
        "comparison": comparison,
        "relative_change_policy": "null for zero baseline or floating-point overflow",
    }
    return {"receipt_id": content_id("sensrun", core), **core}


def _finite_nonnegative_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise QualityAssessmentError(f"{label} must be numeric")
    numeric = float(value)
    if numeric < 0 or numeric != numeric or numeric in {float("inf"), float("-inf")}:
        raise QualityAssessmentError(f"{label} must be finite and non-negative")
    return numeric


_RELEASE_MATURITY: dict[str, dict[str, tuple[str, ...]]] = {
    "synthetic_assurance": {
        "allowed_claims": ("demonstrates executable synthetic assurance only",),
        "prohibited_claims": ("empirical estimate", "representativeness", "policy recommendation"),
    },
    "metadata_only": {
        "allowed_claims": ("describes source metadata or access capability",),
        "prohibited_claims": ("fitness for use", "empirical estimate", "representativeness"),
    },
    "internally_validated": {
        "allowed_claims": ("passes internal validation for the declared scope",),
        "prohibited_claims": (
            "independent reproduction",
            "external replication",
            "global representativeness",
        ),
    },
    "independently_reproduced": {
        "allowed_claims": ("has an independent reproduction receipt for the declared scope",),
        "prohibited_claims": ("external replication", "global representativeness"),
    },
    "externally_replicated": {
        "allowed_claims": ("has documented external replication for the declared scope",),
        "prohibited_claims": ("global representativeness",),
    },
}


def release_language_for_maturity(maturity: str) -> dict[str, Any]:
    """Return conservative allowed and prohibited claim language for a maturity state."""
    try:
        policy = _RELEASE_MATURITY[maturity]
    except KeyError as exc:
        raise QualityAssessmentError(f"Unsupported release maturity: {maturity!r}") from exc
    return {
        "maturity": maturity,
        "allowed_claims": list(policy["allowed_claims"]),
        "prohibited_claims": list(policy["prohibited_claims"]),
        "note": (
            "Claim language remains bounded by source rights, governance and named review gates."
        ),
    }


_HIGH_RISK = {"high_concern", "unclear"}
_MATERIAL_DIFFERENCES = {"moderate", "high", "unknown"}


def _without_identifier(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def _validate_content_identifier(value: Mapping[str, Any], *, field: str, prefix: str) -> None:
    expected = content_id(prefix, _without_identifier(value, field))
    if value.get(field) != expected:
        raise QualityAssessmentError(f"{field} does not match the assessment content")


def build_evidence_assessment(core: Mapping[str, Any]) -> dict[str, Any]:
    """Add a deterministic identifier to an evidence-assessment core."""
    materialised = dict(core)
    materialised.pop("assessment_id", None)
    return {
        **materialised,
        "assessment_id": content_id("eqa", materialised),
    }


def validate_evidence_assessment(
    assessment: Mapping[str, Any], schema: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate schema and non-opaque quality-decision invariants."""
    value = dict(assessment)
    try:
        validate_instance(value, dict(schema), label="evidence_assessment")
    except SchemaValidationError as exc:
        raise QualityAssessmentError(str(exc)) from exc
    _validate_content_identifier(value, field="assessment_id", prefix="eqa")

    domains = value["domains"]
    names = [str(item["domain"]) for item in domains]
    if len(names) != len(set(names)):
        raise QualityAssessmentError("Evidence assessment contains duplicate domains")
    for item in domains:
        if item["judgement"] == "not_applicable" and not item["rationale"].strip():
            raise QualityAssessmentError(
                f"{item['domain']}: not_applicable requires an explicit rationale"
            )
    decision = value["overall_judgement"]["decision"]
    high_risk = sorted(str(item["domain"]) for item in domains if item["judgement"] in _HIGH_RISK)
    if decision == "direct_use" and high_risk:
        raise QualityAssessmentError(
            "direct_use is incompatible with high-concern or unclear domains: "
            + ", ".join(high_risk)
        )
    if decision == "unsuitable" and not high_risk:
        raise QualityAssessmentError(
            "unsuitable requires at least one high-concern or unclear domain"
        )
    return value


def build_transportability_assessment(core: Mapping[str, Any]) -> dict[str, Any]:
    """Add a deterministic identifier to a transportability-assessment core."""
    materialised = dict(core)
    materialised.pop("assessment_id", None)
    return {
        **materialised,
        "assessment_id": content_id("tra", materialised),
    }


def validate_transportability_assessment(
    assessment: Mapping[str, Any], schema: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate schema and fail on contradictory transfer decisions."""
    value = dict(assessment)
    try:
        validate_instance(value, dict(schema), label="transportability_assessment")
    except SchemaValidationError as exc:
        raise QualityAssessmentError(str(exc)) from exc
    _validate_content_identifier(value, field="assessment_id", prefix="tra")

    differences = value["differences"]
    domains = [str(item["domain"]) for item in differences]
    if len(domains) != len(set(domains)):
        raise QualityAssessmentError("Transportability assessment contains duplicate domains")
    material = sorted(
        str(item["domain"]) for item in differences if item["materiality"] in _MATERIAL_DIFFERENCES
    )
    strategy = value["method"]["strategy"]
    use = value["judgement"]["use"]
    multiplier = float(value["judgement"]["uncertainty_multiplier"])

    if use == "direct" and material:
        raise QualityAssessmentError(
            "direct transfer is incompatible with moderate, high, unknown differences: "
            + ", ".join(material)
        )
    if strategy == "no_transfer" and use != "not_transportable":
        raise QualityAssessmentError("no_transfer strategy requires not_transportable use")
    if use == "not_transportable" and strategy != "no_transfer":
        raise QualityAssessmentError("not_transportable use requires no_transfer strategy")
    if use in {"adjusted", "sensitivity_only"} and multiplier == 1:
        raise QualityAssessmentError(
            "adjusted or sensitivity-only transfer requires uncertainty_multiplier greater than 1"
        )
    if use == "direct" and strategy != "direct_transfer":
        raise QualityAssessmentError("direct use requires direct_transfer strategy")
    return value


def release_eligibility(
    *,
    evidence_assessments: Sequence[Mapping[str, Any]],
    transportability_assessments: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarise visible decisions without collapsing them into a quality score."""
    evidence_decisions = sorted(
        {str(item["overall_judgement"]["decision"]) for item in evidence_assessments}
    )
    transport_decisions = sorted(
        {str(item["judgement"]["use"]) for item in transportability_assessments}
    )
    blockers: list[str] = []
    if any(item in {"unsuitable", "unclear"} for item in evidence_decisions):
        blockers.append("evidence quality decision blocks primary release use")
    if any(item in {"not_transportable", "unclear"} for item in transport_decisions):
        blockers.append("transportability decision blocks target-population use")
    if "sensitivity_only" in evidence_decisions or "sensitivity_only" in transport_decisions:
        blockers.append("at least one input is restricted to sensitivity analysis")
    return {
        "eligible_for_primary_analysis": not blockers,
        "evidence_decisions": evidence_decisions,
        "transportability_decisions": transport_decisions,
        "blockers": blockers,
        "note": "This is a rule-based disposition, not a numeric or weighted quality score.",
    }


def build_quality_disposition(
    *,
    analysis_id: str,
    created_at: str,
    intended_use: str,
    evidence_assessments: Sequence[Mapping[str, Any]],
    transportability_assessments: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a content-addressed, use-specific fitness-for-use disposition.

    Synthetic assurance remains possible when evidence is restricted to sensitivity
    analysis, but that restriction stays visible and blocks an empirical primary claim.
    """
    if intended_use not in {
        "synthetic_assurance",
        "exploratory",
        "primary_estimate",
        "policy_decision",
    }:
        raise QualityAssessmentError(f"Unsupported intended_use: {intended_use!r}")
    summary = release_eligibility(
        evidence_assessments=evidence_assessments,
        transportability_assessments=transportability_assessments,
    )
    evidence_decisions = {str(item) for item in summary["evidence_decisions"]}
    transport_decisions = {str(item) for item in summary["transportability_decisions"]}
    synthetic_hard_blockers: list[str] = []
    if evidence_decisions & {"unsuitable", "unclear"}:
        synthetic_hard_blockers.append(
            "evidence is unsuitable or unclear even for the declared synthetic assurance use"
        )
    if transport_decisions & {"not_transportable", "unclear"}:
        synthetic_hard_blockers.append(
            "transportability is not established even for the declared synthetic assurance use"
        )
    core = {
        "analysis_id": analysis_id,
        "created_at": created_at,
        "intended_use": intended_use,
        "evidence_assessment_ids": sorted(
            {str(item["assessment_id"]) for item in evidence_assessments}
        ),
        "transportability_assessment_ids": sorted(
            {str(item["assessment_id"]) for item in transportability_assessments}
        ),
        "eligible_for_primary_analysis": bool(summary["eligible_for_primary_analysis"]),
        "eligible_for_synthetic_assurance": (
            intended_use == "synthetic_assurance" and not synthetic_hard_blockers
        ),
        "evidence_decisions": list(summary["evidence_decisions"]),
        "transportability_decisions": list(summary["transportability_decisions"]),
        "blockers": sorted(
            {str(item) for item in summary["blockers"]} | set(synthetic_hard_blockers)
        ),
        "note": summary["note"],
    }
    materialised = {"schema_version": "1.0.0", **core}
    return {
        **materialised,
        "disposition_id": content_id("qdp", materialised),
    }


def validate_quality_disposition(
    disposition: Mapping[str, Any],
    schema: Mapping[str, Any],
    *,
    evidence_assessments: Sequence[Mapping[str, Any]] | None = None,
    transportability_assessments: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate schema, content identity and optional assessment closure."""
    value = dict(disposition)
    try:
        validate_instance(value, dict(schema), label="quality_disposition")
    except SchemaValidationError as exc:
        raise QualityAssessmentError(str(exc)) from exc
    _validate_content_identifier(value, field="disposition_id", prefix="qdp")
    if value["eligible_for_primary_analysis"] and value["blockers"]:
        raise QualityAssessmentError("eligible_for_primary_analysis cannot coexist with blockers")
    if (
        value["intended_use"] == "synthetic_assurance"
        and not value["eligible_for_synthetic_assurance"]
    ):
        raise QualityAssessmentError(
            "synthetic_assurance intended use must remain executable as assurance"
        )
    if evidence_assessments is not None or transportability_assessments is not None:
        evidence = evidence_assessments or []
        transportability = transportability_assessments or []
        rebuilt = build_quality_disposition(
            analysis_id=str(value["analysis_id"]),
            created_at=str(value["created_at"]),
            intended_use=str(value["intended_use"]),
            evidence_assessments=evidence,
            transportability_assessments=transportability,
        )
        if rebuilt != value:
            raise QualityAssessmentError(
                "Quality disposition differs from the supplied assessment set"
            )
    return value


def verify_parameter_assessment_closure(
    *,
    parameters: Sequence[Mapping[str, Any]],
    parameter_ids: list[str],
    evidence_assessments: Sequence[Mapping[str, Any]],
    transportability_assessments: Sequence[Mapping[str, Any]],
    disposition: Mapping[str, Any],
) -> list[str]:
    """Verify that analysis parameters, assessments and disposition form a closed graph."""
    failures: list[str] = []
    parameter_map = {str(item.get("parameter_id", "")): item for item in parameters}
    evidence_map = {str(item.get("assessment_id", "")): item for item in evidence_assessments}
    transport_map = {
        str(item.get("assessment_id", "")): item for item in transportability_assessments
    }
    selected_evidence: set[str] = set()
    selected_transport: set[str] = set()
    for parameter_id in parameter_ids:
        record = parameter_map.get(parameter_id)
        if record is None:
            failures.append(f"quality closure references unknown parameter: {parameter_id}")
            continue
        evidence_ids = [str(item) for item in record.get("evidence_assessment_ids", [])]
        if not evidence_ids:
            failures.append(f"parameter lacks an evidence assessment: {parameter_id}")
        for assessment_id in evidence_ids:
            selected_evidence.add(assessment_id)
            assessment = evidence_map.get(assessment_id)
            if assessment is None:
                failures.append(
                    f"parameter {parameter_id} references missing evidence assessment "
                    f"{assessment_id}"
                )
                continue
            subject = assessment.get("subject", {})
            if not isinstance(subject, Mapping) or subject.get("subject_type") != "parameter":
                failures.append(f"evidence assessment does not assess a parameter: {assessment_id}")
            elif subject.get("subject_id") != parameter_id:
                failures.append(
                    f"evidence assessment {assessment_id} assesses "
                    f"{subject.get('subject_id')!r}, not {parameter_id!r}"
                )
        for assessment_id in [
            str(item) for item in record.get("transportability_assessment_ids", [])
        ]:
            selected_transport.add(assessment_id)
            assessment = transport_map.get(assessment_id)
            if assessment is None:
                failures.append(
                    f"parameter {parameter_id} references missing transportability "
                    f"assessment {assessment_id}"
                )
            elif assessment.get("parameter_id") != parameter_id:
                failures.append(
                    f"transportability assessment {assessment_id} concerns "
                    f"{assessment.get('parameter_id')!r}, not {parameter_id!r}"
                )
    declared_evidence = {str(item) for item in disposition.get("evidence_assessment_ids", [])}
    declared_transport = {
        str(item) for item in disposition.get("transportability_assessment_ids", [])
    }
    if selected_evidence != declared_evidence:
        failures.append(
            "quality disposition evidence-assessment set differs from selected parameter records"
        )
    if selected_transport != declared_transport:
        failures.append(
            "quality disposition transportability set differs from selected parameter records"
        )
    return sorted(set(failures))


__all__ = [
    "QualityAssessmentError",
    "build_evidence_assessment",
    "build_quality_disposition",
    "build_transportability_assessment",
    "release_eligibility",
    "triangulate_synthetic_estimates",
    "validate_evidence_assessment",
    "validate_quality_disposition",
    "validate_transportability_assessment",
    "verify_parameter_assessment_closure",
]
