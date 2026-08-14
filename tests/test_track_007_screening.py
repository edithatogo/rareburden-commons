from __future__ import annotations

import pytest

from scripts.screen_track_007_results import apply_resolutions, screen


def _result(registry: str, query: str, records: list[dict[str, str]]) -> dict[str, object]:
    return {
        "registry": registry,
        "query_string": query,
        "first_page_records": records,
    }


def test_shared_doi_is_deduplicated_across_indexes() -> None:
    snapshot = {
        "protocol_version": "RBC-LAND-007-v0.2.0",
        "records": [
            _result(
                "crossref",
                "rare disease burden",
                [
                    {
                        "identifier": "10.1234/example",
                        "doi": "10.1234/EXAMPLE",
                        "title": "Rare disease burden study",
                        "canonical_url": "https://doi.org/10.1234/example",
                    }
                ],
            ),
            _result(
                "zenodo",
                "rare disease prevalence",
                [
                    {
                        "identifier": "123",
                        "doi": "https://doi.org/10.1234/example",
                        "title": "Rare disease burden study",
                        "canonical_url": "https://zenodo.org/records/123",
                    }
                ],
            ),
        ],
    }
    result = screen(snapshot)
    assert result["counts"]["discovered_occurrences"] == 2
    assert result["counts"]["screened"] == 1
    assert result["counts"]["exact_duplicate_occurrences_removed"] == 1
    assert len(result["decisions"][0]["occurrences"]) == 2


def test_matching_titles_without_shared_identifier_are_flagged_not_merged() -> None:
    title = "Rare disease registry"
    snapshot = {
        "protocol_version": "RBC-LAND-007-v0.2.0",
        "records": [
            _result(
                "github",
                "rare disease registry",
                [
                    {
                        "identifier": "example/registry",
                        "title": title,
                        "canonical_url": "https://github.com/example/registry",
                    }
                ],
            ),
            _result(
                "huggingface_datasets",
                "rare disease registry",
                [
                    {
                        "identifier": "example/registry",
                        "title": title,
                        "canonical_url": "https://huggingface.co/datasets/example/registry",
                    }
                ],
            ),
        ],
    }
    result = screen(snapshot)
    assert result["counts"]["screened"] == 2
    assert result["counts"]["potential_entity_duplicate_groups"] == 1


def test_repository_self_result_is_excluded() -> None:
    snapshot = {
        "protocol_version": "RBC-LAND-007-v0.2.0",
        "records": [
            _result(
                "github",
                "rare disease burden",
                [
                    {
                        "identifier": "edithatogo/rareburden-commons",
                        "title": "rareburden-commons",
                        "canonical_url": "https://github.com/edithatogo/rareburden-commons",
                    }
                ],
            )
        ],
    }
    result = screen(snapshot)
    assert result["decisions"][0]["decision"] == "exclude"
    assert result["decisions"][0]["reason"] == "self_result"


def test_evidence_bound_resolution_closes_only_uncertain_record() -> None:
    snapshot = {
        "protocol_version": "RBC-LAND-007-v0.2.0",
        "records": [
            _result(
                "crossref",
                "rare disease registry",
                [
                    {
                        "identifier": "10.example/grant",
                        "title": "",
                        "canonical_url": "https://doi.org/10.example/grant",
                    }
                ],
            )
        ],
    }
    result = apply_resolutions(
        screen(snapshot),
        {
            "resolution_version": "test-v1",
            "scope": "bounded_test",
            "resolutions": [
                {
                    "canonical_key": "crossref:10.example/grant",
                    "disposition": "exclude",
                    "reason": "persistent_identifier_metadata_identifies_grant",
                    "evidence": {"response_sha256": "sha256:" + "0" * 64},
                }
            ],
        },
    )
    assert result["counts"]["uncertain"] == 0
    assert result["counts"]["excluded"] == 1
    assert result["decisions"][0]["resolution"]["response_sha256"].startswith("sha256:")


def test_resolution_cannot_overwrite_a_decided_record() -> None:
    snapshot = {
        "protocol_version": "RBC-LAND-007-v0.2.0",
        "records": [
            _result(
                "github",
                "rare disease registry",
                [
                    {
                        "identifier": "example/registry",
                        "title": "Rare disease registry",
                        "canonical_url": "https://github.com/example/registry",
                    }
                ],
            )
        ],
    }
    with pytest.raises(ValueError, match="non-uncertain"):
        apply_resolutions(
            screen(snapshot),
            {
                "resolution_version": "test-v1",
                "scope": "bounded_test",
                "resolutions": [
                    {
                        "canonical_key": "github:example/registry",
                        "disposition": "exclude",
                        "reason": "invalid_override",
                        "evidence": {"response_sha256": "sha256:" + "0" * 64},
                    }
                ],
            },
        )
