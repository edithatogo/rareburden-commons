import json
from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.demonstrators import DemonstratorError, reconcile_paediatric_synthetic_linkage
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = load_mapping(ROOT / "examples/paediatric/linked-data-synthetic.yml")
BINDINGS = load_mapping(ROOT / "docs/track-012-dependency-bindings-2026-08-16.yml")


def _run(fixture=FIXTURE, bindings=BINDINGS, *, threshold=2):
    return reconcile_paediatric_synthetic_linkage(
        fixture,
        bindings,
        disclosure_threshold=threshold,
        created_at="2026-08-16T00:00:00Z",
    )


def test_receipt_deduplicates_people_and_keeps_missingness_explicit() -> None:
    result = _run()
    committed = json.loads(
        (
            ROOT / "manifests/demonstrators/track-012-bounded-synthetic-receipt-2026-08-16.json"
        ).read_text()
    )
    assert result == committed
    assert result["population"] == {
        "deduplicated_people": 2,
        "people_with_diagnosis": 2,
        "people_with_multiple_diagnoses": 1,
    }
    assert result["uncertainty"]["imputation_performed"] is False
    assert result["uncertainty"]["cost_missing_people"] == 1
    assert all(row["suppressed"] and row["count"] is None for row in result["equity_breakdown"])
    assert "person_id" not in json.dumps(result)


@pytest.mark.parametrize(
    "claim",
    [
        "controlled_data_activation",
        "clinical_interpretation",
        "policy_interpretation",
        "contract_frozen",
    ],
)
def test_activation_claims_fail_closed(claim: str) -> None:
    bindings = deepcopy(BINDINGS)
    bindings["claims"][claim] = True
    with pytest.raises(DemonstratorError, match="activation"):
        _run(bindings=bindings)


def test_referential_integrity_duplicates_and_disclosure_floor_fail_closed() -> None:
    unknown = deepcopy(FIXTURE)
    unknown["tables"]["admission"][0]["person_id"] = "missing"
    with pytest.raises(DemonstratorError, match="unknown person"):
        _run(unknown)
    duplicate = deepcopy(FIXTURE)
    duplicate["tables"]["person"].append(deepcopy(duplicate["tables"]["person"][0]))
    with pytest.raises(DemonstratorError, match="duplicate person"):
        _run(duplicate)
    with pytest.raises(DemonstratorError, match="at least two"):
        _run(threshold=1)
