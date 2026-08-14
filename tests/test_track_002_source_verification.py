from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/track-002-source-verification-2026-08-15.yml"


def test_exact_source_verification_preserves_fail_closed_boundaries() -> None:
    payload = yaml.safe_load(EVIDENCE.read_text())
    assert payload["activation"] == "disabled"
    records = {record["source_id"]: record for record in payload["records"]}

    for source_id in ("orphadata-science-epidemiology", "orphadata-science-alignments"):
        record = records[source_id]
        assert record["licence"] == "CC BY 4.0"
        assert record["sha256"]
        assert record["archival"] == "private_raw_copy_permitted_with_attribution_and_change_notice"

    assert records["un-world-population-prospects"]["archival"] == "metadata_hash_and_extraction_manifest_only"
    assert records["who-global-health-estimates"]["archival"] == "metadata_hash_and_lawful_derived_outputs_only"
    assert records["world-bank-indicators-api"]["status"] == "probe_only"
    assert "no silent substitution for WPP" in records["world-bank-indicators-api"]["prohibited_use"]


def test_source_verification_records_current_world_bank_probe() -> None:
    records = yaml.safe_load(EVIDENCE.read_text())["records"]
    world_bank = next(record for record in records if record["source_id"] == "world-bank-indicators-api")
    assert world_bank["response_bytes"] == 8826
    assert world_bank["observations"] == 44
    assert world_bank["response_last_updated"] == "2026-07-13"
    assert len(world_bank["response_sha256"]) == 64

