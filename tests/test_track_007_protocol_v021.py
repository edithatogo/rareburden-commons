from pathlib import Path

from rareburden.schema import load_mapping

ROOT = Path(__file__).parents[1]
PROTOCOL = ROOT / "docs/track-007-protocol-v0.2.1-preparation.yml"


def test_v021_preparation_is_not_frozen() -> None:
    data = load_mapping(PROTOCOL)
    assert data["status"] == "prepared_not_frozen"
    assert data["supersedes"].endswith("track-007-protocol-v0.2.0.md")
    assert data["owner_authorization"]["community_authority"] == "pending"
    assert (
        data["owner_authorization"]["independent_approval"]
        == "not_applicable_to_single_developer_repository"
    )


def test_v021_has_bounded_strata_and_capture_contract() -> None:
    data = load_mapping(PROTOCOL)
    assert len(data["strata"]["languages"]) == 8
    assert len(data["strata"]["regions"]) == 6
    assert data["capture_contract"]["one_immutable_capture_per_provider_language_region_stratum"]
    assert data["capture_contract"]["language_semantics"].startswith("declared_query_language")
    assert data["capture_contract"]["geography_semantics"].startswith("query_country_scope")
    assert data["screening"]["missing_is_exclusion"] is False


def test_v021_keeps_community_and_global_claims_fail_closed() -> None:
    data = load_mapping(PROTOCOL)
    prohibited = set(data["claims"]["prohibited"])
    assert {"global_coverage", "regional_representativeness", "community_approval"} <= prohibited
    assert "community_authority_or_partnership_implied_without_evidence" in data["stop_triggers"]
