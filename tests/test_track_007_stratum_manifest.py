from pathlib import Path

from rareburden.schema import load_mapping

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "docs/track-007-stratum-capture-manifest-v0.2.1.yml"


def test_stratum_manifest_records_authorized_bounded_pilot() -> None:
    data = load_mapping(MANIFEST)
    assert data["status"] == "authorized_bounded_pilot_not_executed"
    assert data["execution_authorization"] == "owner_option_A_selected"
    assert data["observations"] == []
    assert data["planned"]["planned_capture_count"] == 4 * 3 * 4


def test_stratum_manifest_keeps_capture_and_claims_fail_closed() -> None:
    data = load_mapping(MANIFEST)
    assert "executed_capture" in data["claims"]["prohibited"]
    assert "regional_coverage" in data["claims"]["prohibited"]
    assert "community_authority" in data["claims"]["prohibited"]
    assert "execution_without_owner_scope_confirmation" in data["stop_triggers"]
    assert set(data["missingness_values"]) == {
        "observed",
        "unknown",
        "not_assessable",
        "not_applicable",
    }
