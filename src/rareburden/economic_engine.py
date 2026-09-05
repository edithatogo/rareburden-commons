"""Reference methods, data contracts and valuation engine for economic and social burden."""

from __future__ import annotations

import math
from typing import Any


class EconomicEngineError(ValueError):
    """Raised when an economic contract, valuation rule or perspective check is violated."""


def adjust_price_year(
    amount: float,
    from_year: int,
    to_year: int,
    deflator_annual_rate: float,
    *,
    rate_provenance: str,
) -> dict[str, Any]:
    """Adjust a monetary amount between price years using an explicit deflator rate.

    Does not select inflation or deflator rates silently.
    """
    if not isinstance(from_year, int) or not isinstance(to_year, int):
        raise EconomicEngineError("price years must be integers")
    if from_year < 1900 or to_year < 1900:
        raise EconomicEngineError("price years must be valid calendar years >= 1900")
    if deflator_annual_rate < -0.5 or deflator_annual_rate > 1.0:
        raise EconomicEngineError("deflator rate must be within plausible bounds [-0.5, 1.0]")
    if not rate_provenance or not rate_provenance.strip():
        raise EconomicEngineError("rate provenance must be explicitly declared")

    periods = to_year - from_year
    factor = (1.0 + deflator_annual_rate) ** periods
    adjusted_amount = amount * factor

    return {
        "original_amount": amount,
        "from_year": from_year,
        "to_year": to_year,
        "deflator_annual_rate": deflator_annual_rate,
        "adjustment_factor": round(factor, 6),
        "adjusted_amount": round(adjusted_amount, 2),
        "rate_provenance": rate_provenance.strip(),
    }


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    conversion_factor: float,
    *,
    factor_type: str,
    rate_provenance: str,
) -> dict[str, Any]:
    """Convert monetary values using an explicit caller-supplied exchange rate or PPP factor.

    Does not fetch market rates or assume purchasing-power parity silently.
    """
    if not from_currency or len(from_currency) != 3 or not from_currency.isupper():
        raise EconomicEngineError(f"invalid from_currency ISO code: {from_currency}")
    if not to_currency or len(to_currency) != 3 or not to_currency.isupper():
        raise EconomicEngineError(f"invalid to_currency ISO code: {to_currency}")
    if conversion_factor <= 0 or math.isnan(conversion_factor) or math.isinf(conversion_factor):
        raise EconomicEngineError(
            f"conversion factor must be positive finite number, got {conversion_factor}"
        )
    if factor_type not in {
        "market_exchange_rate",
        "purchasing_power_parity",
        "identity_same_currency",
    }:
        raise EconomicEngineError(f"unsupported factor_type: {factor_type}")
    if not rate_provenance or not rate_provenance.strip():
        raise EconomicEngineError("rate provenance must be explicitly declared")

    if from_currency == to_currency:
        converted_amount = amount
        factor = 1.0
    else:
        converted_amount = amount * conversion_factor
        factor = conversion_factor

    return {
        "original_amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "conversion_factor": factor,
        "factor_type": factor_type,
        "converted_amount": round(converted_amount, 2),
        "rate_provenance": rate_provenance.strip(),
    }


def discount_monetary_value(
    amount: float,
    discount_rate: float,
    periods: float | int,
    convention: str = "end_of_period",
) -> dict[str, Any]:
    """Discount future monetary flows with explicit discount rate and timing convention."""
    if discount_rate < 0 or discount_rate > 0.3:
        raise EconomicEngineError("discount rate must be between 0.0 and 0.3 (0% to 30%)")
    if periods < 0:
        raise EconomicEngineError("discounting periods cannot be negative")

    if convention == "undiscounted" or discount_rate == 0.0 or periods == 0:
        discount_factor = 1.0
    elif convention == "end_of_period":
        discount_factor = 1.0 / ((1.0 + discount_rate) ** float(periods))
    elif convention == "beginning_of_period":
        effective_periods = max(0.0, float(periods) - 1.0)
        discount_factor = 1.0 / ((1.0 + discount_rate) ** effective_periods)
    elif convention == "continuous":
        discount_factor = math.exp(-discount_rate * float(periods))
    else:
        raise EconomicEngineError(f"unknown discounting convention: {convention}")

    present_value = amount * discount_factor
    return {
        "nominal_amount": amount,
        "discount_rate": discount_rate,
        "periods": periods,
        "convention": convention,
        "discount_factor": round(discount_factor, 6),
        "present_value": round(present_value, 2),
    }


