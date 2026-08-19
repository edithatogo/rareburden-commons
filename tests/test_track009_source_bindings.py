from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from scripts.render_track009_source_bindings import render_bindings

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/track-009-source-release-bindings-2026-08-16.yml"


def _document() -> dict:
    return yaml.safe_load(SOURCE.read_text(encoding="utf-8"))


def test_track009_bindings_are_immutable_and_fail_closed() -> None:
    rendered = render_bindings(_document(), ROOT)
    assert len(rendered["source_releases"]) == 13
    assert len(rendered["binding_set_sha256"]) == 64
    assert not any(rendered["claims"].values())
    assert all(
        len(record["provenance_manifest_sha256"]) == 64 for record in rendered["source_releases"]
    )


def test_track009_private_and_unusable_sources_remain_disabled() -> None:
    document = _document()
    for record in document["source_releases"]:
        if record["visibility"] == "private" or record["licence_state"] not in {
            "permitted",
            "not_applicable",
        }:
            assert record["activation_state"].startswith("disabled_")

    unsafe = deepcopy(document)
    unsafe["source_releases"][3]["activation_state"] = "enabled_for_bounded_ledger"
    with pytest.raises(ValueError, match="private source"):
        render_bindings(unsafe, ROOT)


def test_track009_rejects_upstream_drift_and_contract_freeze() -> None:
    drifted = _document()
    drifted["upstream_inventory_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="fingerprint mismatch"):
        render_bindings(drifted, ROOT)

    frozen = _document()
    frozen["contract_freeze"] = True
    with pytest.raises(ValueError, match="freeze claims must remain false"):
        render_bindings(frozen, ROOT)
