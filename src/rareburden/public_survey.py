"""Bounded questionnaire-only NHANES domain ratio; no clinical inference."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from collections.abc import Iterable, Mapping
from typing import Any

from rareburden.node import NodeExportError
from rareburden.node_policy_store import DurableNodePolicyStore


def _numeric(value: Any, *, integer: bool = False) -> float:
    try:
        if type(value) not in (int, float):
            raise ValueError
        number = float(value)
        if not math.isfinite(number) or (integer and not number.is_integer()):
            raise ValueError
        return number
    except (ValueError, OverflowError):
        raise NodeExportError("invalid survey numeric field") from None


def _key(value: Any) -> int:
    if type(value) is int and not 0 < value <= 2**53:
        raise NodeExportError("invalid survey identifier or design code")
    number = _numeric(value, integer=True)
    if not 0 < number <= 2**53:
        raise NodeExportError("invalid survey identifier or design code")
    return int(number)


def _prepare(
    demo_rows: Iterable[Mapping[str, Any]], diq_rows: Iterable[Mapping[str, Any]]
) -> tuple[tuple[int, int, float, bool, bool], ...]:
    responses: dict[int, int | None] = {}
    for row in diq_rows:
        if not isinstance(row, Mapping) or not {"SEQN", "DIQ010"}.issubset(row):
            raise NodeExportError("required survey fields missing")
        key = _key(row["SEQN"])
        if key in responses:
            raise NodeExportError("duplicate survey identifier")
        value = row["DIQ010"]
        code = (
            None
            if value is None or (type(value) is float and math.isnan(value))
            else int(_numeric(value, integer=True))
        )
        if code not in (None, 1, 2, 3, 7, 9):
            raise NodeExportError("unsupported questionnaire response")
        responses[key] = code
    seen: set[int] = set()
    prepared = []
    design: dict[int, set[int]] = defaultdict(set)
    for row in demo_rows:
        required = {"SEQN", "RIDAGEYR", "WTINT2YR", "SDMVSTRA", "SDMVPSU"}
        if not isinstance(row, Mapping) or not required.issubset(row):
            raise NodeExportError("required survey fields missing")
        key = _key(row["SEQN"])
        if key in seen:
            raise NodeExportError("duplicate survey identifier")
        seen.add(key)
        age_value = row["RIDAGEYR"]
        age = (
            None
            if age_value is None or (type(age_value) is float and math.isnan(age_value))
            else _numeric(age_value)
        )
        weight = _numeric(row["WTINT2YR"])
        stratum, psu = _key(row["SDMVSTRA"]), _key(row["SDMVPSU"])
        if (
            (age is not None and (not 0 <= age <= 80 or (age >= 1 and not age.is_integer())))
            or weight < 0
            or psu not in (1, 2)
        ):
            raise NodeExportError("invalid survey age, weight or design")
        if age is not None and age >= 1 and key not in responses:
            raise NodeExportError("missing eligible questionnaire join")
        if age is not None and age < 1 and key in responses:
            raise NodeExportError("ineligible questionnaire join")
        code = responses.get(key)
        if weight > 0:
            design[stratum].add(psu)
            prepared.append(
                (
                    stratum,
                    psu,
                    weight,
                    age is not None and age >= 20 and code in (1, 2, 3),
                    code == 1,
                )
            )
    if set(responses) - seen:
        raise NodeExportError("questionnaire key absent from demographics")
    if not prepared or any(psus != {1, 2} for psus in design.values()):
        raise NodeExportError("empty or incomplete positive-weight survey design")
    return tuple(prepared)


def _estimate(records: tuple[tuple[int, int, float, bool, bool], ...]) -> tuple[float, float]:
    # Common scaling preserves the ratio and its variance while avoiding weight overflow.
    scale = max(row[2] for row in records)
    weighted = [(h, j, w / scale, domain, case) for h, j, w, domain, case in records]
    if any(w == 0 for _, _, w, _, _ in weighted):
        raise NodeExportError("survey weight dynamic range is unsupported")
    denominator = math.fsum(w for _, _, w, domain, _ in weighted if domain)
    if denominator <= 0:
        raise NodeExportError("empty survey analysis domain")
    ratio = math.fsum(w for _, _, w, domain, case in weighted if domain and case) / denominator
    psus: dict[tuple[int, int], list[float]] = defaultdict(list)
    for h, j, weight, domain, case in weighted:
        psus[h, j].append(weight * (int(case) - ratio) / denominator if domain else 0.0)
    totals = {key: math.fsum(values) for key, values in psus.items()}
    # With two PSUs per stratum, n/(n-1) sum(centered totals squared) = difference squared.
    variance = math.fsum((totals[h, 1] - totals[h, 2]) ** 2 for h, j in totals if j == 1)
    if not math.isfinite(variance):
        raise NodeExportError("nonfinite survey variance")
    return ratio, math.sqrt(variance)


def run_public_survey(
    demo_rows: Iterable[Mapping[str, Any]],
    diq_rows: Iterable[Mapping[str, Any]],
    *,
    demo_sha256: str,
    diq_sha256: str,
    store: DurableNodePolicyStore,
    policy_id: str,
    policy_sha256: str,
    recorded_at: str,
) -> dict[str, Any]:
    """Return only an allowlisted adult ratio/SE or whole-estimate suppression.

    Caller verifies pinned source bytes before decoding. Digests here are assertions,
    not source authentication. Validation precedes reservation; statistics follow it.
    The fixed query identity cannot be changed to obtain a subgroup or retry.
    """
    if any(
        type(d) is not str or re.fullmatch(r"[0-9a-f]{64}", d) is None
        for d in (demo_sha256, diq_sha256, policy_sha256)
    ):
        raise NodeExportError("fingerprint must be a SHA-256 digest")
    records = _prepare(demo_rows, diq_rows)
    identity = "public-nhanes-adult-questionnaire-ratio-v1"
    reservation = store.reserve_query(
        {"analysis_id": identity, "dimensions": ["group"], "measure": "count"},
        overlap_group=identity,
        policy_id=policy_id,
        expected_policy_content_sha256=policy_sha256,
        recorded_at=recorded_at,
    )
    if reservation.policy.export_mode != "aggregate_only" or "group" not in (
        reservation.policy.allowed_dimension_fields
    ):
        raise NodeExportError("survey requires aggregate-only group policy")
    cases = sum(domain and case for _, _, _, domain, case in records)
    noncases = sum(domain and not case for _, _, _, domain, case in records)
    released = min(cases, noncases) >= reservation.policy.minimum_cell_count
    ratio, standard_error = _estimate(records) if released else (None, None)
    result: dict[str, Any] = {
        "schema_version": "0.1.0",
        "scope": "experimental_survey_weighted_self_report",
        "dataset": "nhanes_2021_2023",
        "estimand": "adult_20plus_valid_response_diagnosed_diabetes_ratio",
        "weight": "WTINT2YR",
        "variance_method": "taylor_stratified_psu_domain_with_replacement",
        "status": "eligible_for_local_export" if released else "suppressed",
        "case_definition": "DIQ010_1",
        "denominator_codes": [1, 2, 3],
        "borderline_handling": "noncase",
        "excluded_response_codes": [7, 9, "missing"],
        "age_handling": "known_age_at_least_20_no_imputation",
        "pregnancy_exception": "question_excludes_pregnancy_only_diabetes_for_women_20plus",
        "proxy_responses": "possible",
        "standardization": "crude_not_age_standardized",
        "nonresponse_limitation": "complete_response_bias_not_adjusted",
        "software_agreement": "unverified",
        "population_release_approved": False,
        "estimate": ratio,
        "standard_error": standard_error,
        "confidence_interval": None,
        "reliability_assessment": "not_completed",
        "clinical_validation": False,
        "custodian_deployment": False,
        "demo_sha256": demo_sha256,
        "diq_sha256": diq_sha256,
        "policy_sha256": reservation.policy_content_sha256,
        "query_sha256": reservation.receipt.query_fingerprint,
        "receipt_chain_sha256": reservation.receipt.chain_sha256,
        "receipt_sequence": reservation.receipt.sequence,
    }
    result["output_sha256"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return result