def calculate_perspective_burden(
    parameters: list[dict[str, Any]],
    perspective: str,
    *,
    societal_boundary: str = "national",
) -> dict[str, Any]:
    """Calculate economic burden by perspective, strictly enforcing boundaries and valuation rules.

    Perspectives:
    - 'health_system': Net direct formal medical and social care expenditure.
    - 'household': Out-of-pocket spending + valued caregiver time - cash transfers received.
    - 'societal': Total real resource costs (direct medical + direct non-medical + formal care +
      caregiver time + productivity losses). Internal transfers are excluded from societal
      resource consumption to prevent double-counting.
    """
    if perspective not in {"health_system", "household", "societal"}:
        raise EconomicEngineError(
            f"unsupported perspective '{perspective}'; "
            "must be health_system, household, or societal"
        )

    if not parameters:
        return {
            "perspective": perspective,
            "total_monetary_burden": 0.0,
            "currency": None,
            "price_year": None,
            "components": [],
            "transfers": [],
            "nonmonetary_resources": {},
            "blocked_overlap_components": [],
            "missing_data_components": [],
        }

    currencies = set()
    price_years = set()
    components_detail = []
    transfers = []
    nonmonetary_resources: dict[str, float] = {}
    blocked_overlap = []
    missing_data = []

    total_monetary = 0.0

    for param in parameters:
        param_id = param.get("parameter_id", "unnamed")
        category = param.get("category")
        quantity = param.get("quantity", {})
        valuation = param.get("valuation", {})
        overlap = param.get("overlap", {})
        missingness = param.get("missingness", {})
        param_perspective = param.get("perspective")

        meas_status = quantity.get("measurement_status")
        if meas_status in {"missing", "not_collected", "unassessed"}:
            missing_data.append(
                {
                    "parameter_id": param_id,
                    "category": category,
                    "status": meas_status,
                    "rationale": missingness.get("rationale", "missing value"),
                }
            )
            continue

        kind = quantity.get("kind")
        q_val = quantity.get("value", 0.0)
        q_unit = quantity.get("unit", "units")

        if kind in {"resource_count", "time_hours", "participation_days", "other_nonmonetary"}:
            nonmonetary_resources[f"{category}:{q_unit}"] = nonmonetary_resources.get(
                f"{category}:{q_unit}", 0.0
            ) + float(q_val)

        ov_status = overlap.get("assessment_status")
        if ov_status in {"possible_overlap", "unassessed"}:
            blocked_overlap.append(
                {
                    "parameter_id": param_id,
                    "category": category,
                    "overlap_status": ov_status,
                    "rationale": overlap.get("rationale", "overlap unassessed"),
                }
            )
            continue

        val_status = valuation.get("status")
        if val_status == "unvalued":
            components_detail.append(
                {
                    "parameter_id": param_id,
                    "category": category,
                    "monetary_value": None,
                    "valuation_status": "unvalued_resource_visible",
                    "quantity": q_val,
                    "unit": q_unit,
                }
            )
            continue
        elif val_status != "valued":
            continue

        curr = valuation.get("currency")
        pyr = valuation.get("price_year")
        if curr:
            currencies.add(curr)
        if pyr:
            price_years.add(pyr)

        if len(currencies) > 1:
            raise EconomicEngineError(
                f"cannot mix multiple currencies silently: {sorted(currencies)}"
            )
        if len(price_years) > 1:
            raise EconomicEngineError(
                f"cannot mix multiple price years silently: {sorted(price_years)}"
            )

        amount = float(valuation.get("total_monetary_value", 0.0))
        is_transfer = bool(valuation.get("is_transfer", False))

        if is_transfer:
            roles = param.get("roles", {})
            payer = roles.get("payer", {}).get("entity_label", "unknown_payer")
            recipient = roles.get("recipient", {}).get("entity_label", "unknown_recipient")
            transfers.append(
                {
                    "parameter_id": param_id,
                    "amount": amount,
                    "payer": payer,
                    "recipient": recipient,
                    "category": category,
                }
            )
            if perspective == "health_system":
                if param_perspective == "health_system":
                    total_monetary += amount
            elif perspective == "household":
                if param_perspective == "household":
                    total_monetary -= amount
            elif perspective == "societal":
                pass
            continue

        eligible_for_perspective = False
        if perspective == "health_system":
            if param_perspective == "health_system" or category in {
                "direct_medical",
                "formal_social_care",
            }:
                eligible_for_perspective = True
        elif perspective == "household":
            if param_perspective == "household" or category in {
                "direct_non_medical",
                "caregiver_time",
            }:
                eligible_for_perspective = True
        elif perspective == "societal":
            eligible_for_perspective = True

        if eligible_for_perspective:
            total_monetary += amount
            components_detail.append(
                {
                    "parameter_id": param_id,
                    "category": category,
                    "monetary_value": amount,
                    "valuation_status": "included",
                    "quantity": q_val,
                    "unit": q_unit,
                }
            )

    active_currency = next(iter(currencies)) if currencies else None
    active_price_year = next(iter(price_years)) if price_years else None

    return {
        "perspective": perspective,
        "societal_boundary": societal_boundary,
        "total_monetary_burden": round(total_monetary, 2),
        "currency": active_currency,
        "price_year": active_price_year,
        "components": components_detail,
        "transfers": transfers,
        "nonmonetary_resources": {k: round(v, 2) for k, v in nonmonetary_resources.items()},
        "blocked_overlap_components": blocked_overlap,
        "missing_data_components": missing_data,
    }


