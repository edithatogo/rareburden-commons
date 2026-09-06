from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from scripts.check_track004_owner_rehearsal import (
    RECEIPT,
    RehearsalValidationError,
    validate_rehearsal,
)

ROOT = Path(__file__).parents[1]


def _copy_rehearsal_inputs(destination: Path) -> None:
    target = destination / RECEIPT
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / RECEIPT, target)


def test_owner_rehearsal_contract_passes() -> None:
    validate_rehearsal(ROOT)


def test_owner_rehearsal_rejects_missing_receipt(tmp_path: Path) -> None:
    with pytest.raises(RehearsalValidationError, match="receipt missing"):
        validate_rehearsal(tmp_path)


def test_owner_rehearsal_rejects_independent_operation_claim(tmp_path: Path) -> None:
    _copy_rehearsal_inputs(tmp_path)
    receipt_path = tmp_path / RECEIPT
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["claims"]["independent_operation"] = True
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(
        RehearsalValidationError, match="must not claim independent_operation"
    ):
        validate_rehearsal(tmp_path)


def test_owner_rehearsal_rejects_custodian_approval_claim(tmp_path: Path) -> None:
    _copy_rehearsal_inputs(tmp_path)
    receipt_path = tmp_path / RECEIPT
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["claims"]["custodian_approval"] = True
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(
        RehearsalValidationError, match="must not claim custodian_approval"
    ):
        validate_rehearsal(tmp_path)


def test_owner_rehearsal_rejects_production_signing_claim(tmp_path: Path) -> None:
    _copy_rehearsal_inputs(tmp_path)
    receipt_path = tmp_path / RECEIPT
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["claims"]["production_signing"] = True
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(
        RehearsalValidationError, match="must not claim production_signing"
    ):
        validate_rehearsal(tmp_path)


def test_owner_rehearsal_rejects_release_authorization_claim(tmp_path: Path) -> None:
    _copy_rehearsal_inputs(tmp_path)
    receipt_path = tmp_path / RECEIPT
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["claims"]["release_authorization"] = True
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(
        RehearsalValidationError, match="must not claim release_authorization"
    ):
        validate_rehearsal(tmp_path)


def test_owner_rehearsal_rejects_scope_drift(tmp_path: Path) -> None:
    _copy_rehearsal_inputs(tmp_path)
    receipt_path = tmp_path / RECEIPT
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["scope"] = "production_authorizing"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(RehearsalValidationError, match="scope drift"):
        validate_rehearsal(tmp_path)


def test_owner_rehearsal_rejects_network_enabled(tmp_path: Path) -> None:
    _copy_rehearsal_inputs(tmp_path)
    receipt_path = tmp_path / RECEIPT
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["result"]["network_disabled"] = False
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(RehearsalValidationError, match="network_disabled drift"):
        validate_rehearsal(tmp_path)


def test_owner_rehearsal_rejects_commit_short(tmp_path: Path) -> None:
    _copy_rehearsal_inputs(tmp_path)
    receipt_path = tmp_path / RECEIPT
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["candidate"]["commit"] = "abc123"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(
        RehearsalValidationError, match="candidate commit binding drift"
    ):
        validate_rehearsal(tmp_path)