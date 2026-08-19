from __future__ import annotations

import json
import urllib.parse

import pytest

from scripts.discover_public_archive_frontier import (
    build_frontier,
    parse_clinvar_index,
    parse_orphanet_media,
)


def _loader(url: str) -> bytes:
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qs(parsed.query)
    page = int(query.get("page", ["1"])[0])
    if parsed.hostname == "api.github.com":
        if page == 1:
            return json.dumps(
                [
                    {
                        "tag_name": f"v{i}",
                        "published_at": "2026-01-01T00:00:00Z",
                        "html_url": f"https://github.com/monarch-initiative/mondo/releases/tag/v{i}",
                        "assets": [],
                    }
                    for i in range(100)
                ]
            ).encode()
        return b"[]"
    if parsed.hostname == "ftp.ncbi.nlm.nih.gov":
        return b'<a href="release.gz">data</a><a href="release.gz.md5">md5</a>'
    if parsed.hostname in {"sciences.orphadata.com", "www.orphacode.org"}:
        if page > 1:
            return b"[]"
        return json.dumps(
            [
                {
                    "id": 1,
                    "date_gmt": "2025-01-01T00:00:00",
                    "modified_gmt": "2025-01-02T00:00:00",
                    "mime_type": "application/zip",
                    "source_url": f"https://{parsed.hostname}/wp-content/uploads/change.zip",
                }
            ]
        ).encode()
    raise AssertionError(url)


def test_frontier_paginates_to_bounded_exhaustion_deterministically() -> None:
    first = build_frontier(observed_at="2026-08-16T00:00:00Z", loader=_loader, delay_seconds=0)
    second = build_frontier(observed_at="2026-08-16T00:00:00Z", loader=_loader, delay_seconds=0)
    assert first == second
    assert first["exhaustion"] == {
        "mondo_release_api": True,
        "orphadata-media": True,
        "orphacode-media": True,
    }
    assert len(first["frontier_sha256"]) == 64
    assert not any(first["claims"].values())


def test_clinvar_index_is_exact_host_and_prefix_bounded() -> None:
    url = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/archive/"
    data = (
        b'<a href="2026/release.gz">data</a>'
        b'<a href="https://example.org/bad.gz">bad</a>'
        b'<a href="../../../outside.gz">escape</a>'
    )
    records = parse_clinvar_index(url, data)
    assert [record["source_url"] for record in records] == [
        "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/archive/2026/release.gz"
    ]
    assert records[0]["byte_route"] == "metadata_only_submitter_provenance_review"


def test_orphanet_media_rejects_cross_host_source() -> None:
    data = json.dumps([{"id": 1, "source_url": "https://example.org/change.zip"}]).encode()
    with pytest.raises(ValueError, match="unexpected source host"):
        parse_orphanet_media(data, expected_host="www.orphacode.org")


def test_page_budgets_must_be_positive() -> None:
    with pytest.raises(ValueError, match="page budgets"):
        build_frontier(observed_at="x", loader=_loader, delay_seconds=0, max_mondo_pages=0)
