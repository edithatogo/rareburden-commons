from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

import scripts.verify_track_002_minimal_candidate as verifier
from scripts.verify_track_002_minimal_candidate import (
    _candidate_notice,
    _safe_scope,
    _validate_content_range,
    deterministic_package_digest,
)

ROOT = Path(__file__).parents[1]
SCOPE = ROOT / "docs/track-002-minimal-public-release-scope-2026-08-20.yml"
ATTEMPT = ROOT / "docs/track-002-minimal-candidate-verification-attempt-2026-08-20.json"
VERIFICATION = ROOT / "docs/track-002-minimal-candidate-verification-2026-08-20.json"
RIGHTS_AUDIT = ROOT / "docs/track-002-minimal-candidate-rights-attribution-audit-2026-08-20.json"


def _scope() -> dict:
    return yaml.safe_load(SCOPE.read_text(encoding="utf-8"))


def test_scope_validation_accepts_only_the_exact_five_artifact_allowlist() -> None:
    assert len(_safe_scope(_scope())) == 5


def test_scope_validation_rejects_extra_source() -> None:
    scope = _scope()
    scope["candidate"]["sources"].append(
        {"source_id": "who-global-health-estimates", "artifacts": []}
    )
    with pytest.raises(ValueError, match="allowlist changed"):
        _safe_scope(scope)


def test_scope_validation_rejects_publication_or_unbounded_claims() -> None:
    scope = _scope()
    scope["authority"]["publication_authorized"] = True
    with pytest.raises(ValueError, match="must not authorize publication"):
        _safe_scope(scope)

    scope = _scope()
    scope["claims"]["clinical_validation"] = True
    with pytest.raises(ValueError, match="claims must remain false"):
        _safe_scope(scope)


def test_scope_validation_rejects_malformed_hash_and_query_url() -> None:
    scope = _scope()
    artifact = scope["candidate"]["sources"][0]["artifacts"][0]
    artifact["sha256"] = "z" * 64
    with pytest.raises(ValueError, match="exact size and SHA-256"):
        _safe_scope(scope)

    scope = _scope()
    artifact = scope["candidate"]["sources"][0]["artifacts"][0]
    artifact["source_url"] += "?token=must-not-persist"
    with pytest.raises(ValueError, match="credential-free and query-free"):
        _safe_scope(scope)


def test_package_digest_is_deterministic_and_bound_to_contents(tmp_path: Path) -> None:
    artifact = tmp_path / "raw/orphadata/2026-07/example.xml"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"exact source bytes")
    manifest = json.dumps({"sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}).encode()

    first = deterministic_package_digest(tmp_path, manifest, _candidate_notice())
    second = deterministic_package_digest(tmp_path, manifest, _candidate_notice())
    assert first == second

    artifact.write_bytes(b"changed source bytes")
    assert deterministic_package_digest(tmp_path, manifest, _candidate_notice()) != first


def test_notice_preserves_bounded_claims_and_attribution() -> None:
    notice = _candidate_notice().decode()
    assert "Orphadata Science / Orphanet" in notice
    assert "Mondo Disease Ontology, Monarch Initiative" in notice
    assert "CC BY 4.0" in notice
    assert "does not claim comprehensive coverage" in notice
    assert "clinical validation" in notice


def test_failed_live_attempt_keeps_every_dependent_gate_closed() -> None:
    attempt = json.loads(ATTEMPT.read_text(encoding="utf-8"))
    assert attempt["status"] == "blocked_transport_exact_candidate_not_built"
    assert set(attempt["gate_disposition"].values()) == {"pending"}
    assert attempt["authority"] == {
        "publication_authorized": False,
        "external_mutation_performed": False,
        "credential_used": False,
        "private_capture_performed": False,
        "source_bytes_retained": False,
    }


def test_cli_refuses_to_overwrite_receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    receipt = tmp_path / "receipt.json"
    receipt.write_text("preserve me\n", encoding="utf-8")
    monkeypatch.setattr(verifier, "verify", lambda _scope_path: {"status": "synthetic"})
    monkeypatch.setattr(
        "sys.argv",
        ["verify_track_002_minimal_candidate.py", "--receipt", str(receipt)],
    )
    with pytest.raises(ValueError, match="refusing to overwrite receipt"):
        verifier.main()
    assert receipt.read_text(encoding="utf-8") == "preserve me\n"


def test_mondo_range_response_must_bind_exact_offsets_and_total() -> None:
    _validate_content_range("bytes 0-15/32", start=0, end=15, total=32)
    with pytest.raises(ValueError, match="unexpected Content-Range"):
        _validate_content_range("bytes 0-15/31", start=0, end=15, total=32)
    with pytest.raises(ValueError, match="unexpected Content-Range"):
        _validate_content_range(None, start=0, end=15, total=32)


def test_success_receipt_is_exact_ephemeral_and_not_publication_authority() -> None:
    receipt = json.loads(VERIFICATION.read_text(encoding="utf-8"))
    assert receipt["status"] == "verified_ephemeral_candidate_not_published"
    assert len(receipt["artifacts"]) == 5
    assert receipt["package"] == {
        "bytes": 591841280,
        "format": "deterministic_pax_tar_stream",
        "retained": False,
        "sha256": "1a8e0a01467a56eee0a85f15f971b0dd03820abfa518cc981d6588a264c58cd1",
    }
    assert receipt["cleanup"] == {
        "source_bytes_retained": False,
        "temporary_directory_removed": True,
    }
    assert receipt["authority"]["publication_authorized"] is False


def test_rights_audit_is_exact_candidate_only_and_preserves_third_party_limits() -> None:
    audit = json.loads(RIGHTS_AUDIT.read_text(encoding="utf-8"))
    assert audit["status"] == ("passed_for_exact_unmodified_candidate_with_publisher_reliance")
    assert audit["candidate"]["package_sha256"] == (
        "1a8e0a01467a56eee0a85f15f971b0dd03820abfa518cc981d6588a264c58cd1"
    )
    assert audit["third_party_rights_disposition"]["prohibited_without_new_audit"]
    assert "WHO GHE" not in audit["excluded_sources_confirmed"]
    assert "who-global-health-estimates" in audit["excluded_sources_confirmed"]
    assert audit["authority"]["publication_authorized"] is False
