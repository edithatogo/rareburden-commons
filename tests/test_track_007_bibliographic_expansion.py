from __future__ import annotations

import hashlib
import importlib.util
import json
import urllib.parse
from pathlib import Path

import pytest

from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]


def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CAPTURE = _load_script("capture_track_007_bibliographic_expansion")
RESOLVE = _load_script("resolve_track_007_pending_public_content")


def test_crossref_capture_enforces_budget_and_missing_language() -> None:
    def fixture(url: str, _timeout: int) -> tuple[bytes, int, str]:
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        cursor = query["cursor"][0]
        item_id = "one" if cursor == "*" else "two"
        payload = {
            "message": {
                "total-results": 2,
                "next-cursor": "next",
                "items": [
                    {
                        "DOI": f"10.1/{item_id}-{hash(query['query'][0])}",
                        "title": ["Rare disease registry"],
                        "URL": "https://doi.org/example",
                        "type": "journal-article",
                    }
                ],
            }
        }
        return json.dumps(payload).encode(), 200, url

    report = CAPTURE.capture(
        fetch_page=fixture,
        rows=1,
        max_pages=2,
        retrieved_at_utc="2026-08-16T00:00:00Z",
    )
    assert report["requests_made"] == report["request_budget"] == 24
    assert all(
        capture["record_language_counts"] == {"not_reported": 2} for capture in report["captures"]
    )


@pytest.mark.parametrize(("rows", "pages"), [(0, 1), (101, 1), (20, 0), (20, 4)])
def test_crossref_capture_rejects_unbounded_configuration(rows: int, pages: int) -> None:
    with pytest.raises(ValueError):
        CAPTURE.capture(rows=rows, max_pages=pages)


def test_public_content_resolution_never_excludes_failed_access() -> None:
    eligibility = {
        "decisions": [
            {
                "canonical_key": "doi:10.1/example",
                "identifier": "10.1/example",
                "eligibility_state": "pending_content_assessment",
            }
        ]
    }

    def fixture(url: str, _timeout: int) -> tuple[bytes, int, str]:
        return b"unavailable", 404, url

    report = RESOLVE.resolve(json.dumps(eligibility).encode(), fetch_record=fixture)
    assert report["counts"] == {"pending_public_evidence": 1}
    assert report["resolutions"] == []


def test_committed_expansion_and_eligibility_are_bounded_and_content_free() -> None:
    expansion = json.loads(
        (ROOT / "docs/track-007-bibliographic-expansion-2026-08-16.json").read_text()
    )
    eligibility = json.loads(
        (ROOT / "docs/track-007-fulltext-eligibility-v0.3.0-2026-08-16.json").read_text()
    )
    assert expansion["requests_made"] == expansion["request_budget"] == 24
    assert sum(c["unique_dois_captured"] for c in expansion["captures"]) == 480
    assert {c["declared_query_language"] for c in expansion["captures"]} == {
        "de",
        "en",
        "es",
        "fr",
        "pt",
    }
    assert eligibility["counts"]["eligibility_state"] == {
        "exclude": 2,
        "include": 56,
        "pending_content_assessment": 2,
        "pending_lawful_access": 8,
        "uncertain": 1,
    }
    serialized = json.dumps(expansion).casefold()
    for prohibited in ('"abstract"', '"description"', '"full_text"'):
        assert prohibited not in serialized


def test_bibliographic_content_update_binds_exact_evidence_and_missingness() -> None:
    update = load_mapping(ROOT / "docs/track-007-bibliographic-content-update-2026-08-16.yml")
    for record in update["evidence"]:
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    assert update["frozen_69_record_outcome"]["pending_lawful_access"] == 8
    assert update["bibliographic_expansion"]["record_language"] == {"not_reported": 480}
    assert update["bibliographic_expansion"]["geography_sampling"] == "not_measured"
