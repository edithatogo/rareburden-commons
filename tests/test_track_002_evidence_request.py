from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_track_002_qualifying_evidence_requests_are_explicit_and_fail_closed() -> None:
    record = yaml.safe_load(
        (ROOT / "docs/track-002-qualifying-evidence-request.yml").read_text(encoding="utf-8")
    )
    assert record["status"] == "requests_prepared_pending_receipts"
    requests = record["requests"]
    assert {item["gate"] for item in requests} == {
        "scientific",
        "data_governance",
        "landscape_challenge",
        "independent_operator",
    }
    assert all(item["status"] == "pending" for item in requests)
    assert all(item["required_fields"] for item in requests)
