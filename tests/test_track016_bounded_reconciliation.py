import copy
import json
from pathlib import Path

import pytest

from scripts.check_track016_bounded_operations import (
    OperationsEvidenceError,
    validate_bounded_operations,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/operations/track-016-bounded-operations-2026-08-16.json"


def _payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_bounded_operations_manifest_preserves_owner_and_independence_boundaries() -> None:
    result = validate_bounded_operations(_payload(), ROOT)
    assert result["status"] == "bounded_operations_evidence_valid"
    assert result["independent_evidence"] is False
    assert result["pending_gate_count"] == 6


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("production_authorized", True),
        ("stable_release_authorized", True),
        ("independent_operator_evidence", True),
        ("independent_security_evidence", True),
        ("backup_handoff_complete", True),
        ("controlled_data_authorized", True),
    ],
)
def test_bounded_operations_rejects_authority_upgrades(field: str, value: bool) -> None:
    payload = _payload()
    payload["claims"][field] = value
    with pytest.raises(OperationsEvidenceError, match="claims must remain false"):
        validate_bounded_operations(payload, ROOT)


def test_bounded_operations_rejects_hash_path_and_candidate_drift() -> None:
    payload = _payload()
    payload["evidence"][0]["sha256"] = "0" * 64
    with pytest.raises(OperationsEvidenceError, match="hash mismatch"):
        validate_bounded_operations(payload, ROOT)

    payload = _payload()
    payload["evidence"][0]["path"] = "../private-receipt"
    with pytest.raises(OperationsEvidenceError, match="unsafe evidence path"):
        validate_bounded_operations(payload, ROOT)

    payload = _payload()
    payload["candidate"]["tree"] = "0" * 40
    with pytest.raises(OperationsEvidenceError, match="commit/tree binding mismatch"):
        validate_bounded_operations(payload, ROOT)


def test_bounded_operations_rejects_duplicate_evidence_or_missing_gate() -> None:
    payload = _payload()
    payload["evidence"].append(copy.deepcopy(payload["evidence"][0]))
    with pytest.raises(OperationsEvidenceError, match="duplicate evidence path"):
        validate_bounded_operations(payload, ROOT)

    payload = _payload()
    payload["pending_gates"] = payload["pending_gates"][:-1]
    with pytest.raises(OperationsEvidenceError, match="must remain pending"):
        validate_bounded_operations(payload, ROOT)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("independent_operator", True),
        ("independent_security", True),
        ("service_level_commitment", True),
        ("backup_state", "complete"),
    ],
)
def test_bounded_operations_rejects_operator_model_overstatement(
    field: str, value: object
) -> None:
    payload = _payload()
    payload["operator_model"][field] = value
    with pytest.raises(OperationsEvidenceError, match="operator model|backup limitation"):
        validate_bounded_operations(payload, ROOT)
