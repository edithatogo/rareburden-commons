from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_archival_policy_is_maximal_but_fail_closed() -> None:
    policy = yaml.safe_load(
        (ROOT / "docs/track-002-lawful-archival-policy-2026-08-15.yml").read_text()
    )
    assert policy["policy"] == "maximal_lawful_archival"
    assert policy["default"] == "metadata_hash_citation_manifest_only"
    records = {record["source_id"]: record for record in policy["records"]}
    assert records["un-world-population-prospects"]["raw_upload_target"] == (
        "public_open_source_projection"
    )
    assert "preserve_attribution" in records["un-world-population-prospects"]["conditions"]
    assert records["who-global-health-estimates"]["raw_upload_target"] == (
        "private_huggingface_archive"
    )
    assert records["world-bank-indicators-api"]["raw_upload_target"] == (
        "public_open_source_projection"
    )
    assert records["mondo-disease-ontology"]["raw_upload_target"] == (
        "public_open_source_projection"
    )
    assert records["ncbi-clinvar"]["raw_upload_target"] == ("public_open_source_projection")
    assert records["human-phenotype-ontology"]["raw_upload_target"] == (
        "private_huggingface_archive"
    )
    assert "private hosting is still a copy and third-party transfer" in policy["stop_rules"]
