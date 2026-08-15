import json
from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.burden_assurance import run_bounded_synthetic_analysis
from rareburden.ledger import load_ledger
from rareburden.model import ModelError
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
LEDGER = load_ledger(
    ROOT / "examples/ledger/public-foundation-synthetic.yml",
    ROOT / "schemas/parameter-ledger.schema.json",
)
SPEC = load_mapping(ROOT / "examples/analyses/expected-population-synthetic.yml")
BINDINGS = load_mapping(ROOT / "manifests/ledger/track-009-source-release-bindings-2026-08-16.json")
DISPOSITION = load_mapping(ROOT / "docs/track-010-bounded-quality-disposition-2026-08-16.yml")


def test_exact_bounded_receipt_is_synthetic_and_dependency_bound() -> None:
    result = run_bounded_synthetic_analysis(
        SPEC, LEDGER, BINDINGS, DISPOSITION, created_at="2026-08-16T00:00:00Z"
    )
    committed = json.loads(
        (ROOT / "manifests/burden/track-010-bounded-synthetic-receipt-2026-08-16.json").read_text()
    )
    assert result == committed
    assert result["activation_state"] == "synthetic_only"
    assert result["contract_frozen"] is False
    assert result["empirical_parameter_activation"] is False
    assert len(result["source_release_binding_sha256"]) == 64


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
