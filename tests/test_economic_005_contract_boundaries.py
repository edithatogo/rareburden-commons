from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from rareburden.ledger import LedgerError, validate_ledger
from rareburden.model import ModelError, run_analysis_spec
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
ECONOMIC = ROOT / "examples/ledger/economic-social-synthetic.yml"
SCHEMA = ROOT / "schemas/parameter-ledger.schema.json"


def _document() -> dict[str, Any]:
    return load_mapping(ECONOMIC)


def test_existing_cost_fixture_keeps_unresolved_economic_contract_explicit() -> None:
    document = _document()
    ledger = validate_ledger(document, load_mapping(SCHEMA))
    record = ledger.get("synthetic-health-system-cost")
    assert record["quantity_type"] == "cost"
    assert record["metric"] == "cost_per_person"
    assert record["unit"] == "SYN"
    assert record["evidence_status"] == "assumed"
    assert record["uncertainty_status"] == "not_quantified"
    assert record["source_release_ids"] == []
    assert record["transformation_ids"] == []
    assert "Synthetic" in record["assumption_rationale"]
    limitations = " ".join(record["limitations"])
    for term in ("Currency", "price year", "PPP", "discounting", "transfers", "unresolved"):
        assert term in limitations
    assert "Not an empirical cost estimate" in limitations
    # The fixture documents an unresolved contract; these are not implemented
    # schema fields or permission to combine monetary components.
    assert (
        not {
            "perspective",
            "price_year",
            "currency",
            "ppp",
            "discounting",
            "transfer_payments",
            "valuation",
            "missingness",
        }
        & record.keys()
    )


@pytest.mark.parametrize("field", ["unit", "price_year"])
def test_requested_economic_context_is_not_silently_assumed(field: str) -> None:
    document = _document()
    second = deepcopy(document["parameters"][0])
    second["parameter_id"] = "synthetic-second-cost"
    second["unit"] = "OTHER-SYN"
    document["parameters"].append(second)
    ledger = validate_ledger(document, load_mapping(SCHEMA))
    message = "incompatible parameter unit" if field == "unit" else "missing price_year"
    with pytest.raises(LedgerError, match=message):
        ledger.require_compatible_context(
            ["synthetic-health-system-cost", "synthetic-second-cost"], fields=(field,)
        )


@pytest.mark.parametrize(
    ("estimand", "message"),
    [
        ("expected_affected_population", "population multiplied by fraction"),
        ("rare_aetiology_cases", "case_count multiplied by fraction"),
    ],
)
def test_cost_fixture_cannot_enter_count_engine_before_sampling(
    monkeypatch: pytest.MonkeyPatch, estimand: str, message: str
) -> None:
    document = _document()
    cost = document["parameters"][0]
    foundation = load_mapping(ROOT / "examples/ledger/public-foundation-synthetic.yml")
    fraction = deepcopy(
        next(record for record in foundation["parameters"] if record["quantity_type"] == "fraction")
    )
    # Match only invented population/period contexts so the actual quantity
    # boundary, not an unrelated context mismatch, must reject the cost input.
    fraction["population"] = deepcopy(cost["population"])
    fraction["period"] = deepcopy(cost["period"])
    document["parameters"].append(fraction)
    ledger = validate_ledger(document, load_mapping(SCHEMA))
    specification = load_mapping(ROOT / "examples/analyses/expected-population-synthetic.yml")
    specification["estimand"] = estimand
    specification["left_parameter_id"] = cost["parameter_id"]
    specification["right_parameter_id"] = fraction["parameter_id"]

    def forbidden_sampling(*args: Any, **kwargs: Any) -> None:
        pytest.fail("invalid cost input reached numerical simulation")

    monkeypatch.setattr("rareburden.model.simulate_product", forbidden_sampling)
    with pytest.raises(ModelError, match=message):
        run_analysis_spec(specification, ledger)
