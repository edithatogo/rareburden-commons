#!/usr/bin/env python3
"""Validate the exact-candidate owner bounded-disposition receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class OwnerDispositionError(ValueError):
    """Raised when the owner receipt loses identity or exceeds its authority."""


def validate_owner_disposition(receipt: dict[str, Any]) -> dict[str, Any]:
    candidate = receipt.get("candidate_commit", "")
    if len(candidate) != 40 or any(char not in "0123456789abcdef" for char in candidate):
        raise OwnerDispositionError("candidate commit must be exact")
    if receipt.get("decision") != "bounded_synthetic_public_preview":
        raise OwnerDispositionError("owner decision must remain bounded")
    if receipt.get("stable_release_disposition") != "deferred":
        raise OwnerDispositionError("stable release must remain deferred")
    remote = receipt.get("github_receipt", {})
    expected_remote = {
        "repository": "edithatogo/rareburden-commons",
        "issue": 16,
        "comment_id": 5303792002,
        "url": "https://github.com/edithatogo/rareburden-commons/issues/16#issuecomment-5303792002",
        "author": "edithatogo",
        "author_association": "OWNER",
    }
    if any(remote.get(key) != value for key, value in expected_remote.items()):
        raise OwnerDispositionError("GitHub owner receipt identity mismatch")
    if remote.get("created_at") != remote.get("updated_at"):
        raise OwnerDispositionError("GitHub receipt must remain unedited as observed")
    digest = remote.get("observed_body_sha256", "")
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise OwnerDispositionError("observed receipt body hash must be exact")
    if len(receipt.get("binding_exclusions", [])) < 10:
        raise OwnerDispositionError("all bounded-preview exclusions must remain explicit")
    if len(receipt.get("stop_triggers", [])) != 8:
        raise OwnerDispositionError("all stop triggers must remain explicit")
    unsafe = sorted(key for key, value in receipt.get("claims", {}).items() if value is not False)
    if unsafe:
        raise OwnerDispositionError("stable and unavailable-authority claims must remain false")
    return {
        "candidate_commit": candidate,
        "decision": "bounded_synthetic_public_preview",
        "stable_release": "deferred",
        "github_comment_id": remote["comment_id"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.receipt.read_text(encoding="utf-8"))
    print(json.dumps(validate_owner_disposition(payload), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
