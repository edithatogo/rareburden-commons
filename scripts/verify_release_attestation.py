#!/usr/bin/env python3
"""Verify a GitHub keyless release attestation with the repository trust profile."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

PROFILE_KEYS = {
    "activation_state",
    "deny_self_hosted_runners",
    "oidc_issuer",
    "predicate_type",
    "repository",
    "schema_version",
    "signer_workflow",
    "source_ref_pattern",
    "trusted_root_refresh_policy",
}
EXPECTED_ACTIVATION_STATE = "repository_profile_approved_custodian_acceptance_pending"
MAX_INPUT_BYTES = 1_000_000_000


class AttestationVerificationError(ValueError):
    """Raised when attestation verification cannot be performed safely."""


def _regular_local_file(value: str | os.PathLike[str], *, label: str) -> Path:
    raw = os.fspath(value)
    if raw.lower().startswith(("http://", "https://", "file://")):
        raise AttestationVerificationError(f"{label} must be a local file")
    path = Path(value)
    if not path.exists() or path.is_symlink() or not path.is_file():
        raise AttestationVerificationError(f"{label} must be a regular, non-symlink file")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise AttestationVerificationError(f"{label} exceeds the size limit")
    return path


def load_profile(path_value: str | os.PathLike[str]) -> dict[str, Any]:
    """Load and fail closed on an incomplete or broadened verification profile."""
    path = _regular_local_file(path_value, label="profile")
    try:
        profile: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AttestationVerificationError("profile is not valid UTF-8 JSON") from exc
    if not isinstance(profile, dict) or set(profile) != PROFILE_KEYS:
        raise AttestationVerificationError("profile fields do not match the supported contract")
    exact = {
        "schema_version": "1.0.0",
        "oidc_issuer": "https://token.actions.githubusercontent.com",
        "predicate_type": "https://slsa.dev/provenance/v1",
        "deny_self_hosted_runners": True,
        "trusted_root_refresh_policy": "per_release",
        "activation_state": EXPECTED_ACTIVATION_STATE,
    }
    for field, expected in exact.items():
        if profile.get(field) != expected:
            raise AttestationVerificationError(f"profile has unsupported {field}")
    repository = profile.get("repository")
    workflow = profile.get("signer_workflow")
    if (
        not isinstance(repository, str)
        or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
        or not isinstance(workflow, str)
        or not workflow.startswith(f"{repository}/.github/workflows/")
        or not workflow.endswith((".yml", ".yaml"))
    ):
        raise AttestationVerificationError("profile repository/workflow identity is invalid")
    pattern = profile.get("source_ref_pattern")
    if not isinstance(pattern, str):
        raise AttestationVerificationError("profile source-ref pattern is invalid")
    try:
        re.compile(pattern)
    except re.error as exc:
        raise AttestationVerificationError("profile source-ref pattern is invalid") from exc
    return profile


def build_verify_command(
    artifact: Path,
    bundle: Path,
    trusted_root: Path,
    source_ref: str,
    profile: dict[str, Any],
    *,
    gh_executable: str = "gh",
) -> list[str]:
    """Build the identity-constrained GitHub CLI verification command."""
    if re.fullmatch(str(profile["source_ref_pattern"]), source_ref) is None:
        raise AttestationVerificationError("source ref is not an approved release tag ref")
    return [
        gh_executable,
        "attestation",
        "verify",
        str(artifact),
        "--repo",
        str(profile["repository"]),
        "--bundle",
        str(bundle),
        "--custom-trusted-root",
        str(trusted_root),
        "--signer-workflow",
        str(profile["signer_workflow"]),
        "--cert-oidc-issuer",
        str(profile["oidc_issuer"]),
        "--predicate-type",
        str(profile["predicate_type"]),
        "--source-ref",
        source_ref,
        "--deny-self-hosted-runners",
        "--format",
        "json",
    ]


def verify_release_attestation(
    artifact_value: str | os.PathLike[str],
    bundle_value: str | os.PathLike[str],
    trusted_root_value: str | os.PathLike[str],
    profile_value: str | os.PathLike[str],
    *,
    source_ref: str,
    output_value: str | os.PathLike[str] | None = None,
    gh_executable: str = "gh",
) -> dict[str, Any]:
    """Run offline cryptographic verification and return a bounded receipt."""
    artifact = _regular_local_file(artifact_value, label="artifact")
    bundle = _regular_local_file(bundle_value, label="attestation bundle")
    trusted_root = _regular_local_file(trusted_root_value, label="trusted root")
    profile_path = _regular_local_file(profile_value, label="profile")
    profile = load_profile(profile_path)
    executable = shutil.which(gh_executable)
    if executable is None:
        raise AttestationVerificationError("GitHub CLI executable is unavailable")
    command = build_verify_command(
        artifact,
        bundle,
        trusted_root,
        source_ref,
        profile,
        gh_executable=executable,
    )
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or "GitHub CLI rejected the attestation"
        raise AttestationVerificationError(f"attestation verification failed: {detail}")
    try:
        result: Any = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AttestationVerificationError(
            "GitHub CLI returned malformed verification JSON"
        ) from exc
    if not isinstance(result, list) or not result:
        raise AttestationVerificationError("GitHub CLI returned no verified attestations")
    receipt: dict[str, Any] = {
        "artifact": {
            "filename": artifact.name,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "size": artifact.stat().st_size,
        },
        "constraints": {
            "deny_self_hosted_runners": True,
            "oidc_issuer": profile["oidc_issuer"],
            "predicate_type": profile["predicate_type"],
            "repository": profile["repository"],
            "signer_workflow": profile["signer_workflow"],
            "source_ref": source_ref,
        },
        "schema_version": "1.0.0",
        "verification_result": result,
    }
    if output_value is not None:
        output = Path(output_value)
        inputs = {path.resolve() for path in (artifact, bundle, trusted_root, profile_path)}
        if output.exists() and (output.is_symlink() or not output.is_file()):
            raise AttestationVerificationError("receipt output must be a regular file path")
        if output.resolve() in inputs:
            raise AttestationVerificationError("receipt must not overwrite a verification input")
        output.parent.mkdir(parents=True, exist_ok=True)
        payload = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
        temporary_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=output.parent,
                prefix=f".{output.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary.write(payload)
                temporary_name = temporary.name
            Path(temporary_name).replace(output)
            temporary_name = None
        finally:
            if temporary_name is not None:
                Path(temporary_name).unlink(missing_ok=True)
    return receipt


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--trusted-root", type=Path, required=True)
    parser.add_argument(
        "--profile",
        type=Path,
        default=Path("examples/config/release-attestation-profile.json"),
    )
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        receipt = verify_release_attestation(
            args.artifact,
            args.bundle,
            args.trusted_root,
            args.profile,
            source_ref=args.source_ref,
            output_value=args.output,
        )
    except (AttestationVerificationError, OSError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"release attestation verification failed: {exc}\n")
    if args.output is None:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"Verified release attestation; receipt: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
