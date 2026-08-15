from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCREENING = ROOT / "docs" / "track-007-screening-2026-08-15.json"
ADJUDICATION = ROOT / "docs" / "track-007-title-cluster-adjudication-2026-08-15.json"


def test_every_flagged_title_cluster_has_exact_record_level_adjudication() -> None:
    screening = json.loads(SCREENING.read_text(encoding="utf-8"))
    adjudication = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    assert adjudication["raw_responses_retained"] is False
    assert "gh api JSON observation bytes" in adjudication["hash_scope"]["github"]
    flagged = {
        item["normalized_title"]: set(item["canonical_keys"])
        for item in screening["potential_entity_duplicates"]
    }
    resolved = {
        item["normalized_title"]: set(item["canonical_keys"]) for item in adjudication["clusters"]
    }
    assert resolved == flagged
    assert adjudication["counts"]["record_level_adjudicated"] == len(flagged)


def test_repository_records_are_not_silently_entity_merged() -> None:
    adjudication = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    repository_clusters = [
        item
        for item in adjudication["clusters"]
        if item["disposition"] == "keep_separate_repository_records"
    ]
    assert len(repository_clusters) == 3
    for cluster in repository_clusters:
        assert cluster["entity_equivalence"] == "unresolved"
        ids = {observation["repository_id"] for observation in cluster["observations"]}
        assert len(ids) == 2
        assert all(not observation["fork"] for observation in cluster["observations"])
        assert all(observation["parent"] is None for observation in cluster["observations"])
        assert all(observation["source"] is None for observation in cluster["observations"])
        assert all(
            len(observation["response_sha256"]) == 64 for observation in cluster["observations"]
        )


def test_preprint_and_article_are_linked_without_dropping_either_record() -> None:
    adjudication = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    cluster = next(
        item
        for item in adjudication["clusters"]
        if item["disposition"] == "link_versions_single_work"
    )
    assert cluster["canonical_work_key"] == "doi:10.2217/frd-2020-0004"
    relations = {
        (item["doi"], item["relation"], item["related_doi"]) for item in cluster["observations"]
    }
    assert relations == {
        (
            "10.21203/rs.3.rs-32979/v1",
            "is-preprint-of",
            "10.2217/frd-2020-0004",
        ),
        (
            "10.2217/frd-2020-0004",
            "has-preprint",
            "10.21203/rs.3.rs-32979/v1",
        ),
    }
