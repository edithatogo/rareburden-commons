from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_huggingface_estate_audit_is_fail_closed() -> None:
    audit = yaml.safe_load((ROOT / "docs/huggingface-estate-audit-2026-08-21.yml").read_text())

    assert len(audit["live_inventory"]) == 3
    assert audit["ascertainment"]["all_sources_indexed"]["result"] is False
    assert audit["ascertainment"]["all_source_metadata_archived"]["result"] is False
    assert (
        audit["ascertainment"]["private_data_can_move_public"]["result"]
        == "some_exact_families_only"
    )
    assert audit["recommendation"] == "B"
    assert audit["claims"]["all_private_content_redistributable"] is False
    assert audit["claims"]["independent_review"] is False
