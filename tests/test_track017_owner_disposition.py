from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_track017_owner_disposition import (
    OwnerDispositionError,
    validate_owner_disposition,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "manifests/release/track-017-owner-bounded-disposition-2026-08-16.json"


def _payload() -> dict:
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_exact_owner_bounded_disposition_validates() -> None:
    result = validate_owner_disposition(_payload())
    assert result["candidate_commit"] == "ba92940572bd69e19d54447e59b8ba8f776e3d5b"
    assert result["stable_release"] == "deferred"
    assert result["github_comment_id"] == 5303792002


@pytest.mark.parametrize(
    "claim", ["stable_release_authorized", "production_activated", "v1_tag_created"]
)
def test_release_overclaims_fail_closed(claim: str) -> None:
    payload = _payload()
    payload["claims"][claim] = True
    with pytest.raises(OwnerDispositionError, match="claims must remain false"):
        validate_owner_disposition(payload)


def test_owner_receipt_identity_drift_fails_closed() -> None:
    payload = _payload()
    payload["github_receipt"]["comment_id"] = 1
    with pytest.raises(OwnerDispositionError, match="identity mismatch"):
        validate_owner_disposition(payload)


def test_edited_remote_receipt_fails_closed() -> None:
    payload = _payload()
    payload["github_receipt"]["updated_at"] = "2026-08-15T19:10:00Z"
    with pytest.raises(OwnerDispositionError, match="unedited"):
        validate_owner_disposition(payload)


def test_stable_release_cannot_be_promoted() -> None:
    payload = _payload()
    payload["stable_release_disposition"] = "release"
    with pytest.raises(OwnerDispositionError, match="must remain deferred"):
        validate_owner_disposition(payload)
