#!/usr/bin/env python3
"""Validate the Track 004 owner-operated clean-environment rehearsal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RECEIPT = Path("docs/track-004-owner-operated-rehearsal-2026-09-05.json")
PLAN = Path("conductor/tracks/004-federated-node-runner/plan.md")


class RehearsalValidationError(ValueError):
    """The Track 004 owner rehearsal contract escaped scope."""


def _load_receipt(root: Path) -> dict[str, Any]:
    value = json.loads((root / RECEIPT).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RehearsalValidationError("owner rehearsal receipt is not a mapping")
    return value


def validate_rehearsal(root: Path) -> None:
    if not (root / RECEIPT).exists():
        raise RehearsalValidationError("owner rehearsal receipt missing")
    receipt = _load_receipt(root)

    candidate = receipt.get("candidate")
    if not isinstance(candidate, dict):
        raise RehearsalValidationError("candidate binding missing")
    commit = candidate.get("commit")
    tree = candidate.get("tree")
    if not isinstance(commit, str) or len(commit) != 40:
        raise RehearsalValidationError("candidate commit binding drift")
    if not isinstance(tree, str) or len(tree) != 40:
        raise RehearsalValidationError("candidate tree binding drift")

    if receipt.get("operator_mode") != "owner_operated":
        raise RehearsalValidationError("operator_mode drift")
    if receipt.get("scope") != "synthetic_offline_only":
        raise RehearsalValidationError("scope drift")

    result = receipt.get("result")
    if not isinstance(result, dict):
        raise RehearsalValidationError("result section missing")
    if result.get("exit_status") != 0:
        raise RehearsalValidationError("exit_status drift")
    if result.get("network_disabled") is not True:
        raise RehearsalValidationError("network_disabled drift")
    installed = result.get("installed_result", {})
    if not isinstance(installed, dict) or installed.get("rows") != 1:
        raise RehearsalValidationError("installed_result rows drift")
    artifacts = result.get("artifact_sha256", {})
    if not isinstance(artifacts, dict) or not artifacts:
        raise RehearsalValidationError("artifact_sha256 map missing")
    for digest in artifacts.values():
        if not isinstance(digest, str) or len(digest) != 64:
            raise RehearsalValidationError("artifact digest format drift")

    claims = receipt.get("claims")
    if not isinstance(claims, dict):
        raise RehearsalValidationError("claims section missing")
    expected_claims_false = (
        "independent_operation",
        "custodian_approval",
        "production_signing",
        "release_authorization",
    )
    for field in expected_claims_false:
        if claims.get(field) is not False:
            raise RehearsalValidationError(f"owner rehearsal must not claim {field}")

    plan_text = (root / PLAN).read_text(encoding="utf-8")
    if "[x] Complete a separately recorded owner-operated clean-environment" not in plan_text:
        raise RehearsalValidationError(
            "Track 004 plan does not record the owner-operated rehearsal item"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate_rehearsal(args.root.resolve())
    except (RehearsalValidationError, OSError, json.JSONDecodeError) as exc:
        print(f"Track 004 owner rehearsal failed: {exc}")
        return 1
    print(
        "Track 004 owner rehearsal contract verified; production, custodian, "
        "independent and release claims remain false."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
