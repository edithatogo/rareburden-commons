from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from scripts.verify_track_002_minimal_candidate import (
    _candidate_notice,
    _safe_scope,
    deterministic_package_digest,
)

ROOT = Path(__file__).parents[1]
SCOPE = ROOT / "docs/track-002-minimal-public-release-scope-2026-08-20.yml"
ATTEMPT = ROOT / "docs/track-002-minimal-candidate-verification-attempt-2026-08-20.json"


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
