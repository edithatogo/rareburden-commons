from __future__ import annotations

import json
import urllib.parse

import pytest

from scripts.discover_public_archive_history import SURFACES, build_inventory, discover_clinvar


def _loader(url: str) -> bytes:
    if url == SURFACES["orphacode"]:
        return b'<a href="https://www.orphacode.org/files/en-2026.zip">pack</a>'
    if urllib.parse.urlsplit(url).hostname == "sciences.orphadata.com":
        return b'<a href="https://www.orphadata.com/data/en_product1.xml">file</a>'
    if url == SURFACES["mondo"]:
        return json.dumps(
            [
                {
                    "tag_name": "v1",
                    "published_at": "2026-01-01T00:00:00Z",
                    "html_url": "https://github.com/monarch-initiative/mondo/releases/tag/v1",
                    "assets": [
                        {
                            "name": "mondo.owl",
                            "size": 12,
                            "browser_download_url": "https://github.com/monarch-initiative/mondo/releases/download/v1/mondo.owl",
                        }
                    ],
                }
            ]
        ).encode()
    if url == SURFACES["clinvar"]:
        return (
            b'<a href="variant_summary_2026-08.txt.gz">file</a>'
            b'<a href="variant_summary_2026-08.txt.gz.md5">hash</a>'
        )
    raise AssertionError(url)


def test_inventory_is_deterministic_bounded_and_content_addressed() -> None:
    first = build_inventory(observed_at="2026-08-16T00:00:00Z", loader=_loader, delay_seconds=0)
    second = build_inventory(observed_at="2026-08-16T00:00:00Z", loader=_loader, delay_seconds=0)
    assert first == second
    assert {item["family"] for item in first["observations"]} == {
        "orphacode",
        "orphadata",
        "mondo",
        "clinvar",
    }
    assert len(first["inventory_sha256"]) == 64
    assert not any(first["claims"].values())


def test_controlled_or_ambiguous_bytes_never_gain_public_route() -> None:
    inventory = build_inventory(observed_at="2026-08-16T00:00:00Z", loader=_loader, delay_seconds=0)
    clinvar = next(item for item in inventory["observations"] if item["family"] == "clinvar")
    assert all(
        record["byte_route"] == "metadata_only_submitter_provenance_review"
        for record in clinvar["records"]
    )


def test_clinvar_rejects_nonofficial_and_nondata_links() -> None:
    data = b'<a href="https://example.org/a.gz">bad</a><a href="README">readme</a>'
    assert discover_clinvar(data) == []


def test_live_mode_rejects_rate_bypass(tmp_path) -> None:
    import sys

    from scripts.discover_public_archive_history import main

    old = sys.argv
    sys.argv = [
        "discover",
        "--observed-at",
        "x",
        "--output",
        str(tmp_path / "x.json"),
        "--delay-seconds",
        "0",
    ]
    try:
        with pytest.raises(ValueError, match="at least one second"):
            main()
    finally:
        sys.argv = old
