import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/node/track004-bounded-orchestration-20260901.json"


def test_bounded_orchestration_candidate_binds_every_candidate_file() -> None:
    manifest = json.loads(MANIFEST.read_bytes())
    assert manifest["candidate_commit"] == "928c8b2441f55faaeca8d110c2805a13822574c0"
    assert manifest["candidate_tree"] == "1be930148a0367da8630cc7f0076394c21ff3ab9"
    expected = {
        "conductor/tracks/004-federated-node-runner/plan.md",
        "conductor/tracks/004-federated-node-runner/review.md",
        "docs/decisions/2026-09-01-track-004-integration-options.yml",
        "docs/federated-node-004-offline-install-rehearsal.md",
        "docs/federated-node-004-operator-guide.md",
        "docs/track-004-node-review-packet.md",
        "src/rareburden/node_analysis.py",
        "src/rareburden/node_orchestration.py",
        "src/rareburden/node_policy_store.py",
        "src/rareburden/resources/repository/conductor/tracks/004-federated-node-runner/plan.md",
        "src/rareburden/resources/repository/conductor/tracks/004-federated-node-runner/review.md",
        "src/rareburden/resources/repository/docs/decisions/2026-09-01-track-004-integration-options.yml",
        "src/rareburden/resources/repository/docs/federated-node-004-offline-install-rehearsal.md",
        "src/rareburden/resources/repository/docs/federated-node-004-operator-guide.md",
        "src/rareburden/resources/repository/docs/track-004-node-review-packet.md",
        "src/rareburden/resources/repository/runtime-assets.json",
        "tests/test_node_orchestration.py",
        "tests/test_node_policy_store.py",
        "tests/test_track004_integration_options.py",
        "tests/test_track005_component_candidate.py",
    }
    assert set(manifest["files"]) == expected
    for relative, digest in manifest["files"].items():
        if relative == "src/rareburden/resources/repository/runtime-assets.json":
            continue
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_bounded_orchestration_candidate_keeps_external_gates_false() -> None:
    manifest = json.loads(MANIFEST.read_bytes())
    assert manifest["scope"] == "experimental_synthetic_only"
    assert manifest["option_selected"] is True
    assert manifest["integration_implemented"] is True
    for field in (
        "production_contract_approved",
        "authoritative_custodian_store",
        "controlled_data_activation",
        "independent_review",
        "track_complete",
        "release",
    ):
        assert manifest[field] is False
