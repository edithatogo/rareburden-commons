from __future__ import annotations

from rareburden.demonstrator_economic import (
    evaluate_monogenic_diabetes_economic_reference,
)


def test_monogenic_diabetes_economic_reference_evaluates_consistently() -> None:
    result = evaluate_monogenic_diabetes_economic_reference(
        synthetic_case_count=8520.0,
        currency="AUD",
        price_year=2024,
    )
    assert result["intended_use"] == "synthetic_demonstrator_reference"
    assert result["synthetic_case_count"] == 8520.0

    hs = result["health_system_burden"]
    assert hs["perspective"] == "health_system"
    # 8520 * 2 * 250 (consults) + 8520 * 0.1 * 1200 (sequencing) = 4,260,000 + 1,022,400 = 5,282,400
    assert hs["total_monetary_burden"] == 5282400.0

    hh = result["household_burden"]
    assert hh["perspective"] == "household"
    # 8520 * 600 (OOP monitoring) + 8520 * 52 * 35 (caregiver hours)
    # = 5,112,000 + 15,506,400 = 20,618,400
    assert hh["total_monetary_burden"] == 20618400.0

    soc = result["societal_burden"]
    assert soc["perspective"] == "societal"
    # 5,282,400 + 20,618,400 = 25,900,800
    assert soc["total_monetary_burden"] == 25900800.0

    scenarios = result["scenario_sensitivity"]["scenarios"]
    assert len(scenarios) == 2
    assert scenarios[0]["scenario_id"] == "high_care_cost"
    assert scenarios[0]["percentage_change"] == 20.0
    assert scenarios[1]["scenario_id"] == "low_care_cost"
    assert scenarios[1]["percentage_change"] == -20.0
