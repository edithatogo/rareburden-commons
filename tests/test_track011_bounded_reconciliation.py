import json
from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.demonstrators import DemonstratorError, reconcile_bronchiectasis_synthetic_profile
from rareburden.schema import load_mapping
from rareburden.semantics import load_hierarchy

ROOT = Path(__file__).resolve().parents[1]
PROFILE = load_mapping(ROOT / "examples/demonstrators/011-bounded-synthetic-profile.yml")
BINDINGS = load_mapping(ROOT / "docs/track-011-dependency-bindings-2026-08-16.yml")
HIERARCHY = load_hierarchy(
    ROOT / "examples/semantics/bronchiectasis-synthetic.yml",
    ROOT / "schemas/disease-hierarchy.schema.json",
)


def _run(profile=PROFILE, bindings=BINDINGS):
    return reconcile_bronchiectasis_synthetic_profile(
        profile, HIERARCHY, bindings, created_at="2026-08-16T00:00:00Z"
    )


def test_committed_receipt_preserves_structural_missingness_and_exact_bindings() -> None:
    result = _run()
    committed = json.loads(
        (
            ROOT / "manifests/demonstrators/track-011-bounded-synthetic-receipt-2026-08-16.json"
        ).read_text()
    )
    assert result == committed
    assert result["exclusive_composition"]["value"] == 700
    assert result["multi_aetiology_count"] == 80
    assert result["unknown_count"] == 150
    assert result["unaccounted_count"] == 70
    assert result["activation_state"] == "synthetic_only"
    assert result["empirical_activation"] is False
    assert result["clinical_interpretation"] is False
    assert result["contract_frozen"] is False


@pytest.mark.parametrize(
    "claim", ["empirical_activation", "clinical_interpretation", "contract_frozen"]
)
def test_activation_claims_fail_closed(claim: str) -> None:
    bindings = deepcopy(BINDINGS)
    bindings["claims"][claim] = True
    with pytest.raises(DemonstratorError, match="activation"):
        _run(bindings=bindings)


def test_missing_context_and_overallocated_composition_fail_closed() -> None:
    missing = deepcopy(PROFILE)
    missing["context"]["setting"] = ""
    with pytest.raises(DemonstratorError, match="explicit geography"):
        _run(missing)
    over = deepcopy(PROFILE)
    over["denominator"] = 900
    with pytest.raises(DemonstratorError, match="exceeds"):
        _run(over)


def test_multi_aetiology_is_not_silently_added_to_an_individual_cause() -> None:
    result = _run()
    inputs = result["exclusive_composition"]["inputs"]
    assert all(item["value"] != result["multi_aetiology_count"] for item in inputs)
    assert "multi_aetiology_count" not in {item["entity_id"] for item in inputs}
