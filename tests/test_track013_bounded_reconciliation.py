import copy
import json
from pathlib import Path

import pytest

from scripts.check_track013_bounded_reconciliation import (
    ReconciliationError,
    validate_reconciliation,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/assurance/track-013-bounded-reconciliation-2026-08-16.json"


def _payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_bounded_reconciliation_closes_exact_synthetic_chain() -> None:
    result = validate_reconciliation(_payload(), ROOT)
    assert result == {
        "status": "bounded_synthetic_reconciliation_valid",
        "dependency_count": 5,
        "tracks": ["008", "009", "010", "011", "012"],
        "empirical_rows": 0,
        "pending_gate_count": 4,
    }


def test_reconciliation_rejects_hash_drift() -> None:
    payload = copy.deepcopy(_payload())
    payload["dependencies"][0]["sha256"] = "0" * 64
    with pytest.raises(ReconciliationError, match="hash mismatch"):
        validate_reconciliation(payload, ROOT)


def test_reconciliation_rejects_activation_or_empirical_claim() -> None:
    payload = copy.deepcopy(_payload())
    payload["dependencies"][2]["required_assertions"]["empirical_parameter_activation"] = True
    with pytest.raises(ReconciliationError, match="unsafe dependency assertion"):
        validate_reconciliation(payload, ROOT)
    payload = _payload()
    payload["claims"]["representativeness"] = True
    with pytest.raises(ReconciliationError, match="claims must remain false"):
        validate_reconciliation(payload, ROOT)


def test_reconciliation_cannot_drop_equity_or_owner_gate() -> None:
    payload = _payload()
    payload["pending_gates"].remove("subgroup_and_equity_interpretation")
    with pytest.raises(ReconciliationError, match="must remain pending"):
        validate_reconciliation(payload, ROOT)
