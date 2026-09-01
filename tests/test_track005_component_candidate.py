from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/ledger/track005-component-prototype-20260901.json"


def test_component_candidate_binds_exact_files_and_selected_proposal() -> None:
    manifest = json.loads(MANIFEST.read_bytes())
    assert manifest["candidate_commit"] == "0c1fb2530913fca40c5b650b06d7be84bace915e"
    assert manifest["candidate_tree"] == "0528bd1c37e27659b8953bc59d2ccea768791779"
    assert manifest["selected_proposal_commit"] == ("1ed8ed425120f31f6d812230e924de6f3ca7b25f")
    assert manifest["selected_option"] == "A"
    for relative, digest in manifest["files"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


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
