from __future__ import annotations

import pytest

from rareburden.economic_engine import (
    EconomicEngineError,
    adjust_price_year,
    calculate_perspective_burden,
    convert_currency,
    discount_monetary_value,
    evaluate_economic_scenarios,
    generate_distributional_equity_report,
    propagate_economic_uncertainty,
)


def test_adjust_price_year_calculates_compounded_adjustment() -> None:
    result = adjust_price_year(1000.0, 2020, 2024, 0.03, rate_provenance="AIHW deflator index 2024")
    assert result["original_amount"] == 1000.0
    assert result["from_year"] == 2020
    assert result["to_year"] == 2024
    assert result["adjustment_factor"] == pytest.approx(1.125509, rel=1e-5)
    assert result["adjusted_amount"] == pytest.approx(1125.51, rel=1e-3)
    assert result["rate_provenance"] == "AIHW deflator index 2024"


def test_adjust_price_year_rejects_invalid_inputs() -> None:
    with pytest.raises(EconomicEngineError, match="price years must be integers"):
        adjust_price_year(100.0, "2020", 2024, 0.03, rate_provenance="provenance")  # type: ignore[arg-type]
    with pytest.raises(EconomicEngineError, match="rate provenance must be explicitly declared"):
        adjust_price_year(100.0, 2020, 2024, 0.03, rate_provenance="")
    with pytest.raises(EconomicEngineError, match="deflator rate must be within plausible bounds"):
        adjust_price_year(100.0, 2020, 2024, 2.5, rate_provenance="test")


def test_convert_currency_converts_and_tracks_provenance() -> None:
    result = convert_currency(
        1000.0,
        "USD",
        "AUD",
        1.52,
        factor_type="market_exchange_rate",
        rate_provenance="RBA 2024-06-30 midpoint",
    )
    assert result["converted_amount"] == 1520.0
    assert result["factor_type"] == "market_exchange_rate"

    same = convert_currency(
        500.0,
        "AUD",
        "AUD",
        1.0,
        factor_type="identity_same_currency",
        rate_provenance="identity",
    )
    assert same["converted_amount"] == 500.0


def test_convert_currency_rejects_invalid_factors() -> None:
    with pytest.raises(EconomicEngineError, match="invalid from_currency"):
        convert_currency(
            100.0, "us", "AUD", 1.5, factor_type="market_exchange_rate", rate_provenance="test"
        )
    with pytest.raises(EconomicEngineError, match="conversion factor must be positive"):
        convert_currency(
            100.0, "USD", "AUD", -1.5, factor_type="market_exchange_rate", rate_provenance="test"
        )


def test_discount_monetary_value_supports_multiple_conventions() -> None:
    end = discount_monetary_value(1000.0, 0.05, 2, convention="end_of_period")
    assert end["present_value"] == pytest.approx(907.03, rel=1e-3)

    beg = discount_monetary_value(1000.0, 0.05, 2, convention="beginning_of_period")
    assert beg["present_value"] == pytest.approx(952.38, rel=1e-3)

    cont = discount_monetary_value(1000.0, 0.05, 2, convention="continuous")
    assert cont["present_value"] == pytest.approx(904.84, rel=1e-3)

    undisc = discount_monetary_value(1000.0, 0.05, 2, convention="undiscounted")
    assert undisc["present_value"] == 1000.0


def test_calculate_perspective_burden_enforces_boundaries_and_transfers() -> None:
    parameters = [
        {
            "parameter_id": "direct_medical_hospital",
            "category": "direct_medical",
            "perspective": "health_system",
            "quantity": {
                "kind": "resource_count",
                "unit": "admissions",
                "measurement_status": "explicit_value",
                "value": 10,
            },
            "valuation": {
                "status": "valued",
                "is_transfer": False,
                "currency": "AUD",
                "price_year": 2024,
                "total_monetary_value": 50000.0,
            },
            "overlap": {"assessment_status": "assessed_no_overlap"},
        },
        {
            "parameter_id": "disability_support_transfer",
            "category": "direct_non_medical",
            "perspective": "household",
            "roles": {
                "payer": {"status": "declared", "entity_label": "Department of Social Services"},
                "recipient": {"status": "declared", "entity_label": "Patient Household"},
            },
            "quantity": {
                "kind": "monetary_expenditure",
                "unit": "aud",
                "measurement_status": "explicit_value",
                "value": 12000.0,
            },
            "valuation": {
                "status": "valued",
                "is_transfer": True,
                "currency": "AUD",
                "price_year": 2024,
                "total_monetary_value": 12000.0,
            },
            "overlap": {"assessment_status": "assessed_no_overlap"},
        },
        {
            "parameter_id": "caregiver_hours",
            "category": "caregiver_time",
            "perspective": "household",
            "quantity": {
                "kind": "time_hours",
                "unit": "hours",
                "measurement_status": "explicit_value",
                "value": 500,
            },
            "valuation": {
                "status": "valued",
                "is_transfer": False,
                "currency": "AUD",
                "price_year": 2024,
                "total_monetary_value": 17500.0,
            },
            "overlap": {"assessment_status": "assessed_no_overlap"},
        },
    ]

    hs = calculate_perspective_burden(parameters, "health_system")
    assert hs["total_monetary_burden"] == 50000.0

    hh = calculate_perspective_burden(parameters, "household")
    # Household has 17500 caregiver time cost minus 12000 cash transfer credit = 5500
    assert hh["total_monetary_burden"] == 5500.0

    soc = calculate_perspective_burden(parameters, "societal")
    # Societal excludes intra-society transfer, so real resource cost = 50000 + 17500 = 67500
    assert soc["total_monetary_burden"] == 67500.0
    assert len(soc["transfers"]) == 1
    assert soc["transfers"][0]["amount"] == 12000.0


