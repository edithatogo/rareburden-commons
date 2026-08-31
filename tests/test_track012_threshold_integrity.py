from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from rareburden.demonstrators import DemonstratorError, reconcile_paediatric_synthetic_linkage
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/paediatric/linked-data-synthetic.yml"
BINDINGS = ROOT / "docs/track-012-dependency-bindings-2026-08-16.yml"
RECEIPT = ROOT / "manifests/demonstrators/track-012-bounded-synthetic-receipt-2026-08-16.json"


class UnreadableTables(dict[str, Any]):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "tables":
            pytest.fail("invalid disclosure threshold reached linked-table processing")
        return super().get(key, default)


@pytest.mark.parametrize(
    "threshold",
    [2.0, 2.5, float("nan"), float("inf"), -float("inf"), True, False, "2", None, [], {}, 1, 0, -1],
)
def test_invalid_threshold_fails_before_any_table_access(threshold: Any) -> None:
    fixture = UnreadableTables(status="synthetic_only")
    with pytest.raises(DemonstratorError, match="integer of at least two"):
        reconcile_paediatric_synthetic_linkage(
            fixture,
            load_mapping(BINDINGS),
            disclosure_threshold=threshold,
            created_at="2026-08-16T00:00:00Z",
        )


@pytest.mark.parametrize("threshold", [2, 3])
def test_valid_integer_threshold_keeps_existing_inclusive_suppression(threshold: int) -> None:
    fixture = deepcopy(load_mapping(FIXTURE))
    for person in fixture["tables"]["person"]:
        person["jurisdiction"] = "synthetic-au"
    result = reconcile_paediatric_synthetic_linkage(
        fixture,
        load_mapping(BINDINGS),
        disclosure_threshold=threshold,
        created_at="2026-08-16T00:00:00Z",
    )
    assert result["disclosure_threshold"] == threshold
    assert result["equity_breakdown"] == [
        {
            "jurisdiction": "synthetic-au",
            "count": 2 if threshold == 2 else None,
            "suppressed": threshold == 3,
        }
    ]
    assert result["controlled_data_activation"] is False
    assert result["contract_frozen"] is False


def test_original_threshold_two_reproduces_retained_receipt_without_file_writes() -> None:
    original = RECEIPT.read_bytes()
    retained = json.loads(original)
    assert retained["disclosure_threshold"] == 2
    result = reconcile_paediatric_synthetic_linkage(
        load_mapping(FIXTURE),
        load_mapping(BINDINGS),
        disclosure_threshold=2,
        created_at=retained["created_at"],
    )
    assert result == retained
    assert RECEIPT.read_bytes() == original
