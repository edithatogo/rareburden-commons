from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ALTERNATIVES = _load("resolve_track_007_lawful_alternatives")
ENRICH = _load("enrich_track_007_live_minimal_metadata")
MERGE = _load("merge_track_007_live_safe_metadata")


def test_restricted_doi_uses_crossref_not_publisher_and_keeps_ambiguity() -> None:
    source = {
        "decisions": [
            {
                "canonical_key": "doi:10.1/example",
                "identifier": "10.1/example",
                "canonical_url": "https://doi.org/10.1/example",
                "eligibility_state": "pending_lawful_access",
            }
        ]
    }

    def fixture(url: str, _timeout: int):
        assert url.startswith("https://api.crossref.org/works/")
        body = {
            "message": {
                "title": ["Introducing a journal"],
                "type": "journal-article",
                "publisher": "Example",
                "URL": "https://doi.org/10.1/example",
            }
        }
        return json.dumps(body).encode(), 200, url

    result = ALTERNATIVES.resolve(json.dumps(source).encode(), fetch_record=fixture)
    assert result["counts"] == {"include": 0, "uncertain": 1, "pending_lawful_access": 0}
    assert result["resolutions"][0]["decision"] == "uncertain"
    assert all("abstract" not in item for item in result["resolutions"])


def test_failed_public_alternative_stays_pending_never_excluded() -> None:
    source = {
        "decisions": [
            {
                "canonical_key": "doi:10.1/example",
                "identifier": "10.1/example",
                "canonical_url": "https://doi.org/10.1/example",
                "eligibility_state": "pending_lawful_access",
            }
        ]
    }
    result = ALTERNATIVES.resolve(
        json.dumps(source).encode(), fetch_record=lambda url, timeout: (b"no", 429, url)
    )
    assert result["resolutions"][0]["decision"] == "pending_lawful_access"


def test_safe_live_metadata_can_upgrade_but_never_excludes() -> None:
    source = {
        "observations": [
            {
                "identifier_key": "github:o/r",
                "identifier": "o/r",
                "registry": "github",
                "request_url": "https://api.github.com/repos/o/r",
                "title": "Project",
                "canonical_url": "https://github.com/o/r",
            }
        ]
    }

    def fixture(url: str, _timeout: int):
        body = {
            "topics": ["rare-disease", "registry"],
            "language": "Python",
            "license": {"spdx_id": "MIT"},
            "archived": False,
            "fork": False,
        }
        return json.dumps(body).encode(), 200, url

    result = ENRICH.enrich(json.dumps(source).encode(), fetch_record=fixture)
    assert result["counts"] == {"include": 1, "uncertain": 0}
    serialized = json.dumps(result).casefold()
    for prohibited in ('"description"', '"abstract"', '"body"', '"full_text"'):
        assert prohibited not in serialized


def test_safe_live_metadata_ambiguity_remains_uncertain() -> None:
    source = {
        "observations": [
            {
                "identifier_key": "zenodo:1",
                "identifier": "1",
                "registry": "zenodo",
                "request_url": "https://zenodo.org/api/records/1",
                "title": "Dataset",
                "canonical_url": "https://zenodo.org/records/1",
            }
        ]
    }
    payload = {
        "metadata": {
            "keywords": [],
            "resource_type": {"id": "dataset"},
            "language": None,
            "access_right": "open",
        }
    }
    result = ENRICH.enrich(
        json.dumps(source).encode(),
        fetch_record=lambda url, timeout: (json.dumps(payload).encode(), 200, url),
    )
    assert result["counts"] == {"include": 0, "uncertain": 1}


def test_safe_enrichment_never_downgrades_prior_hash_bound_include() -> None:
    source = {
        "observations": [
            {
                "identifier_key": "github:o/r",
                "identifier": "o/r",
                "registry": "github",
                "request_url": "https://api.github.com/repos/o/r",
                "title": "Project",
                "canonical_url": "https://github.com/o/r",
                "screening_decision": "include_for_content_assessment",
            }
        ]
    }
    payload = {"topics": [], "language": None, "license": None, "archived": False, "fork": False}
    result = ENRICH.enrich(
        json.dumps(source).encode(),
        fetch_record=lambda url, timeout: (json.dumps(payload).encode(), 200, url),
    )
    assert result["counts"] == {"include": 1, "uncertain": 0}
    assert result["decisions"][0]["reason"] == "prior_hash_bound_public_signal_preserved"


def test_merge_preserves_prior_include_and_safe_upgrade() -> None:
    prior = {
        "observations": [
            {
                "identifier_key": "github:a/a",
                "screening_decision": "include_for_content_assessment",
            },
            {
                "identifier_key": "github:b/b",
                "screening_decision": "uncertain_public_metadata_signal",
            },
        ]
    }
    enrichment = {
        "content_retention": "safe_only",
        "limitations": [],
        "decisions": [
            {"identifier_key": "github:a/a", "decision": "uncertain", "reason": "insufficient"},
            {"identifier_key": "github:b/b", "decision": "include", "reason": "safe"},
        ],
    }
    result = MERGE.merge(json.dumps(prior).encode(), json.dumps(enrichment).encode())
    assert result["counts"] == {"include": 2, "uncertain": 0}


def test_committed_lawful_alternative_evidence_is_bounded_and_hash_bound() -> None:
    from rareburden.schema import load_mapping

    update = load_mapping(ROOT / "docs/track-007-lawful-alternatives-update-2026-08-16.yml")
    for evidence in update["evidence"]:
        actual = hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest()
        assert actual == evidence["sha256"]
    assert update["frozen_69_outcome"]["include"] == 66
    assert update["frozen_69_outcome"]["exclude"] == 2
    assert update["frozen_69_outcome"]["uncertain"] == 1
    assert update["frozen_69_outcome"]["pending_lawful_access"] == 0
    assert update["live_144_outcome"]["include"] == 54
    assert update["live_144_outcome"]["uncertain"] == 90
    assert update["additional_bibliographic_provider"]["activated"] is False
