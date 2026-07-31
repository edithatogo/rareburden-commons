from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts.verify_release_attestation import (
    AttestationVerificationError,
    build_verify_command,
    load_profile,
    verify_release_attestation,
)

ROOT = Path(__file__).parents[1]
PROFILE = ROOT / "examples/config/release-attestation-profile.json"


def test_release_attestation_profile_matches_schema_and_pins_identity() -> None:
    schema = json.loads(
        (ROOT / "schemas/release-attestation-profile.schema.json").read_text(encoding="utf-8")
    )
    profile = load_profile(PROFILE)
    Draft202012Validator(schema).validate(profile)
    assert profile["repository"] == "edithatogo/rareburden-commons"
    assert profile["signer_workflow"].endswith("/.github/workflows/release.yml")
    assert profile["deny_self_hosted_runners"] is True


def test_build_verify_command_enforces_all_trust_constraints(tmp_path: Path) -> None:
    profile = load_profile(PROFILE)
    command = build_verify_command(
        tmp_path / "artifact.whl",
        tmp_path / "bundle.json",
        tmp_path / "trusted_root.jsonl",
        "refs/tags/v0.3.0-rc.2",
        profile,
        gh_executable="/usr/bin/gh",
    )
    assert command[:3] == ["/usr/bin/gh", "attestation", "verify"]
    for flag in (
        "--repo",
        "--bundle",
        "--custom-trusted-root",
        "--signer-workflow",
        "--cert-oidc-issuer",
        "--predicate-type",
        "--source-ref",
        "--deny-self-hosted-runners",
    ):
        assert flag in command


@pytest.mark.parametrize(
    "source_ref",
    ["refs/heads/main", "v0.3.0-rc.2", "refs/tags/not-a-version", "refs/tags/v1"],
)
def test_build_verify_command_rejects_non_release_refs(tmp_path: Path, source_ref: str) -> None:
    with pytest.raises(AttestationVerificationError, match="approved release tag"):
        build_verify_command(
            tmp_path / "artifact.whl",
            tmp_path / "bundle.json",
            tmp_path / "trusted_root.jsonl",
            source_ref,
            load_profile(PROFILE),
        )


def test_profile_rejects_weakened_runner_policy(tmp_path: Path) -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    profile["deny_self_hosted_runners"] = False
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(profile), encoding="utf-8")
    with pytest.raises(AttestationVerificationError, match="deny_self_hosted_runners"):
        load_profile(path)


def _inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    artifact = tmp_path / "artifact.whl"
    bundle = tmp_path / "bundle.json"
    trusted_root = tmp_path / "trusted_root.jsonl"
    artifact.write_bytes(b"artifact")
    bundle.write_text("{}\n", encoding="utf-8")
    trusted_root.write_text("{}\n", encoding="utf-8")
    return artifact, bundle, trusted_root


def test_verifier_writes_receipt_only_after_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact, bundle, trusted_root = _inputs(tmp_path)
    monkeypatch.setattr("scripts.verify_release_attestation.shutil.which", lambda _name: "/bin/gh")
    monkeypatch.setattr(
        "scripts.verify_release_attestation.subprocess.run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, '[{"verified": true}]', ""),
    )
    receipt_path = tmp_path / "receipt.json"
    receipt = verify_release_attestation(
        artifact,
        bundle,
        trusted_root,
        PROFILE,
        source_ref="refs/tags/v0.3.0-rc.2",
        output_value=receipt_path,
    )
    assert receipt["artifact"]["filename"] == artifact.name
    assert receipt["constraints"]["source_ref"] == "refs/tags/v0.3.0-rc.2"
    assert json.loads(receipt_path.read_text(encoding="utf-8")) == receipt


def test_verifier_fails_closed_on_tamper_or_wrong_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact, bundle, trusted_root = _inputs(tmp_path)
    monkeypatch.setattr("scripts.verify_release_attestation.shutil.which", lambda _name: "/bin/gh")
    monkeypatch.setattr(
        "scripts.verify_release_attestation.subprocess.run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 1, "", "signature mismatch"),
    )
    receipt_path = tmp_path / "receipt.json"
    with pytest.raises(AttestationVerificationError, match="signature mismatch"):
        verify_release_attestation(
            artifact,
            bundle,
            trusted_root,
            PROFILE,
            source_ref="refs/tags/v0.3.0-rc.2",
            output_value=receipt_path,
        )
    assert not receipt_path.exists()


def test_verifier_rejects_symlinked_trust_material(tmp_path: Path) -> None:
    artifact, bundle, trusted_root = _inputs(tmp_path)
    link = tmp_path / "root-link.jsonl"
    link.symlink_to(trusted_root)
    with pytest.raises(AttestationVerificationError, match="non-symlink"):
        verify_release_attestation(
            artifact,
            bundle,
            link,
            PROFILE,
            source_ref="refs/tags/v0.3.0-rc.2",
        )


def test_release_workflow_retains_bundles_roots_and_profile() -> None:
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "steps.attest_provenance.outputs.bundle-path" in workflow
    assert "steps.attest_sbom.outputs.bundle-path" in workflow
    assert "gh attestation trusted-root" in workflow
    assert "attestation-evidence/profile.json" in workflow
    assert "attestation-evidence/verify_release_attestation.py" in workflow
    assert "attestation-evidence/*" in workflow
