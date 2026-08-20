import copy
import json
from pathlib import Path

import pytest

from scripts.resolve_track_007_bounded_content import resolve

ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "docs/track-007-live-safe-metadata-final-2026-08-16.json"
OUTPUT = ROOT / "docs/track-007-bounded-content-resolution-2026-08-20.json"


def test_bounded_content_resolution_closes_uncertainty_without_exclusion() -> None:
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert data["schema_version"] == "RBC-LAND-007-BOUNDED-CONTENT-v0.2.0"
    assert data["counts"] == {
        "include_bounded_adjacency": 54,
        "not_assessable_in_bounded_public_metadata_scope": 90,
    }
    assert len(data["resolutions"]) == 144
    assert all(item["evidence_sha256"].startswith("sha256:") for item in data["resolutions"])
    assert data["future_assessment_priority_counts"] == {
        "tier_1_explicit_safe_metadata_signal": 46,
        "tier_2_no_explicit_safe_metadata_signal": 44,
    }
    unresolved = [
        item
        for item in data["resolutions"]
        if item["resolution"] == "not_assessable_in_bounded_public_metadata_scope"
    ]
    assert len(unresolved) == 90
    assert all("future_assessment_priority" in item for item in unresolved)
    assert all(
        "future_assessment_priority" not in item
        for item in data["resolutions"]
        if item["resolution"] == "include_bounded_adjacency"
    )
    assert "confirmed_novelty" in data["prohibited_claims"]
    assert "community_approval" in data["prohibited_claims"]
    assert "global_or_geographic_representativeness" in data["prohibited_claims"]


def test_bounded_content_resolution_is_deterministic() -> None:
    assert resolve(SOURCE.read_bytes()) == json.loads(OUTPUT.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "defect", ["duplicate", "missing_hash", "malformed_hash", "unsupported_decision", "non_mapping"]
)
def test_bounded_content_resolution_rejects_invalid_sources(defect: str) -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    broken = copy.deepcopy(source)
    if defect == "duplicate":
        broken["decisions"][1]["identifier_key"] = broken["decisions"][0]["identifier_key"]
    elif defect == "missing_hash":
        broken["decisions"][0].pop("response_sha256", None)
        broken["decisions"][0].pop("evidence_sha256", None)
    elif defect == "malformed_hash":
        broken["decisions"][0]["response_sha256"] = "sha256:not-a-digest"
    elif defect == "non_mapping":
        broken["decisions"][0] = ["not", "an", "object"]
    else:
        broken["decisions"][0]["decision"] = "exclude"
    with pytest.raises(ValueError):
        resolve(json.dumps(broken).encode())
