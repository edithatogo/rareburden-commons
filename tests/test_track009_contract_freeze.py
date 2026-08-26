from __future__ import annotations

import json

from scripts.gen_track009_contract_freeze import (
    BASELINE_COMMIT,
    OUTPUT,
    ROOT,
    build_manifest,
    render_manifest,
)


def test_contract_freeze_regenerates_exact_checked_in_bytes() -> None:
    assert (ROOT / OUTPUT).read_bytes() == render_manifest()


def test_contract_freeze_remains_bounded_and_non_authorizing() -> None:
    manifest = build_manifest()
    claims = manifest["claims"]
    assert isinstance(claims, dict)
    assert manifest["binding_baseline"]["repository_commit"] == BASELINE_COMMIT
    assert manifest["owner_disposition"]["path"].endswith(
        "track-009-owner-v04-freeze-disposition.yml"
    )
    assert claims == {
        "contract_frozen": True,
        "scope_synthetic_and_receipted_public_aggregate_only": True,
        "empirical_parameter_activation": False,
        "controlled_data_in_scope": False,
        "independent_review": False,
        "track_complete": False,
        "release_authority": False,
    }
    json.loads(render_manifest())
