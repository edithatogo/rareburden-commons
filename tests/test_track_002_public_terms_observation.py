from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_public_terms_observation_remains_non_activating() -> None:
    document = yaml.safe_load(
        (ROOT / "docs/track-002-public-terms-observation-2026-08-03.yml").read_text()
    )
    assert document["status"].startswith("observation_only")
    assert all(record["activation"] == "disabled" for record in document["records"])
    assert "custodian disposition" in document["fail_closed_rules"][0]
