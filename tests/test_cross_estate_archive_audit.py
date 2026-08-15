from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from scripts.render_cross_estate_archive_audit import REQUIRED_FAMILIES, render_audit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/track-002-cross-estate-archive-audit-2026-08-16.yml"


def _document() -> dict:
    return yaml.safe_load(SOURCE.read_text(encoding="utf-8"))


def test_cross_estate_audit_covers_requested_scope_and_is_deterministic() -> None:
    first = render_audit(_document(), ROOT)
    second = render_audit(_document(), ROOT)
    assert first == second
    assert {record["id"] for record in first["families"]} == REQUIRED_FAMILIES
    assert len(first["audit_sha256"]) == 64
    assert all(len(record["evidence_sha256"]) == 64 for record in first["families"])
    assert not any(first["claims"].values())
    assert first["archive_counts"]["explicitly_counted_public_assets"] == 492
    assert sum(first["archive_counts"]["components"].values()) == 492
    mondo = next(record for record in first["families"] if record["id"] == "mondo")
    assert "seven digest-pinned assets" in mondo["observed"]


def test_cross_estate_audit_keeps_licensed_families_metadata_only() -> None:
    document = _document()
    for family_id in ("umls", "snomed-ct", "meddra"):
        record = next(record for record in document["families"] if record["id"] == family_id)
        assert record["public_route"] == "metadata_only"
        assert (
            "private" in record["private_route"]
            or record["private_route"] == "prepared_not_executed"
        )

    unsafe = deepcopy(document)
    next(record for record in unsafe["families"] if record["id"] == "umls")["public_route"] = (
        "existing_public_archive"
    )
    with pytest.raises(ValueError, match="licensed family umls"):
        render_audit(unsafe, ROOT)


def test_cross_estate_audit_rejects_scope_and_claim_inflation() -> None:
    incomplete = _document()
    incomplete["families"].pop()
    with pytest.raises(ValueError, match="family scope"):
        render_audit(incomplete, ROOT)

    inflated = _document()
    inflated["claims"]["all_versions_complete"] = True
    with pytest.raises(ValueError, match="claims must remain false"):
        render_audit(inflated, ROOT)

    drifted_count = _document()
    drifted_count["archive_counts"]["components"]["mondo"] = 1916
    with pytest.raises(ValueError, match="count components"):
        render_audit(drifted_count, ROOT)


def test_cross_estate_audit_rejects_missing_evidence() -> None:
    document = _document()
    document["families"][0]["evidence"] = "../outside.json"
    with pytest.raises(ValueError, match="unsafe or missing evidence"):
        render_audit(document, ROOT)
