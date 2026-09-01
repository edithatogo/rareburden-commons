from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/ledger/track005-component-prototype-20260901.json"


def test_component_candidate_binds_exact_files_and_selected_proposal() -> None:
    manifest = json.loads(MANIFEST.read_bytes())
    assert manifest["candidate_commit"] == "a0e14be0d0c95b994eb69e1b979fc76aae60a45c"
    assert manifest["candidate_tree"] == "2bcb2b90ab91e5ed57fd478cde619870eb000f6a"
    assert manifest["selected_proposal_commit"] == ("1ed8ed425120f31f6d812230e924de6f3ca7b25f")
    assert manifest["selected_option"] == "A"
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
        "focused_tests_passed": 31,
        "full_tests_passed": 1807,
        "repository_integrity_passed": True,
        "retained_provenance_passed": True,
        "hosted_checks_passed": False,
    }
