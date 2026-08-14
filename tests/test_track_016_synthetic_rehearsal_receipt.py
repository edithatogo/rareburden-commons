from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
RECEIPT = ROOT / "docs/track-016-synthetic-rehearsal-receipt-2026-08-05.yml"


def test_owner_operated_rehearsal_receipt_is_hash_bound_and_non_authorizing() -> None:
    receipt = yaml.safe_load(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["commit"] == "c8c1a7c4e04e754bc87389d7bfd1a1b7dadb6e0e"
    assert receipt["outcome"] == "qualified"
    assert receipt["production_authorized"] is False
    assert receipt["independence_basis"] == "owner_operated; not independent"
    assert len(receipt["input_hashes"]) == 3
    assert len(receipt["output_hashes"]) == 1
    assert receipt["stop_triggers_observed"] == []
    assert all("No " in finding for finding in receipt["residual_findings"])