def evaluate_economic_scenarios(
    parameters: list[dict[str, Any]],
    perspective: str,
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate named sensitivity scenarios against baseline economic parameters."""
    base_result = calculate_perspective_burden(parameters, perspective)
    base_total = base_result["total_monetary_burden"]

    evaluations = []
    for sc in scenarios:
        sc_id = sc.get("scenario_id", "unnamed_scenario")
        title = sc.get("title", sc_id)
        multiplier = float(sc.get("cost_multiplier", 1.0))
        discount_adj = float(sc.get("discount_adjustment_rate", 0.0))

        adjusted_params = []
        for p in parameters:
            p_copy = {**p, "valuation": {**p.get("valuation", {})}}
            val = p_copy["valuation"]
            if val.get("status") == "valued":
                orig_val = float(val.get("total_monetary_value", 0.0))
                new_val = orig_val * multiplier
                if discount_adj > 0:
                    disc = discount_monetary_value(new_val, discount_adj, 1)
                    new_val = disc["present_value"]
                val["total_monetary_value"] = new_val
            adjusted_params.append(p_copy)

        sc_result = calculate_perspective_burden(adjusted_params, perspective)
        sc_total = sc_result["total_monetary_burden"]
        diff = sc_total - base_total
        pct = (diff / base_total * 100.0) if base_total != 0.0 else 0.0

        evaluations.append(
            {
                "scenario_id": sc_id,
                "title": title,
                "multiplier": multiplier,
                "discount_adjustment_rate": discount_adj,
                "monetary_total": round(sc_total, 2),
                "difference_from_base": round(diff, 2),
                "percentage_change": round(pct, 2),
            }
        )

    return {
        "perspective": perspective,
        "base_monetary_total": base_total,
        "currency": base_result["currency"],
        "price_year": base_result["price_year"],
        "scenarios": evaluations,
    }


def propagate_economic_uncertainty(
    component_distributions: list[dict[str, Any]],
    iterations: int = 1000,
    seed: int = 20260905,
) -> dict[str, Any]:
    """Seeded Monte Carlo uncertainty propagation across stochastic economic components."""
    if iterations < 10 or iterations > 100_000:
        raise EconomicEngineError("iterations must be between 10 and 100000")

    # Simple linear congruential generator for deterministic platform-independent PRNG
    state = seed & 0xFFFFFFFF

    def prng() -> float:
        nonlocal state
        state = (state * 1664525 + 1013904223) & 0xFFFFFFFF
        return state / 4294967296.0

    totals = []
    for _ in range(iterations):
        sample_total = 0.0
        for comp in component_distributions:
            dist_type = comp.get("distribution", "fixed")
            if dist_type == "fixed":
                sample_total += float(comp.get("value", 0.0))
            elif dist_type == "uniform":
                low = float(comp["low"])
                high = float(comp["high"])
                val = low + (high - low) * prng()
                sample_total += val
            elif dist_type == "triangular":
                low = float(comp["low"])
                high = float(comp["high"])
                mode = float(comp.get("mode", (low + high) / 2.0))
                u = prng()
                fc = (mode - low) / (high - low)
                if u < fc:
                    val = low + math.sqrt(u * (high - low) * (mode - low))
                else:
                    val = high - math.sqrt((1.0 - u) * (high - low) * (high - mode))
                sample_total += val
            else:
                raise EconomicEngineError(f"unsupported distribution type: {dist_type}")
        totals.append(sample_total)

    totals.sort()
    n = len(totals)
    mean_val = sum(totals) / n
    variance = sum((x - mean_val) ** 2 for x in totals) / n
    std_dev = math.sqrt(variance)

    idx_025 = round(0.025 * n)
    idx_500 = round(0.500 * n)
    idx_975 = min(n - 1, round(0.975 * n))

    return {
        "iterations": iterations,
        "seed": seed,
        "mean": round(mean_val, 2),
        "std_dev": round(std_dev, 2),
        "median": round(totals[idx_500], 2),
        "ci_lower_95": round(totals[idx_025], 2),
        "ci_upper_95": round(totals[idx_975], 2),
        "min": round(totals[0], 2),
        "max": round(totals[-1], 2),
    }


def generate_distributional_equity_report(
    parameters: list[dict[str, Any]],
    subgroup_field: str = "payer",
) -> dict[str, Any]:
    """Generate distributional equity breakdown showing who bears burden and benefits."""
    allocations: dict[str, float] = {}
    total = 0.0

    for p in parameters:
        val = p.get("valuation", {})
        if val.get("status") != "valued":
            continue
        amt = float(val.get("total_monetary_value", 0.0))
        roles = p.get("roles", {})

        if subgroup_field == "payer":
            key = roles.get("payer", {}).get("entity_label", "unattributed_payer")
        elif subgroup_field == "bearer":
            key = roles.get("bearer", {}).get("entity_label", "unattributed_bearer")
        elif subgroup_field == "category":
            key = p.get("category", "unattributed_category")
        else:
            key = "general"

        allocations[key] = allocations.get(key, 0.0) + amt
        total += amt

    breakdown = [
        {
            "subgroup": k,
            "monetary_amount": round(v, 2),
            "percentage_of_total": round((v / total * 100.0) if total > 0 else 0.0, 2),
        }
        for k, v in sorted(allocations.items(), key=lambda x: -x[1])
    ]

    return {
        "subgroup_dimension": subgroup_field,
        "total_monetary_amount": round(total, 2),
        "breakdown": breakdown,
    }
