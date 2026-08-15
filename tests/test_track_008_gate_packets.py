from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from scripts.render_track008_source_provenance import render_inventory

ROOT = Path(__file__).resolve().parents[1]


def test_track_008_source_inventory_is_fail_closed() -> None:
    document = yaml.safe_load(
        (ROOT / "docs/track-008-source-release-inventory-2026-08-03.yml").read_text()
    )
    assert document["status"] == "bounded_source_reconciliation"
    assert document["activation"] == "synthetic_and_metadata_only_no_v0_4_freeze"
    assert len(document["records"]) == 8
    assert not any(document["claims"].values())
    rendered = render_inventory(document, ROOT)
    assert len(rendered["inventory_sha256"]) == 64
    assert all(len(record["release_evidence_sha256"]) == 64 for record in rendered["records"])


def test_track_008_source_inventory_rejects_unsafe_activation_and_rights() -> None:
    document = yaml.safe_load(
        (ROOT / "docs/track-008-source-release-inventory-2026-08-03.yml").read_text()
    )
    activated = deepcopy(document)
    activated["claims"]["production_activation"] = True
    with pytest.raises(ValueError, match="claims must remain false"):
        render_inventory(activated, ROOT)

    unsafe_public = deepcopy(document)
    hpo = next(
        record
        for record in unsafe_public["records"]
        if record["source_id"] == "human-phenotype-ontology"
    )
    hpo["byte_route"] = "public_rights_filtered_archive"
    with pytest.raises(ValueError, match="lacks exact permissive terms"):
        render_inventory(unsafe_public, ROOT)


def test_track_008_source_inventory_keeps_controlled_bytes_disabled() -> None:
    document = yaml.safe_load(
        (ROOT / "docs/track-008-source-release-inventory-2026-08-03.yml").read_text()
    )
    for source_id in (
        "human-phenotype-ontology",
        "umls-2026aa",
        "snomed-ct-uts-current",
        "who-icd-api-observation",
    ):
        record = next(record for record in document["records"] if record["source_id"] == source_id)
        assert record["byte_route"] == "private_licensed_archive_only"
        assert "disabled" in record["semantic_use"]


def test_track_008_panel_packet_preserves_accountable_gate_boundary() -> None:
    document = yaml.safe_load(
        (ROOT / "docs/track-008-semantic-challenge-panel-2026-08-03.yml").read_text()
    )
    assert document["mode"] == "panel_assurance"
    assert document["panel"]["quorum"] >= 3
    assert len(document["panel"]["roles"]) == 3
    assert "cannot_replace" in document["accountable_gate_boundary"]
    assert "dissent" in document["required_output"]
