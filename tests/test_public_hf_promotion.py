from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.promote_rights_cleared_hf_family import load_family

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/huggingface/public-promotion-2026-08-21.json"


def test_all_public_promotion_families_are_bounded_and_rights_cleared() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert payload["status"] == "bounded_exact_file_candidate_no_promotion"
    assert payload["promotion_enabled"] is False
    assert payload["claims"] == {
        "all_private_content_redistributable": False,
        "licensed_terminology_public": False,
        "private_quota_reclaimed": False,
    }
    for item in payload["families"]:
        _, family = load_family(MANIFEST, item["id"])
        assert family == item


def test_raw_promotion_is_quarantined() -> None:
    from scripts.promote_rights_cleared_hf_family import promote

    with pytest.raises(RuntimeError, match="quarantined"):
        promote(MANIFEST, "disease-ontology", max_bytes=2_000_000_000)


def test_unknown_family_fails_closed() -> None:
    with pytest.raises(ValueError, match="exactly once"):
        load_family(MANIFEST, "umls")


def test_unsafe_or_incomplete_family_fails_closed(tmp_path: Path) -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["families"][0]["prefix"] = "../licensed-private/"
    path = tmp_path / "unsafe.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="unsafe"):
        load_family(path, "disease-ontology")
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["families"][0]["conditions"].remove("record_sha256")
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="mandatory"):
        load_family(path, "disease-ontology")