def test_calculate_perspective_burden_fails_closed_on_mixed_currencies() -> None:
    parameters = [
        {
            "parameter_id": "item1",
            "category": "direct_medical",
            "quantity": {"measurement_status": "explicit_value", "value": 1},
            "valuation": {
                "status": "valued",
                "currency": "AUD",
                "price_year": 2024,
                "total_monetary_value": 100.0,
            },
            "overlap": {"assessment_status": "assessed_no_overlap"},
        },
        {
            "parameter_id": "item2",
            "category": "direct_medical",
            "quantity": {"measurement_status": "explicit_value", "value": 1},
            "valuation": {
                "status": "valued",
                "currency": "USD",
                "price_year": 2024,
                "total_monetary_value": 100.0,
            },
            "overlap": {"assessment_status": "assessed_no_overlap"},
        },
    ]
    with pytest.raises(EconomicEngineError, match="cannot mix multiple currencies"):
        calculate_perspective_burden(parameters, "health_system")


def test_calculate_perspective_burden_blocks_overlap_and_tracks_missing() -> None:
    parameters = [
        {
            "parameter_id": "uncertain_overlap_item",
            "category": "formal_social_care",
            "quantity": {"measurement_status": "explicit_value", "value": 1},
            "valuation": {
                "status": "valued",
                "currency": "AUD",
                "price_year": 2024,
                "total_monetary_value": 5000.0,
            },
            "overlap": {
                "assessment_status": "possible_overlap",
                "rationale": "May duplicate clinic nursing",
            },
        },
        {
            "parameter_id": "uncollected_school_item",
            "category": "education_impact",
            "quantity": {"measurement_status": "not_collected"},
            "missingness": {"rationale": "School data not collected in survey"},
            "overlap": {"assessment_status": "not_applicable"},
        },
        {
            "parameter_id": "unvalued_item",
            "category": "social_participation",
            "quantity": {"measurement_status": "explicit_value", "value": 20, "unit": "days"},
            "valuation": {"status": "unvalued"},
            "overlap": {"assessment_status": "assessed_no_overlap"},
        },
    ]
    result = calculate_perspective_burden(parameters, "societal")
    assert result["total_monetary_burden"] == 0.0
    assert len(result["blocked_overlap_components"]) == 1
    assert result["blocked_overlap_components"][0]["parameter_id"] == "uncertain_overlap_item"
    assert len(result["missing_data_components"]) == 1
    assert result["missing_data_components"][0]["parameter_id"] == "uncollected_school_item"
    assert len(result["components"]) == 1
    assert result["components"][0]["valuation_status"] == "unvalued_resource_visible"


def test_evaluate_economic_scenarios() -> None:
    parameters = [
        {
            "parameter_id": "clinic_cost",
            "category": "direct_medical",
            "quantity": {"measurement_status": "explicit_value", "value": 1},
            "valuation": {
                "status": "valued",
                "currency": "AUD",
                "price_year": 2024,
                "total_monetary_value": 10000.0,
            },
            "overlap": {"assessment_status": "assessed_no_overlap"},
        }
    ]
    scenarios = [
        {"scenario_id": "high", "cost_multiplier": 1.25},
        {"scenario_id": "low", "cost_multiplier": 0.75},
    ]
    res = evaluate_economic_scenarios(parameters, "health_system", scenarios)
    assert res["base_monetary_total"] == 10000.0
    assert res["scenarios"][0]["monetary_total"] == 12500.0
    assert res["scenarios"][0]["percentage_change"] == 25.0
    assert res["scenarios"][1]["monetary_total"] == 7500.0
    assert res["scenarios"][1]["percentage_change"] == -25.0


def test_propagate_economic_uncertainty_is_deterministic() -> None:
    dists = [
        {"distribution": "fixed", "value": 1000.0},
        {"distribution": "uniform", "low": 200.0, "high": 400.0},
        {"distribution": "triangular", "low": 100.0, "high": 300.0, "mode": 200.0},
    ]
    r1 = propagate_economic_uncertainty(dists, iterations=200, seed=42)
    r2 = propagate_economic_uncertainty(dists, iterations=200, seed=42)
    assert r1["mean"] == r2["mean"]
    assert r1["median"] == r2["median"]
    assert r1["ci_lower_95"] < r1["median"] < r1["ci_upper_95"]


def test_generate_distributional_equity_report() -> None:
    params = [
        {
            "parameter_id": "p1",
            "category": "direct_medical",
            "roles": {"payer": {"entity_label": "Public System"}},
            "valuation": {"status": "valued", "total_monetary_value": 8000.0},
        },
        {
            "parameter_id": "p2",
            "category": "direct_medical",
            "roles": {"payer": {"entity_label": "Household OOP"}},
            "valuation": {"status": "valued", "total_monetary_value": 2000.0},
        },
    ]
    report = generate_distributional_equity_report(params, subgroup_field="payer")
    assert report["total_monetary_amount"] == 10000.0
    assert report["breakdown"][0]["subgroup"] == "Public System"
    assert report["breakdown"][0]["percentage_of_total"] == 80.0
    assert report["breakdown"][1]["subgroup"] == "Household OOP"
    assert report["breakdown"][1]["percentage_of_total"] == 20.0
