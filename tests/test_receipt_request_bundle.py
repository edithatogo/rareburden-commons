from __future__ import annotations

from pathlib import Path

from rareburden.schema import load_document

ROOT = Path(__file__).parents[1]
BUNDLE = ROOT / "docs/qualifying-receipt-request-bundle-2026-08-03.yml"


def test_receipt_request_bundle_is_prepared_and_bound_to_candidate() -> None:
    bundle = load_document(BUNDLE)
    assert bundle["status"] == "prepared_not_sent"
    assert bundle["candidate"]["tag"] == "candidate-2026-08-03"
    assert bundle["candidate"]["manifest_id"] == "rel-b213c531a6b754940f80ab70"
    assert {request["gate"] for request in bundle["requests"]} == {
        "scientific",
        "patient_community",
        "custodian_data_governance",
        "independent_operator",
        "operational_owners",
        "release",
    }
