from __future__ import annotations

import urllib.parse

import pytest

from scripts.discover_clinvar_recursive_metadata import discover


def _loader(url: str) -> bytes:
    path = urllib.parse.urlsplit(url).path
    if path.endswith("archive/") or path.endswith("archive_2.0/"):
        return b'<a href="2026/">year</a><a href="release.gz.md5">sum</a>'
    if path.endswith("2026/"):
        return b'<a href="release.gz">data</a>'
    return b'<a href="README.txt">readme</a>'


def test_recursive_inventory_is_deterministic_and_metadata_only() -> None:
    first = discover(
        observed_at="2026-08-16T00:00:00Z",
        max_requests=20,
        max_depth=2,
        delay_seconds=0,
        loader=_loader,
    )
    second = discover(
        observed_at="2026-08-16T00:00:00Z",
        max_requests=20,
        max_depth=2,
        delay_seconds=0,
        loader=_loader,
    )
    assert first == second
    assert first["exhausted_within_scope"]
    assert first["byte_route"] == "metadata_only_submitter_provenance_review"
    assert not any(first["claims"].values())
    assert all(
        "release_key" not in record and "artifact_name" in record
        for observation in first["observations"]
        for record in observation["records"]
    )


def test_recursive_inventory_retains_frontier_at_request_budget() -> None:
    result = discover(
        observed_at="x",
        max_requests=7,
        max_depth=2,
        delay_seconds=0,
        loader=_loader,
    )
    assert not result["exhausted_within_scope"]
    assert result["frontier_queue_count"] > 0


def test_recursive_inventory_rejects_invalid_budget() -> None:
    with pytest.raises(ValueError, match="budgets"):
        discover(observed_at="x", max_requests=1, max_depth=0, delay_seconds=0, loader=_loader)
