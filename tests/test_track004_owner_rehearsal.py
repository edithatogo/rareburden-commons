import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs/track-004-owner-operated-rehearsal-2026-09-05.json"


def test_owner_rehearsal_is_exact_candidate_bound_and_non_authorizing() -> None:
    receipt = json.loads(RECEIPT.read_bytes())
    assert len(receipt["candidate"]["commit"]) == 40
    assert len(receipt["candidate"]["tree"]) == 40
    assert receipt["operator_mode"] == "owner_operated"
    assert receipt["scope"] == "synthetic_offline_only"
    assert receipt["result"]["exit_status"] == 0
    assert receipt["result"]["installed_result"]["rows"] == 1
    assert receipt["result"]["network_disabled"] is True
    for field in (
        "independent_operation",
        "custodian_approval",
        "production_signing",
        "release_authorization",
    ):
        assert receipt["claims"][field] is False


def test_owner_rehearsal_records_artifact_hashes() -> None:
    receipt = json.loads(RECEIPT.read_bytes())
    artifacts = receipt["result"]["artifact_sha256"]
    assert artifacts
    assert all(len(digest) == 64 for digest in artifacts.values())
