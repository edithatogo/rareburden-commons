from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.burden_assurance import run_bounded_synthetic_analysis
from rareburden.ledger import load_ledger
from rareburden.model import ModelError
from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).resolve().parents[1]
LEDGER = load_ledger(
    ROOT / "examples/ledger/public-foundation-synthetic.yml",
    ROOT / "schemas/parameter-ledger.schema.json",
)
SPEC = load_mapping(ROOT / "examples/analyses/expected-population-synthetic.yml")
BINDINGS = load_mapping(ROOT / "manifests/ledger/track-009-source-release-bindings-2026-08-16.json")
DISPOSITION = load_mapping(
    ROOT / "docs/track-010-post-dependency-quality-disposition-2026-08-27.yml"
)


def test_exact_bounded_receipt_is_synthetic_and_dependency_bound() -> None:
    result = run_bounded_synthetic_analysis(
        SPEC, LEDGER, BINDINGS, DISPOSITION, created_at="2026-08-16T00:00:00Z"
    )
    validate_instance(
        result,
        load_mapping(ROOT / "schemas/analysis-result.schema.json"),
        label="bounded_synthetic_result",
    )
    assert result["intended_use"] == "synthetic_assurance"
    assert result["activation_state"] == "not_activated"
    assert "not an empirical" in result["interpretation"]


@pytest.mark.parametrize(
    "mutation,message",
    [
        (("spec", "intended_use", "primary_estimate"), "synthetic_assurance only"),
        (("claims", "v0_4_contract_frozen", True), "activation"),
        (("claims", "empirical_parameter_activation", True), "activation"),
    ],
)
def test_reconciliation_fails_closed_on_activation_or_freeze(mutation, message: str) -> None:
    spec = deepcopy(SPEC)
    bindings = deepcopy(BINDINGS)
    target, key, value = mutation
    if target == "spec":
        spec[key] = value
    elif target == "bindings":
        bindings[key] = value
    else:
        bindings["claims"][key] = value
    with pytest.raises(ModelError, match=message):
        run_bounded_synthetic_analysis(
            spec,
            LEDGER,
            bindings,
            DISPOSITION,
            created_at="2026-08-16T00:00:00Z",
        )
