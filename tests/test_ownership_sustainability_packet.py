from __future__ import annotations

from pathlib import Path

from rareburden.schema import validate_document_files

ROOT = Path(__file__).parents[1]


def test_ownership_packet_is_blank_and_non_authorizing() -> None:
    packet = validate_document_files(
        ROOT / "examples/fixtures/ownership-sustainability-packet.json",
        ROOT / "schemas/ownership-sustainability-packet.schema.json",
    )
    assert packet["status"] == "preparation_only"
    assert packet["decision"] == "pending"
    assert all(role["primary"] == "" and role["backup"] == "" for role in packet["roles"])
