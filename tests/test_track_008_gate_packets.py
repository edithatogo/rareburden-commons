from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_track_008_source_inventory_is_fail_closed() -> None:
    document = yaml.safe_load(
        (ROOT / "docs/track-008-source-release-inventory-2026-08-03.yml").read_text()
    )
    assert document["status"] == "preparation_only"
    assert document["activation"].startswith("disabled")
    assert all(record["mapping_use"] == "disabled" for record in document["records"])
    assert all(record["content_sha256"] is None for record in document["records"])


def test_track_008_panel_packet_preserves_accountable_gate_boundary() -> None:
    document = yaml.safe_load(
        (ROOT / "docs/track-008-semantic-challenge-panel-2026-08-03.yml").read_text()
    )
    assert document["mode"] == "panel_assurance"
    assert document["panel"]["quorum"] >= 3
    assert len(document["panel"]["roles"]) == 3
    assert "cannot_replace" in document["accountable_gate_boundary"]
    assert "dissent" in document["required_output"]
