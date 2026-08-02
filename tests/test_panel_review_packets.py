from __future__ import annotations

from pathlib import Path

from rareburden.schema import load_mapping, validate_document_files

ROOT = Path(__file__).parents[1]
SCHEMA = ROOT / "schemas/panel-review-packet.schema.json"


def test_track_002_and_007_panel_fixtures_are_pending_and_schema_valid() -> None:
    for name in ("track-002-panel-packet-synthetic.json", "track-007-panel-packet-synthetic.json"):
        packet = validate_document_files(ROOT / "examples/fixtures" / name, SCHEMA)
        assert packet["accountable_gate_status"] == "pending"
        assert packet["recommendation"] == "prepare"


def test_panel_fixtures_use_at_least_three_distinct_roles() -> None:
    for name in ("track-002-panel-packet-synthetic.json", "track-007-panel-packet-synthetic.json"):
        packet = validate_document_files(ROOT / "examples/fixtures" / name, SCHEMA)
        assert len(set(packet["panel_roles"])) >= 3
