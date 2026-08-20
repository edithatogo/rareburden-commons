import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
PILOT = ROOT / "docs/track-007-v021-option-a-pilot-2026-08-20.json"


def test_option_a_pilot_has_one_hash_bound_observation_per_cell() -> None:
    data = json.loads(PILOT.read_text(encoding="utf-8"))
    assert data["status"] == "bounded_observation_complete"
    assert data["selected_option"] == "A"
    observations = data["observations"]
    assert len(observations) == 48
    keys = {
        (item["provider"], item["language_stratum"], item["region_stratum"])
        for item in observations
    }
    assert len(keys) == 48
    assert all(item.get("response_sha256", "").startswith("sha256:") for item in observations)
    assert all("body" not in item and "raw_response" not in item for item in observations)


def test_option_a_pilot_preserves_missingness_and_claim_boundaries() -> None:
    data = json.loads(PILOT.read_text(encoding="utf-8"))
    assert any(item["missingness"] == "unknown" for item in data["observations"])
    assert "global_coverage" in data["prohibited_claims"]
    assert "community_approval" in data["prohibited_claims"]
