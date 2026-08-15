#!/usr/bin/env python3
"""Validate Track 016 owner-operated evidence without upgrading independent claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


class OperationsEvidenceError(ValueError):
    """Raised when bounded operations evidence is incomplete or overclaims authority."""


_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def validate_bounded_operations(payload: dict[str, Any], root: Path) -> dict[str, Any]:
    if payload.get("scope") != "repository_owned_synthetic_public_candidate_operations":
        raise OperationsEvidenceError("operations scope must remain repository-owned and bounded")

    candidate = payload.get("candidate", {})
    commit = candidate.get("commit")
    tree = candidate.get("tree")
    if not isinstance(commit, str) or _HEX40.fullmatch(commit) is None:
        raise OperationsEvidenceError("candidate commit must be exact")
    if not isinstance(tree, str) or _HEX40.fullmatch(tree) is None:
        raise OperationsEvidenceError("candidate tree must be exact")
    try:
        observed_tree = _git(root, "show", "-s", "--format=%T", commit)
    except subprocess.CalledProcessError as exc:
        raise OperationsEvidenceError("candidate commit is unavailable") from exc
    if observed_tree != tree:
        raise OperationsEvidenceError("candidate commit/tree binding mismatch")

    seen: set[str] = set()
    for item in payload.get("evidence", []):
        relative = Path(str(item.get("path", "")))
        if relative.as_posix() in seen:
            raise OperationsEvidenceError(f"duplicate evidence path: {relative}")
        seen.add(relative.as_posix())
        if relative.is_absolute() or ".." in relative.parts:
            raise OperationsEvidenceError(f"unsafe evidence path: {relative}")
        digest = item.get("sha256")
        if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
            raise OperationsEvidenceError(f"invalid evidence digest: {relative}")
        path = root / relative
        if not path.is_file() or _sha256(path) != digest:
            raise OperationsEvidenceError(f"evidence hash mismatch: {relative}")

    model = payload.get("operator_model", {})
    if (
        model.get("primary") != "edithatogo"
        or model.get("single_developer_repository") is not True
        or model.get("independent_operator") is not False
        or model.get("independent_security") is not False
        or model.get("service_level_commitment") is not False
    ):
        raise OperationsEvidenceError("operator model overstates scope or independence")
    if model.get("backup_state") != "owner_attested_private_acceptance_handoff_incomplete":
        raise OperationsEvidenceError("backup limitation must remain explicit")

    claims = payload.get("claims", {})
    prohibited = {
        "production_authorized",
        "stable_release_authorized",
        "independent_operator_evidence",
        "independent_security_evidence",
        "backup_handoff_complete",
        "controlled_data_authorized",
    }
    unsafe = sorted(key for key in prohibited if claims.get(key) is not False)
    if unsafe:
        raise OperationsEvidenceError("bounded operations claims must remain false: " + ", ".join(unsafe))

    required_pending = {
        "exact_candidate_owner_operated_exercises",
        "backup_owner_handoff",
        "independent_operator",
        "independent_security",
        "release_authority",
        "production_operations",
    }
    if set(payload.get("pending_gates", [])) != required_pending:
        raise OperationsEvidenceError("all unresolved operations gates must remain pending")

    results = payload.get("exercise_results", {})
    allowed = {"pass", "qualified", "bounded_repository_policy", "pending_exact_candidate_execution"}
    if not results or any(value not in allowed for value in results.values()):
        raise OperationsEvidenceError("exercise results contain an unsupported disposition")
    return {
        "status": "bounded_operations_evidence_valid",
        "candidate_commit": commit,
        "evidence_count": len(seen),
        "pending_gate_count": len(required_pending),
        "independent_evidence": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path())
    args = parser.parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    print(json.dumps(validate_bounded_operations(payload, args.root.resolve()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
