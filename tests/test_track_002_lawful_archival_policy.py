from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_archival_policy_is_maximal_but_fail_closed() -> None:
    policy = yaml.safe_load(
        (ROOT / "docs/track-002-lawful-archival-policy-2026-08-15.yml").read_text()
    )
    assert policy["policy"] == "maximal_lawful_archival"
    assert policy["default"] == "metadata_hash_citation_manifest_only"
    assert all(record["raw_upload_target"] is None for record in policy["records"])
    assert "private hosting is still a copy and third-party transfer" in policy["stop_rules"]
