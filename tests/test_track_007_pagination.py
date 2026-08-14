from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.capture_track_007_pages import CaptureError, PageRequest, capture_query

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "track007_pagination"


def fixture_pages(prefix: str):
    def fetch(request: PageRequest, _timeout: int) -> tuple[bytes, int, str]:
        path = FIXTURES / f"{prefix}-page-{request.page_number}.json"
        return path.read_bytes(), 200, request.url

    return fetch


def test_declared_total_requires_exact_unique_capture() -> None:
    capture = capture_query(
        "github",
        "fixture query",
        page_size=2,
        max_pages=3,
        timeout=1,
        fetch_page=fixture_pages("github-complete"),
        retrieved_at_utc="2026-08-15T00:00:00Z",
    )
    assert capture["pages_captured"] == 2
    assert capture["unique_identifiers_captured"] == 3
    assert capture["stop_reason"] == "provider_total_reached"
    assert capture["capture_complete_for_declared_total"] is True
    assert "does not establish landscape" in capture["claim_boundary"]
    assert all(page["response_sha256"].startswith("sha256:") for page in capture["pages"])


def test_page_budget_is_explicitly_incomplete() -> None:
    capture = capture_query(
        "github",
        "fixture query",
        page_size=2,
        max_pages=1,
        timeout=1,
        fetch_page=fixture_pages("github-changed-total"),
    )
    assert capture["stop_reason"] == "page_budget_reached"
    assert capture["capture_complete_for_declared_total"] is False
    assert capture["provider_declared_total"] == 4


def test_changed_total_fails_closed() -> None:
    with pytest.raises(CaptureError, match="declared total changed"):
        capture_query(
            "github",
            "fixture query",
            page_size=2,
            max_pages=3,
            timeout=1,
            fetch_page=fixture_pages("github-changed-total"),
        )


def test_cross_page_duplicate_fails_closed() -> None:
    with pytest.raises(CaptureError, match="repeated identifiers"):
        capture_query(
            "github",
            "fixture query",
            page_size=2,
            max_pages=3,
            timeout=1,
            fetch_page=fixture_pages("github-repeat"),
        )


def test_invalid_json_and_http_status_fail_closed() -> None:
    def invalid_json(request: PageRequest, _timeout: int) -> tuple[bytes, int, str]:
        return b"not-json", 200, request.url

    with pytest.raises(CaptureError, match="invalid JSON"):
        capture_query(
            "zenodo", "fixture", page_size=2, max_pages=1, timeout=1, fetch_page=invalid_json
        )

    def forbidden(request: PageRequest, _timeout: int) -> tuple[bytes, int, str]:
        return b"{}", 403, request.url

    with pytest.raises(CaptureError, match="HTTP 403"):
        capture_query(
            "zenodo", "fixture", page_size=2, max_pages=1, timeout=1, fetch_page=forbidden
        )


def test_capture_schema_fixture_is_fail_closed() -> None:
    evidence = json.loads(
        (ROOT / "docs" / "track-007-pagination-strategy-2026-08-15.json").read_text()
    )
    assert evidence["schema_version"] == "RBC-LAND-007-PAGES-v0.1.0"
    assert evidence["status"] == "strategy_and_synthetic_fixture_only"
    assert evidence["production_capture_status"] == "not_run"
    assert evidence["claims"]["ecosystem_completeness"] == "prohibited"
    assert evidence["claims"]["captured_page_reproducibility"] == "supported"
