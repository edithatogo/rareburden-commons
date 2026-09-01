from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/ledger/track005-component-prototype-20260901.json"


def test_component_candidate_binds_every_changed_candidate_file() -> None:
    manifest = json.loads(MANIFEST.read_bytes())
    assert manifest["candidate_commit"] == "2cf64c8f49f1b4a2f752106d4c3c9ae6e7986e67"
    assert manifest["candidate_tree"] == "14873320d571e089ea603163988134ea6308e7d3"
    assert manifest["selected_proposal_commit"] == ("1ed8ed425120f31f6d812230e924de6f3ca7b25f")
    assert manifest["selected_option"] == "A"
    expected = {
        "conductor/tracks/005-economic-social-burden/metadata.json",
        "conductor/tracks/005-economic-social-burden/plan.md",
        "conductor/tracks/005-economic-social-burden/review.md",
        "docs/decisions/2026-08-31-track-005-method-options.yml",
        "examples/economics/component-first-invented.yml",
        "schemas/economic-component-prototype.schema.json",
        "src/rareburden/economic_components.py",
        "src/rareburden/resources/repository/conductor/tracks/005-economic-social-burden/metadata.json",
        "src/rareburden/resources/repository/conductor/tracks/005-economic-social-burden/plan.md",
        "src/rareburden/resources/repository/conductor/tracks/005-economic-social-burden/review.md",
        "src/rareburden/resources/repository/docs/decisions/2026-08-31-track-005-method-options.yml",
        "src/rareburden/resources/repository/examples/economics/component-first-invented.yml",
        "src/rareburden/resources/repository/runtime-assets.json",
        "src/rareburden/resources/repository/schemas/economic-component-prototype.schema.json",
        "tests/test_economic_components.py",
        "tests/test_track005_method_options.py",
    }
    assert set(manifest["files"]) == expected
    for relative, digest in manifest["files"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    assert (ROOT / "schemas/economic-component-prototype.schema.json").read_bytes() == (
        ROOT
        / "src/rareburden/resources/repository/schemas/economic-component-prototype.schema.json"
    ).read_bytes()


def test_component_candidate_retains_all_activation_and_release_blocks() -> None:
    manifest = json.loads(MANIFEST.read_bytes())
    assert manifest["experimental"] is True
    assert manifest["synthetic_only"] is True
    for field in (
        "economic_use",
        "valuation",
        "totals",
        "engine_integration",
        "empirical_activation",
        "controlled_data_activation",
        "track_complete",
        "release",
    ):
        assert manifest[field] is False
    assert manifest["validation"] == {
        "focused_tests_passed": 43,
        "full_tests_passed": 1816,
        "repository_integrity_passed": True,
        "retained_provenance_passed": True,
        "hosted_checks_passed": False,
    }
